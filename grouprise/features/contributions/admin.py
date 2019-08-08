from django.contrib import admin
from . import models


class ContributionModelAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = self.model.objects_with_internal.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


admin.site.register(models.Contribution, ContributionModelAdmin)
admin.site.register(models.Text)
