from core import fragments

fragments.register('sidebar-calendar', 'events/_group_sidebar.html')

fragments.insert(
        'sidebar-calendar',
        'group-sidebar',
        fragments.always,
        after=['sidebar-logo'],
        before=['sidebar-share-group', 'sidebar-groups'])
