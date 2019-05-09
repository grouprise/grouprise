from grouprise.core import notifications


class GroupShare(notifications.Notification):
    def get_formatted_recipient(self):
        return '<{}>'.format(self.recipient)

    def get_subject(self):
        return 'Gruppe {}'.format(str(self.object))


class GroupRecommend(GroupShare):
    pass


class MemberInvite(GroupShare):
    pass
