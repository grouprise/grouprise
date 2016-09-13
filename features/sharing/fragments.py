from core import fragments

fragments.register(
        'group-meta-subscriptions-share', 'sharing/_group_meta_share.html')
fragments.register('invite-member', 'sharing/_invite_member.html')
fragments.register('sidebar-share-group', 'sharing/_sidebar_group.html')

fragments.insert(
        'group-meta-subscriptions-share',
        'group-meta-subscriptions')

fragments.insert(
        'invite-member',
        'group-meta-members')

fragments.insert(
        'sidebar-share-group',
        'group-sidebar',
        after=['sidebar-logo', 'sidebar-calendar'],
        before=['sidebar-groups'])
