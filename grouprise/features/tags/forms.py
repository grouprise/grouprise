from typing import Callable, Iterable, Union

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils.translation import ngettext
from taggit.forms import TagField, TextareaTagWidget

from .settings import TAG_SETTINGS
from .utils import get_featured_tags, get_sorted_featured_tags


class TagGroup(forms.Form):

    group = forms.ModelChoiceField(label="Gruppe", queryset=None)

    def __init__(self, **kwargs):
        group_queryset = kwargs.pop("group_queryset")
        super().__init__(**kwargs)
        self.fields["group"].queryset = group_queryset


TagInputSuggestions = Union[Iterable[str], QuerySet, Callable[[], Iterable[str]]]


class TagInputWidget(TextareaTagWidget):
    template_name = "tags/widgets/taginput.html"

    def __init__(self, attrs=None, *, suggestions: TagInputSuggestions = tuple()):
        default_attrs = {"cols": None, "rows": "2"}
        if attrs:
            default_attrs.update(attrs)
        default_attrs["data-component"] = "taginput"
        super().__init__(default_attrs)
        self.suggestions = suggestions

    def get_context(self, name, value, attrs):
        attrs = attrs or {}
        suggestions = self.suggestions
        if isinstance(suggestions, QuerySet):
            # ensure the queryset is refreshed
            suggestions = suggestions.all()
        elif callable(suggestions):
            suggestions = suggestions()
        suggestions = [str(s) for s in suggestions]
        if suggestions:
            _id = self.attrs["id"]
            list_id = f"{_id}-suggestions"
            attrs["list"] = list_id
        else:
            list_id = None

        ctx = super().get_context(name, value, attrs)
        if suggestions and list_id:
            ctx["suggestions"] = suggestions
            ctx["suggestion_list_id"] = list_id
        return ctx


class TagInputField(TagField):
    def __init__(self, id: str, suggestions: TagInputSuggestions, **kwargs):
        _id = f"taginput-{id}"
        kwargs["max_length"] = None
        kwargs["min_length"] = None
        kwargs["widget"] = TagInputWidget({"id": _id}, suggestions=suggestions)
        super().__init__(**kwargs)


class FeaturedTagInputField(TagInputField):
    def __init__(self, id: str, **kwargs):
        super().__init__(id, self.get_featured_tag_suggestions, **kwargs)

    def clean(self, value):
        tags = super().clean(value)
        if min_tag_count := TAG_SETTINGS.MIN_FEATURED_GROUP_TAG_COUNT:
            tag_count = get_featured_tags().filter(name__in=tags).count()
            if tag_count < min_tag_count:
                raise ValidationError(
                    ngettext(
                        "At least one featured tag needs to be selected.",
                        "At least %(count)d featured tags need to be selected.",
                        min_tag_count,
                    )
                )
        return tags

    @staticmethod
    def get_featured_tag_suggestions():
        return [tag.name for tag in get_sorted_featured_tags()]
