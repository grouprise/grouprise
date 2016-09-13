from core import fragments

fragments.register(
        'group-meta-subscriptions',
        'subscriptions/_group_meta.html')

fragments.insert(
        'group-meta-subscriptions',
        'group-meta',
        after=['group-meta-memberships'])
