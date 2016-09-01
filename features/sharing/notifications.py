from core import notifications


class GroupShare(notifications.Notification):
    def get_recipient_str(self):
        return '<{}>'.format(self.recipient_email)

    def get_subject(self):
        return 'Stadtgestalten: {}'.format(str(self.group))


class GroupRecommend(GroupShare):
    template_name = 'sharing/notifications/grouprecommend.txt'


class MemberInvite(GroupShare):
    template_name = 'sharing/notifications/memberinvite.txt'
