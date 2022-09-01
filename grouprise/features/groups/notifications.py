from grouprise.features.email_notifications.notifications import EmailNotification


class RecommendNotification(EmailNotification):

    subject = "Empfehlung für Gruppe"

    def get_body(self):
        return self.object

    def get_formatted_recipient(self):
        return "<{}>".format(self.recipient)
