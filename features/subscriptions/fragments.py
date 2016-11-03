from core import fragments

fragments.register(
        'content-subscription-actions',
        'subscriptions/_content_actions.html')
fragments.register(
        'group-meta-subscriptions',
        'subscriptions/_group_meta.html')

fragments.insert(
        'content-subscription-actions',
        'content-actions',
        after=['content-actions-edit'],
        )
fragments.insert(
        'group-meta-subscriptions',
        'group-meta',
        after=['group-meta-memberships'])
