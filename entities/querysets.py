from django.db import models


class Group(models.QuerySet):
    ATTENDEES_WEIGHT = 1.0
    CONTENT_WEIGHT = 1.0
    MEMBERS_WEIGHT = 1.0

    def scored(self):
        counted = self.annotate(
                num_attendees=models.ExpressionWrapper(
                    models.Count('attendees', distinct=True),
                    output_field=models.FloatField()),
                num_content=models.ExpressionWrapper(
                    models.Count('content', distinct=True),
                    output_field=models.FloatField()),
                num_members=models.ExpressionWrapper(
                    models.Count('members', distinct=True),
                    output_field=models.FloatField()),
                )
        maxima = counted.aggregate(
                attendees=models.Max('num_attendees'),
                content=models.Max('num_content'),
                members=models.Max('num_members'),
                )
        for m in maxima:
            maxima[m] = 1.0 if maxima[m] == 0.0 else maxima[m]
        scored = counted.annotate(
                attendees_score=models.F('num_attendees') / maxima['attendees'],
                content_score=models.F('num_content') / maxima['content'],
                members_score=models.F('num_members') / maxima['members'],
                )
        return scored.annotate(score=
                models.F('attendees_score') * Group.ATTENDEES_WEIGHT +
                models.F('content_score') * Group.CONTENT_WEIGHT +
                models.F('members_score') * Group.MEMBERS_WEIGHT
                )
