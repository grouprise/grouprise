from . import models


def statistics(request):
    return {
            'article_count': models.Article.objects.permitted(request.user).count,
            'content_count': models.Content.objects.permitted(request.user).count,
            }
