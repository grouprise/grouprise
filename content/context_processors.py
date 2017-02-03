from . import models


def events(request):
    return {
            'all_events': models.Event.objects.permitted(request.user),
            'all_calendar_events': models.Event.objects.permitted(request.user).around(),
            'all_upcoming_events': models.Event.objects.permitted(request.user).upcoming(5),
            }


def statistics(request):
    return {
            'article_count': models.Article.objects.permitted(request.user).count,
            'content_count': models.Content.objects.permitted(request.user).count,
            }
