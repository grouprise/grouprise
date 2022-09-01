from grouprise.features.email_notifications.notifications import EmailNotification


class MembershipRequest(EmailNotification):
    subject = "Mitgliedschaft"

    def get_context_data(self, **kwargs):
        kwargs["token"] = self.token
        return super().get_context_data(**kwargs)


class Join(MembershipRequest):
    pass


class MembershipCreated(EmailNotification):
    subject = "Mitgliedschaft"

    @classmethod
    def get_recipients(cls, membership):
        return {gestalt: {} for gestalt in membership.group.members.all()}


class NoMember(EmailNotification):
    subject = "Mitgliedschaft"

    def get_formatted_recipient(self):
        return "<{}>".format(self.recipient)


class Resign(MembershipRequest):
    pass
