from core import fragments

fragments.register('sidebar-groups', 'groups/_sidebar_list.html')

fragments.insert(
        'sidebar-groups',
        'group-sidebar',
        fragments.always,
        after=['sidebar-logo', 'sidebar-calendar', 'sidebar-share-group'])
