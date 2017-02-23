from django_mailbox import signals
from django import dispatch

@dispatch.receiver(signals.message_received)
def process_messages(**args):
    print('GOT ONE')
