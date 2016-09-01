from core import fragments

fragments.register('sidebar-calendar', 'events/_sidebar.html')

fragments.insert(
        'sidebar-calendar',
        'group-sidebar',
        fragments.always,
        after=['sidebar-logo'],
        before=['sidebar-share', 'sidebar-groups'])
