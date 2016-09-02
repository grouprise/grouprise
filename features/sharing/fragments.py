from core import fragments

fragments.register('invite-member', 'sharing/_invite_member.html')
fragments.register('sidebar-share-group', 'sharing/_sidebar_group.html')

fragments.insert(
        'invite-member',
        'group-meta-members',
        fragments.always)

fragments.insert(
        'sidebar-share-group',
        'group-sidebar',
        fragments.always,
        after=['sidebar-logo', 'sidebar-calendar'],
        before=['sidebar-groups'])
