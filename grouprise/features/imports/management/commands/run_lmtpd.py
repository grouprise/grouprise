import asyncio
import email.parser
import email.policy
import functools
import logging
import random
import signal
import smtplib
import sys
import traceback

from aiosmtpd.lmtp import LMTP
from aiosmtplib.errors import SMTPRecipientsRefused, SMTPResponseException
from aiosmtplib.smtp import SMTP
import django
from django.conf import settings

from grouprise.core.notifications import DEFAULT_REPLY_TO_EMAIL
from grouprise.features.imports.signals import (
        ContributionMailProcessor, MailProcessingFailure, ParsedMailMessage)

logger = logging.getLogger(__name__)


# internal error mails are sent to the postmaster
POSTMASTER_ADDRESS = settings.GROUPRISE.get('POSTMASTER_EMAIL', 'postmaster@localhost')


class Command(django.core.management.base.BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('host')
        parser.add_argument('port')

    def handle(self, host=None, port=None, **options):
        def message_writer(text, style=None):
            if style == self.style.ERROR:
                logger.error(text)
            else:
                self.stderr.write(style(text))
        success_writer = functools.partial(message_writer, style=self.style.SUCCESS)
        error_writer = functools.partial(message_writer, style=self.style.ERROR)
        lmtp_daemon = ContributionLMTPD(success_writer, error_writer)
        lmtp_daemon.serve_forever(host, port)


class ContributionLMTPD:
    """ an LMTP daemon for handling incoming mail messages

    The daemon can either be run in foreground (via "serve_forever") or in its own event loop
    (by using the instance as a context).
    """

    def __init__(self, success_writer=None, error_writer=None):
        if success_writer is None:
            self._success_writer = functools.partial(print, file=sys.stdout)
        else:
            self._success_writer = success_writer
        if error_writer is None:
            self._error_writer = functools.partial(logger.error)
        else:
            self._error_writer = error_writer
        processor = ContributionMailProcessor(DEFAULT_REPLY_TO_EMAIL,
                                              settings.DEFAULT_FROM_EMAIL)
        self._handler = ContributionHandler(processor, self._success_writer, self._error_writer)

    def serve_forever(self, host, port):
        """ block execution and run the LMTP daemon until it is stopped via signal or CTRL-C """
        loop = asyncio.get_event_loop()
        server = loop.run_until_complete(
            loop.create_server(functools.partial(LMTP, self._handler), host=host, port=port))
        self._success_writer('Server is waiting for requests: {}:{}'.format(host, port))

        def stop_by_signal():
            self._success_writer('Shutting down due to signalling')
            loop.stop()

        loop.add_signal_handler(signal.SIGTERM, loop.stop)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self._success_writer('Shutting down due to interrupt')
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

    def __enter__(self):
        """ initialize a context with an LMTP daemon running on a random port on localhost

        The context returns an AsyncLMTPClient.

        Example usage:

            with ContributionLMTPD() as lmtp_client:
                failed_recipients = lmtp_client.sendmail(from_address, recipients, data)
        """
        host = 'localhost'
        port = random.randint(16384, 32767)

        loop = asyncio.get_event_loop()
        self._server = loop.run_until_complete(
            loop.create_server(functools.partial(LMTP, self._handler), host=host, port=port))
        self._success_writer('Server is waiting for requests: {}:{}'.format(host, port))

        def stop_by_signal():
            self._success_writer('Shutting down due to signalling')
            self._server.close()

        loop.add_signal_handler(signal.SIGTERM, stop_by_signal)

        return AsyncLMTPClient(loop, host, port)

    def __exit__(self, exc_type, exc_value, traceback):
        assert hasattr(self, '_server')
        self._server.close()
        del self._server


class AsyncLMTPClient:
    """ wrapper around smtplib.SMTP for communicating with an asynchronous LMTP server

    A synchronous interface is exposed, while performing asynchronous operations with the LMTP
    server (which must use the same loop).
    The HELO/EHLO greetings of the SMTP client are replaced with LHLO (for LMTP).
    """

    def __init__(self, loop, host, port):
        self.loop = loop
        self.smtp_client = SMTP(hostname=host, port=port)

        # monkey-patch the greeting command from HELO/EHLO to LHLO (LMTP-only)
        orig_execute_command = self.smtp_client.execute_command

        async def execute_command(command, *args, **kwargs):
            if command in (b'HELO', b'EHLO'):
                command = b'LHLO'
            return await orig_execute_command(command, *args, **kwargs)

        self.smtp_client.execute_command = execute_command

    async def sendmail(self, from_address, recipients, data, hide_error_messages=False):
        """ Submit a raw mail message (as bytes) to an LMTP server

        Returns a list of recipients with failed delivery.
        """
        recipients = tuple(recipients)
        await self.smtp_client.connect()
        try:
            failures, err_msg = await self.smtp_client.sendmail(from_address, recipients, data)
            failed_recipients = tuple(failures.keys())
        except SMTPRecipientsRefused as exc:
            if not hide_error_messages:
                logger.error('Failed to submit message: {}'.format(exc))
            # all deliveries failed
            failed_recipients = recipients
        await self.smtp_client.quit()
        return failed_recipients

    async def verify_recipient(self, recipient):
        """ send the VRFY command to the LMTP server and evaluate the response code """
        await self.smtp_client.connect()
        try:
            await self.smtp_client.vrfy(recipient)
            result = True
        except SMTPResponseException:
            result = False
        await self.smtp_client.quit()
        return result

    def run_sync(self, command):
        """ wrapper to be used for synchronously executing the async methods of this object """
        return self.loop.run_until_complete(command)


class ContributionHandler:

    def __init__(self, contribution_processor, success_writer, error_writer):
        self._contribution_processor = contribution_processor
        self._success_writer = success_writer
        self._error_writer = error_writer

    def _get_recipient_check_error_message(self, recipient):
        """ check if the recipient could be valid

        No permission or other sanity checks are conducted.
        """
        try:
            local_part, domain = recipient.split('@')
        except ValueError:
            return 'Invalid address format'
        if not self._contribution_processor.is_mail_domain(domain):
            return 'Unexpected mail domain'
        elif self._contribution_processor.is_valid_groupname(local_part):
            return None
        elif self._contribution_processor.parse_authentication_token_text(recipient):
            # we do not check the validity of the token here
            return None
        else:
            return 'Unknown target mail address'

    async def handle_VRFY(self, server, session, envelope, recipient):
        error_message = self._get_recipient_check_error_message(recipient)
        if error_message is None:
            return '250 <{}>'.format(recipient)
        else:
            return '550 {}'.format(error_message)

    async def handle_RCPT(self, server, session, envelope, recipient, rcpt_options):
        # TODO: we should test here, if the sender is allowed to reach this recipient. LMTP allows
        # partial rejection - this would be good to use (e.g. for CCing multiple groups).
        error_message = self._get_recipient_check_error_message(recipient)
        if error_message is None:
            envelope.rcpt_tos.append(recipient)
            return '250 OK'
        else:
            return '550 {}'.format(error_message)

    async def handle_DATA(self, server, session, envelope):
        parser = email.parser.BytesParser(policy=email.policy.SMTP)
        message = parser.parsebytes(envelope.content)
        try:
            parsed_message = ParsedMailMessage.from_email_object(message, envelope.mail_from)
        except Exception:
            err_msg = ''.join(traceback.format_exception(*sys.exc_info()))
            self._error_writer('Failed to parse Message:\n{}'.format(err_msg))
            django.core.mail.send_mail(
                'LMTP Handling Error', err_msg, from_email=POSTMASTER_ADDRESS,
                recipient_list=[POSTMASTER_ADDRESS], fail_silently=True)
            return '500 Failed to parse incoming message'
        success_count = 0
        error_messages = []
        internal_problems = []
        for recipient in envelope.rcpt_tos:
            try:
                self._contribution_processor.process_message_for_recipient(parsed_message,
                                                                           recipient)
                success_count += 1
                self._success_writer('Processed recipient {:d}/{:d} ({}) successfully'
                                     .format(success_count, len(envelope.rcpt_tos), recipient))
            except MailProcessingFailure as exc:
                error_messages.append((recipient, str(exc)))
                self._error_writer('Failed to process recipient <{}>: {}'.format(recipient, exc))
            except Exception as exc:
                # unknown internal problems end up here
                internal_problems.append((recipient,
                                          ''.join(traceback.format_exception(*sys.exc_info()))))
                self._error_writer('Internal error while processing recipient <{}>: {}\n{}'
                                   .format(recipient, exc, internal_problems[-1][1]))
        if error_messages:
            # The mail was not acceptable for us (e.g. due to permissions). We send a human
            # readable separate response and tell the mail server, that the mail was handled.
            if len(error_messages) > 1:
                # format multiple errors into one string
                error_response_text = '\n\n'.join('= {} =\n\n{}'.format(recipient, error_message)
                                                  for recipient, error_message in error_messages)
            else:
                error_response_text = error_messages[0][1]
        else:
            error_response_text = None
        if internal_problems:
            # At least one recipient failed mysteriously.
            problems_text = '\n\n'.join('= {} =\n{}\n'.format(recipient, exc)
                                        for recipient, exc in internal_problems)
            # inform developers
            self._contribution_processor.send_error_mail_response(
                parsed_message, problems_text, recipient=POSTMASTER_ADDRESS, fail_silently=True)
            if success_count > 0:
                # Never reject a message that was at least partly processed. Otherwise a
                # contribution could be published multiple times - which would be quite annoying
                # for the subscribers.
                return '250 Message partially accepted for delivery (ignoring internal errors)'
            else:
                # The mail server should ask us again later. Hopefully the problem is fixed until
                # then.  An error message mail is not yet returned to the sender.
                return '451 Requested action aborted: error in processing'
        elif error_response_text is not None:
            # Try to send an helpful error message mail back to sender.
            # Only return a bounce, if we failed to submit this error message mail.
            try:
                self._contribution_processor.send_error_mail_response(parsed_message,
                                                                      error_response_text,
                                                                      recipient=envelope.mail_from)
                return ('250 The incoming message was at least partly not accepted for '
                        'publication. Instead a separate error mails was returned.')
            except smtplib.SMTPException:
                # emergency bounce in case of mail delivery problems
                return '550 Rejected incoming mail due to errors'
        elif success_count > 0:
            return '250 Message accepted for delivery'
        else:
            self._error_writer('Unexpectedly encountered an empty list of recipients.')
