import core.notifications


class ContentAssociated(core.notifications.Notification):
    generate_reply_tokens = True

    def get_message_ids(self):
        return self.object.container.get_unique_id(), None, []

    def get_recipients(self):
        recipients = set(self.object.container.get_authors())
        if self.object.entity.is_group:
            recipients.update(set(self.object.entity.members.all()))
        else:
            recipients.add(self.object.entity)
        return recipients

    def get_sender(self):
        return self.object.container.versions.last().author

    def get_subject(self):
        group = '[{}] '.format(self.object.entity.slug) if self.object.entity.is_group else ''
        return group + self.object.container.subject

    def get_template_name(self):
        if self.object.container.is_gallery:
            name = 'galleries/associated.txt'
        elif self.object.container.is_file:
            name = 'files/associated.txt'
        elif self.object.container.is_event:
            name = 'events/associated.txt'
        else:
            name = 'articles/associated.txt'
        return name
