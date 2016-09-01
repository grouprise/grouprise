from core import fragments

fragments.register('sidebar-share-group', 'sharing/_sidebar_group.html')

fragments.insert(
        'sidebar-share-group',
        'group-sidebar',
        fragments.always,
        after=['sidebar-logo', 'sidebar-calendar'],
        before=['sidebar-groups'])
