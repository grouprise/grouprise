from core import notifications


class MembershipCreated(notifications.Notification):
    subject = 'Stadtgestalten: In Gruppe aufgenommen'
    template_name = 'memberships/notifications/membershipcreated.txt'

    def get_recipient(self):
        return self.membership.member
