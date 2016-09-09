from core import notifications


class MembershipCreated(notifications.Notification):
    subject = 'Stadtgestalten: In Gruppe aufgenommen'

    def get_recipients(self):
        return [self.kwargs['membership'].member]
