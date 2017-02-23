from core import notifications


class GroupShare(notifications.Notification):
    def get_formatted_recipients(self):
        return [('<{}>'.format(self.kwargs['recipient_email']), {'with_name': False})]

    def get_subject(self):
        return 'Stadtgestalten: {}'.format(str(self.kwargs['group']))


class GroupRecommend(GroupShare):
    pass


class MemberInvite(GroupShare):
    pass
