from django.db import models


class Group(models.QuerySet):
    ATTENDEES_WEIGHT = 1.0
    CONTENT_WEIGHT = 1.0
    MEMBERS_WEIGHT = 1.0
    SIMILARITY_WEIGHT = 3.0

    def scored(self):
        counted = self.annotate(
                num_attendees=models.ExpressionWrapper(
                    models.Count('subscriptions', distinct=True),
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

    def similar(self, group):
        query1 = str(group.members.all().query)
        query2 = group.members.all().query.sql_with_params()[0] % '"entities_group"."id"'
        counted = self.annotate(
                num_same_members=models.expressions.RawSQL(
                    'SELECT COUNT(*) FROM ({} INTERSECT {}) same_members'.format(
                        query1, query2),
                    [],
                    output_field=models.FloatField()),
                )
        if group.members.count() > 0:
            maximum = float(group.members.count())
        else:
            maximum = 1.0
        scored = counted.annotate(
                similarity_score=models.F('num_same_members') / maximum,
                )
        return scored.annotate(score=
                models.F('score') +
                models.F('similarity_score') * Group.SIMILARITY_WEIGHT
                )
