from grouprise.features.content.forms import Create as ContentCreateForm


class EventCreateForm(ContentCreateForm):
    """ model form for creating event content

    Sends post_create signal after successful creation.
    """

    def save(self, commit=True):
        instance = super().save(commit)
        if commit:
            self.send_post_create()
        return instance
