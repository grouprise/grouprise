import grouprise.features


class Create(grouprise.features.content.forms.Create):
    def save(self, commit=True):
        super().save(commit)
        if commit:
            self.send_post_create()
        return self.instance
