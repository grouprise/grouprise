from core import fragments

fragments.register(
        'group-meta-memberships',
        'memberships/_group_meta.html')

fragments.insert(
        'group-meta-memberships',
        'group-meta',
        before=['group-meta-subscriptions'])
