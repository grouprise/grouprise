from core.notifications import Notification


class Member(Notification):
    subject = 'Mitgliedschaft'

    def get_context_data(self, **kwargs):
        kwargs['token'] = self.token
        return super().get_context_data(**kwargs)


class MembershipCreated(Notification):
    subject = 'Mitgliedschaft'


class NoMember(Notification):
    subject = 'Mitgliedschaft'

    def get_formatted_recipient(self):
        return '<{}>'.format(self.recipient)
