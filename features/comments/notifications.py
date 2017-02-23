from core import notifications


class Commented(notifications.Notification):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.comment = kwargs['comment']

    def get_message_ids(self):
        my_id = self.comment.get_unique_id()
        last_comment = self.comment.content.comments.exclude(id=self.comment.id).last()
        thread_id = self.comment.content.get_unique_id()
        if last_comment:
            # there was a previous comment
            parent_id = last_comment.get_unique_id()
            ref_ids = [thread_id]
        else:
            # we are the first comment
            parent_id = thread_id
            ref_ids = []
        return my_id, parent_id, ref_ids

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
