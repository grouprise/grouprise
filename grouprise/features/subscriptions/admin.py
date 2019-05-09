from django.contrib import admin

from . import models


class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ['subscriber__user__username']


admin.site.register(models.Subscription, SubscriptionAdmin)
