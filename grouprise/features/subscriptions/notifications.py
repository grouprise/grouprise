from grouprise.core.notifications import Notification


class NoSubscriber(Notification):
    subject = "Abonnement"

    def get_formatted_recipient(self):
        return "<{}>".format(self.recipient)


class Subscriber(Notification):
    subject = "Abonnement"

    def get_context_data(self, **kwargs):
        kwargs["token"] = self.token
        return super().get_context_data(**kwargs)
