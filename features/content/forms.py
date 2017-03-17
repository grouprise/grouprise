from core import forms
from features.contributions import forms as contributions


class Comment(contributions.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append(forms.Submit('Kommentieren'))
