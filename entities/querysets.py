from django.db import models


class Group(models.QuerySet):
    CONTENT_WEIGHT = 1.0
    SIMILARITY_WEIGHT = 3.0

    def scored(self):
        counted = self.annotate(num_content=models.ExpressionWrapper(
            models.Count('content', distinct=True), output_field=models.FloatField()))
        maxima = counted.aggregate(content=models.Max('num_content'))
        for m in maxima:
            maxima[m] = 1.0 if maxima[m] == 0.0 else maxima[m]
        scored = counted.annotate(content_score=models.F('num_content') / maxima['content'])
        return scored.annotate(old_score=models.F('content_score') * Group.CONTENT_WEIGHT)

    def similar(self, group):
        return self
