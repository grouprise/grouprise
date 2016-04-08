'''
https://github.com/perenecabuto/django-sendmail-backend
https://djangosnippets.org/snippets/1864/
'''
from django.core.mail.backends import base
import subprocess


class EmailBackend(base.BaseEmailBackend):
    def send_messages(self, email_messages):
        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1
        return num_sent

    def _send(self, email_message):
        try:
            sendmail = subprocess.Popen(
                    ['/usr/sbin/sendmail'] + email_message.recipients(), 
                    stdin=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
            sendmail.stdin.write(email_message.message().as_bytes())
            (stdout, stderr) = sendmail.communicate()
        except:
            if not self.fail_silently:
                raise
            return False
        if sendmail and sendmail.returncode:
            if not self.fail_silently:
                raise Exception('sendmail failed: {}'.format(
                    stderr if stderr else stdout))
            return False
        return True
