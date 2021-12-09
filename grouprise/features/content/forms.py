import datetime
import enum

import django.db.transaction
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.safestring import mark_safe

import grouprise.core.forms
from grouprise.core.signals import post_create
from grouprise.core.utils import slugify
from grouprise.features.associations import models as associations
from grouprise.features.groups import models as groups
from grouprise.features.images.models import Image

from . import models


class RepetitionPeriod(enum.Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    WEEKDAY_IN_MONTH = "weekday_in_month"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    @classmethod
    def _get_date_by_month_offset(
        self, base_date, month_offset_count, day_override=None
    ):
        new_day = base_date.day if day_override is None else day_override
        new_month_plain = base_date.month + month_offset_count
        new_month = (new_month_plain - 1) % 12 + 1
        new_year = base_date.year + ((new_month_plain - 1) // 12)
        try:
            return base_date.replace(day=new_day, month=new_month, year=new_year)
        except ValueError:
            return None

    def get_repetition_datetimes(self, base_date, count):
        """retrieve a number of dates separated by a given period

        Only repetitions (not the very first event date - see *base_date*) are returned.

        Invalid dates are silently discarded. This reduces the number of returned items. For
        example when retrieving three monthly values (count=3) starting with the 30th of December,
        then the result is the 30th of January and the 30th of March. The 30th of February is an
        invalid date - thus it is silently discarded.
        This reduces the number of generated items from three to two.
        """
        offsets = range(1, count + 1)
        if self is self.ONCE:
            return
        elif self is self.DAILY:
            yield from (base_date + datetime.timedelta(days=index) for index in offsets)
        elif self is self.WEEKLY:
            yield from (
                base_date + datetime.timedelta(weeks=index) for index in offsets
            )
        elif self is self.MONTHLY:
            for index in offsets:
                possible_date = self._get_date_by_month_offset(base_date, index)
                if possible_date is not None:
                    yield possible_date
        elif self is self.YEARLY:
            for index in offsets:
                possible_date = self._get_date_by_month_offset(base_date, 12 * index)
                if possible_date is not None:
                    yield possible_date
        elif self is self.WEEKDAY_IN_MONTH:
            wanted_weekday = base_date.weekday()
            week_in_month = (base_date.day - 1) // 7
            for index in offsets:
                # find the first day in the desired week
                first_possible_day = self._get_date_by_month_offset(
                    base_date, index, day_override=week_in_month * 7 + 1
                )
                if first_possible_day is not None:
                    # find the fitting day of week within one week
                    for day_offset in range(7):
                        candidate = first_possible_day + datetime.timedelta(
                            days=day_offset
                        )
                        if (candidate.month == first_possible_day.month) and (
                            candidate.weekday() == wanted_weekday
                        ):
                            yield candidate
                            break


class Create(forms.ModelForm):
    container_class = models.Content

    class Meta:
        model = associations.Association
        fields = ("pinned", "public")

    group = forms.ModelChoiceField(
        label="Veröffentlichen als",
        queryset=groups.Group.objects.none(),
        required=False,
        widget=grouprise.core.forms.GroupSelect,
    )
    as_gestalt = forms.BooleanField(
        label="Veröffentlichung unter persönlichem Profil",
        required=False,
        help_text=mark_safe(
            "Der Beitrag wird nicht von einer Gruppe, sondern von dir als <em>Gestalt</em> "
            "veröffentlicht. Einige Funktionen wie beispielsweise <em>Abonnieren</em> stehen "
            "nicht zur Verfügung."
        ),
    )
    text = forms.CharField(label="Text", widget=grouprise.core.forms.EditorTextarea)
    title = forms.CharField(label="Titel")
    image = forms.ModelChoiceField(
        label="Beitragsbild",
        queryset=None,
        required=False,
        widget=forms.Select(attrs={"data-component": "image-picker"}),
        help_text="Das Beitragsbild wird beispielsweise auf Übersichtsseiten in der "
        "Vorschau des Beitrags angezeigt.",
    )

    place = forms.CharField(label="Veranstaltungsort / Anschrift", max_length=255)
    time = forms.DateTimeField(label="Beginn")
    until_time = forms.DateTimeField(label="Ende", required=False)
    all_day = forms.BooleanField(
        label="ganztägig",
        help_text="Die Veranstaltung dauert den ganzen Tag.",
        required=False,
    )
    time_repetitions_period = forms.ChoiceField(
        label="Häufigkeit der Veranstaltung",
        help_text="Ereignisse können wiederholt stattfinden.",
        choices=(
            (RepetitionPeriod.ONCE.value, "einmalig"),
            (RepetitionPeriod.DAILY.value, "täglich"),
            (RepetitionPeriod.WEEKLY.value, "wöchentlich"),
            (RepetitionPeriod.WEEKDAY_IN_MONTH.value, "Wochentag im Monat"),
            (RepetitionPeriod.MONTHLY.value, "monatlich"),
            (RepetitionPeriod.YEARLY.value, "jährlich"),
        ),
        required=False,
    )
    time_repetitions_count = forms.DecimalField(
        label="Anzahl",
        help_text="Anzahl der Ereignisse dieser Art.",
        min_value=1,
        max_value=100,
        required=False,
    )

    def __init__(self, **kwargs):
        self.author = kwargs.pop("author")
        with_time = kwargs.pop("with_time")
        super().__init__(**kwargs)
        self.fields["image"].queryset = self.author.images
        if self.instance.entity.is_group:
            del self.fields["group"]
            del self.fields["as_gestalt"]
        else:
            self.fields["group"].queryset = groups.Group.objects.filter(
                memberships__member=self.author
            )
        if not with_time:
            del self.fields["place"]
            del self.fields["time"]
            del self.fields["until_time"]
            del self.fields["all_day"]
            del self.fields["time_repetitions_period"]
            del self.fields["time_repetitions_count"]
        else:
            del self.fields["image"]

    def clean(self):
        cleaned_data = super().clean()
        if (
            not self.instance.entity.is_group
            and not cleaned_data["group"]
            and not cleaned_data["as_gestalt"]
        ):
            self.add_error("group", "Bitte eine Gruppe auswählen")
            self.add_error(
                "as_gestalt",
                "Falls keine Gruppe gewählt wird, bitte diese Option wählen",
            )
            raise ValidationError(
                "Entweder eine Gruppe oder 'Veröffentlichung unter persönlichem Profil' muss "
                "ausgewählt sein.",
                code="invalid",
            )

    @classmethod
    def _create_time_based_repetitions(
        cls,
        times,
        container_class,
        model,
        entity_id,
        entity_type,
        title,
        text,
        author,
        image,
        place,
        duration,
        all_day,
        commit,
    ):
        """create a number of instances of "model" for a given set of timestamps

        All new instances share the same title, text and other properties (except for the time).

        This implementation should be kept in sync with the method "save".
        """
        for time in times:
            new_instance = model()
            new_instance.entity_id = entity_id
            new_instance.entity_type = entity_type
            new_instance.slug = grouprise.core.models.get_unique_slug(
                associations.Association,
                {
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "slug": slugify(title),
                },
            )
            container = container_class.objects.create(
                title=title,
                image=image,
                place=place,
                time=time,
                until_time=(time + duration),
                all_day=all_day,
            )
            if not hasattr(container, "content_ptr"):
                new_instance.container = container
            else:
                new_instance.container = container.content_ptr
            new_instance.container.versions.create(author=author, text=text)
            if commit:
                new_instance.save()
                # TODO: send notifications

    def save(self, commit=True):
        with django.db.transaction.atomic():
            if not self.instance.entity.is_group and self.cleaned_data["group"]:
                self.instance.entity = self.cleaned_data["group"]
            # keep the following lines in sync with the method "_create_time_based_repetitions"
            self.instance.slug = grouprise.core.models.get_unique_slug(
                associations.Association,
                {
                    "entity_id": self.instance.entity_id,
                    "entity_type": self.instance.entity_type,
                    "slug": slugify(self.cleaned_data["title"]),
                },
            )
            container = self.container_class.objects.create(
                title=self.cleaned_data["title"],
                image=self.cleaned_data.get("image"),
                place=self.cleaned_data.get("place", ""),
                time=self.cleaned_data.get("time"),
                until_time=self.cleaned_data.get("until_time"),
                all_day=self.cleaned_data.get("all_day", False),
            )
            if not hasattr(container, "content_ptr"):
                self.instance.container = container
            else:
                self.instance.container = container.content_ptr
            self.instance.container.versions.create(
                author=self.author, text=self.cleaned_data["text"]
            )
            self.save_content_relations(commit)
            # create the item (for repetitions: only the first item)
            result = super().save(commit)
            # handle repetitions (only useful for events)
            repetitions_count_decimal = self.cleaned_data.get("time_repetitions_count")
            if repetitions_count_decimal is None:
                repetitions_count = 0
            else:
                repetitions_count = int(repetitions_count_decimal)
            if repetitions_count > 0:
                period_name = self.cleaned_data.get("time_repetitions_period")
                period = RepetitionPeriod(period_name)
                first_time = self.cleaned_data.get("time")
                start_times = period.get_repetition_datetimes(
                    first_time, repetitions_count
                )
                self._create_time_based_repetitions(
                    start_times,
                    self.container_class,
                    self._meta.model,
                    self.instance.entity_id,
                    self.instance.entity_type,
                    self.cleaned_data["title"],
                    self.cleaned_data["text"],
                    self.author,
                    self.cleaned_data.get("image"),
                    self.cleaned_data.get("place", ""),
                    self.cleaned_data.get("until_time") - first_time,
                    self.cleaned_data.get("all_day", False),
                    commit,
                )
            return result

    def save_content_relations(self, commit):
        pass

    def send_post_create(self, instance=None):
        post_create.send(
            sender=self.__class__,
            instance=instance if instance else self.instance.container,
        )


class Update(forms.ModelForm):
    class Meta:
        model = associations.Association
        fields = ("pinned", "public", "slug")

    title = forms.CharField(label="Titel")
    text = forms.CharField(label="Text", widget=grouprise.core.forms.EditorTextarea())
    image = forms.ModelChoiceField(
        label="Beitragsbild",
        queryset=None,
        required=False,
        widget=forms.Select(attrs={"data-component": "image-picker"}),
        help_text="Das Beitragsbild wird beispielsweise auf Übersichtsseiten in der "
        "Vorschau des Beitrags angezeigt.",
    )

    place = forms.CharField(label="Veranstaltungsort / Anschrift", max_length=255)
    time = forms.DateTimeField(label="Beginn")
    until_time = forms.DateTimeField(label="Ende", required=False)
    all_day = forms.BooleanField(
        label="ganztägig",
        help_text="Die Veranstaltung dauert den ganzen Tag.",
        required=False,
    )

    def __init__(self, **kwargs):
        self.author = kwargs.pop("author")
        super().__init__(**kwargs)
        q = Q(creator=self.author)
        if self.initial["image"]:
            q |= Q(pk=self.initial["image"].pk)
        self.fields["image"].queryset = Image.objects.filter(q)
        if not self.instance.entity.is_group:
            del self.fields["pinned"]
        if not self.initial["time"]:
            del self.fields["place"]
            del self.fields["time"]
            del self.fields["until_time"]
            del self.fields["all_day"]
        else:
            del self.fields["image"]

    def clean_slug(self):
        q = associations.Association.objects.filter(
            entity_type=self.instance.entity_type,
            entity_id=self.instance.entity_id,
            slug=self.cleaned_data["slug"],
        )
        if q.exists() and q.get() != self.instance:
            raise forms.ValidationError(
                "Der Kurzname ist bereits vergeben.", code="unique"
            )
        return self.cleaned_data["slug"]

    def save(self, commit=True):
        association = super().save(commit)
        association.container.title = self.cleaned_data["title"]
        association.container.image = self.cleaned_data.get("image")
        if self.initial["time"]:
            association.container.place = self.cleaned_data["place"]
            association.container.time = self.cleaned_data["time"]
            association.container.until_time = self.cleaned_data["until_time"]
            association.container.all_day = self.cleaned_data["all_day"]
        association.container.save()
        association.container.versions.create(
            author=self.author, text=self.cleaned_data["text"]
        )
        self.save_content_relations(commit)
        return association

    def save_content_relations(self, commit):
        pass
