import email
import email.utils
import logging
import os
import re
import sys

from django.core.management.base import BaseCommand, CommandError

from grouprise.core.settings import CORE_SETTINGS
from grouprise.features.imports.mails import (
    ContributionMailProcessor,
    MailProcessingFailure,
    ParsedMailMessage,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

"""
The DTLINE environment variable is set, if the caller uses the "dotforward" mechanism (popularized
by sendmail, implement by many other mailers).
The content of the line could be:
    Delivered-To: Alice <foo@example.org>
"""
DTLINE_REGEX = re.compile(r"^Delivered-To:\s*(.+)$", flags=re.IGNORECASE)
EXITCODE_TEMPORARY_FAILURE = 1
EXITCODE_PERMANENT_FAILURE = 70
EXITCODE_DELIVERY_SUCCESS = 99


def get_normalized_address(address):
    return email.utils.parseaddr(address)[1].lower()


class Command(BaseCommand):
    help = "Receive incoming mail via stdin"

    def handle(self, mailbox_name=None, *args, **options):
        """Process an incoming message (expected via STDIN)

        The destination address is supposed to be specified in the DTLINE environment setting.
        Alternatively the header "Delivered-To" or "To" is used.
        Exitcode 70 indicates a permanent delivery failure (rejection).
        Exitcode 99 indicates final success of delivery.
        Any other exitcode indicates a temporary delivery failure.  In this case our caller is
        supposed to attempt another delivery later.
        """
        message = email.message_from_bytes(sys.stdin.buffer.read())
        try:
            destination_address = self.get_destination_addresses(message)
        except ValueError as exc:
            # report a permanent delivery failure
            raise CommandError(exc, returncode=EXITCODE_PERMANENT_FAILURE) from exc
        destination_address = get_normalized_address(destination_address)
        try:
            parsed_message = ParsedMailMessage.from_email_object(message)
        except MailProcessingFailure as exc:
            raise CommandError(
                f"Mail from {message['from']} could not be parsed: {exc}",
                returncode=EXITCODE_PERMANENT_FAILURE,
            ) from exc
        processor = ContributionMailProcessor()
        try:
            processor.process_message_for_recipient(parsed_message, destination_address)
        except MailProcessingFailure as exc:
            processor.send_error_mail_response(
                parsed_message, str(exc), fail_silently=True
            )
            # report a permanent delivery failure
            raise CommandError(
                f"Mail from {message['from']} was rejected",
                returncode=EXITCODE_PERMANENT_FAILURE,
            ) from exc
        else:
            logger.info("Message received from %s", message["from"])
            # report exitcode for successful delivery (as specified for the "dotforward" mechanism)
            sys.exit(EXITCODE_DELIVERY_SUCCESS)

    def get_destination_addresses(self, message):
        dtline_env = os.getenv("DTLINE")
        if dtline_env:
            line_match = DTLINE_REGEX.search(dtline_env)
            if not line_match:
                raise ValueError(
                    "Failed to parse content of DTLINE environment variable ({})".format(
                        dtline_env
                    )
                )
            delivered_to_address = get_normalized_address(line_match.groups()[0])
            if CORE_SETTINGS.COLLECTOR_MAILBOX_ADDRESS:
                if (
                    get_normalized_address(CORE_SETTINGS.COLLECTOR_MAILBOX_ADDRESS)
                    == delivered_to_address
                ):
                    # The message was delivered to the mailbox configured for collecting all
                    # incoming mails.
                    # We need to guess the target address by parsing the "To" header.
                    destination_headers = ("To",)
                else:
                    raise ValueError(
                        "Rejecting the mail, since its envelope address ({}) does not match the "
                        "expected mailbox address (COLLECTOR_MAILBOX_ADDRESS='{}').".format(
                            delivered_to_address,
                            CORE_SETTINGS.COLLECTOR_MAILBOX_ADDRESS,
                        )
                    )
            else:
                # No inbox address was specified - thus we expect a delivery to the real inbox of
                # this group.
                return delivered_to_address
        else:
            # no DTLINE environment setting was found - fall back to a wild guess
            destination_headers = ("Delivered-To", "To")
        # We need to guess, since no formal delivery method is defined.
        for key in destination_headers:
            if key in message.keys():
                return message[key]
        else:
            raise ValueError(
                "Failed to determine destination address (DTLINE, Delivered-To, To)"
            )
