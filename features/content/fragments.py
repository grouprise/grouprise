from core import fragments

fragments.register(
        'content-actions-edit',
        'content/_content_actions.html')

fragments.insert(
        'content-actions-edit',
        'content-actions',
        before=['content-subscription-actions'],
        )
