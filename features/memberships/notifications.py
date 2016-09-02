from core import notifications


class MembershipCreated(notifications.Notification):
    subject = 'Stadtgestalten: In Gruppe aufgenommen'

    def get_recipient(self):
        return self.membership.member
