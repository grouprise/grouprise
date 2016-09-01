from core import notifications


class GroupRecommend(notifications.Notification):
    template_name = 'sharing/notifications/grouprecommend.txt'

    def get_recipient_str(self):
        return '<{}>'.format(self.recipient_email)

    def get_subject(self):
        return 'Stadtgestalten: {}'.format(str(self.group))
