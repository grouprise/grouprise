from core import notifications


class GroupShare(notifications.Notification):
    def get_recipient_str(self):
        return '<{}>'.format(self.kwargs['recipient_email'])

    def get_subject(self):
        return 'Stadtgestalten: {}'.format(str(self.kwargs['group']))


class GroupRecommend(GroupShare):
    pass


class MemberInvite(GroupShare):
    pass
