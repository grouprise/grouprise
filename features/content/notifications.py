import core.notifications


class ContentAssociated(core.notifications.Notification):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.association = kwargs['association']

    def get_message_ids(self):
        pass

    def get_recipients(self):
        pass

    def get_sender(self):
        return self.association.container.versions.last().author

    def get_subject(self):
        pass

    def get_template_name(self):
        if self.association.container.is_gallery:
            name = 'galleries/associated.txt'
        elif self.association.container.is_event:
            name = 'events/associated.txt'
        else:
            name = 'articles/associated.txt'
        return name
