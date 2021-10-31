from grouprise.core.notifications import Notification


class RecommendNotification(Notification):

    subject = "Empfehlung für Gruppe"

    def get_body(self):
        return self.object

    def get_formatted_recipient(self):
        return "<{}>".format(self.recipient)
