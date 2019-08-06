from grouprise.core.notifications import Notification


class MembershipRequest(Notification):
    subject = 'Mitgliedschaft'

    def get_context_data(self, **kwargs):
        kwargs['token'] = self.token
        return super().get_context_data(**kwargs)


class Join(MembershipRequest):
    pass


class MembershipCreated(Notification):
    subject = 'Mitgliedschaft'

    @classmethod
    def get_recipients(cls, membership):
        return {gestalt: {} for gestalt in membership.group.members.all()}


class NoMember(Notification):
    subject = 'Mitgliedschaft'

    def get_formatted_recipient(self):
        return '<{}>'.format(self.recipient)


class Resign(MembershipRequest):
    pass
