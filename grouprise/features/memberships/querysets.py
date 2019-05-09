from django.db import models
from django.db.models import Case, When, Value, IntegerField, Sum
from django.utils.timezone import now, timedelta


class MembershipQuerySet(models.QuerySet):
    def order_by_gestalt_activity(self, gestalt):
        a_week_ago = now() - timedelta(days=7)
        a_month_ago = now() - timedelta(days=30)
        three_months_ago = now() - timedelta(days=90)
        six_months_ago = now() - timedelta(days=180)

        content_score = Case(*[
            When(
                group__associations__content__versions__author=gestalt,
                group__associations__content__versions__time_created__gte=time,
                then=Value(modifier)
            ) for time, modifier in (
                (a_week_ago, 48),
                (a_month_ago, 32),
                (three_months_ago, 16),
                (six_months_ago, 8)
            )], default=1, output_field=IntegerField())

        content_contrib_score = Case(*[
            When(
                group__associations__content__contributions__author=gestalt,
                group__associations__content__contributions__time_created__gte=time,
                then=Value(modifier)
            ) for time, modifier in (
                (a_week_ago, 12),
                (a_month_ago, 8),
                (three_months_ago, 4),
                (six_months_ago, 2)
            )], default=0, output_field=IntegerField())

        conversation_contrib_score = Case(*[
            When(
                group__associations__conversation__contributions__author=gestalt,
                group__associations__conversation__contributions__time_created__gte=time,
                then=Value(modifier)
            ) for time, modifier in (
                (a_week_ago, 12),
                (a_month_ago, 8),
                (three_months_ago, 4),
                (six_months_ago, 2)
            )], default=0, output_field=IntegerField())

        return self \
            .annotate(activity=Sum(
                content_score
                + content_contrib_score
                + conversation_contrib_score,
                output_field=IntegerField())) \
            .order_by('-activity')
