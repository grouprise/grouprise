from grouprise.features.email_notifications.notifications import EmailNotification


class NoSubscriber(EmailNotification):
    subject = "Abonnement"

    def get_formatted_recipient(self):
        return "<{}>".format(self.recipient)


class Subscriber(EmailNotification):
    subject = "Abonnement"

    def get_context_data(self, **kwargs):
        kwargs["token"] = self.token
        return super().get_context_data(**kwargs)
