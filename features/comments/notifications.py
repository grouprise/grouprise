from core import notifications


class Commented(notifications.Notification):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.comment = kwargs['comment']

    def get_message_id(self):
        return self.comment.get_unique_id()

    def get_recipients(self):
        recipients = {self.comment.content.author}
        recipients.update(set(self.comment.content.comment_authors.all()))
        recipients.discard(self.comment.author)
        return recipients

    def get_sender(self):
        return self.comment.author

    def get_subject(self):
        slugs = self.comment.content.groups.values_list('slug', flat=True)
        groups = '[{}] '.format(','.join(slugs)) if slugs else ''
        return 'Re: ' + groups + self.comment.content.title
