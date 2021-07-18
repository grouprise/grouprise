# Django-Admin

The web-based django-admin interface allows the direct manipulation of database content.

This approach can be a bit cumbersome, since you are working on a database-level.
But it allows to manipulate *everything* and relies on an approachable web interface.


## Register an administrative account

You can create a privileged account on the *grouprise* host:
```shell
grouprisectl createsuperuser
```

This account can be used for accessing the django-admin web interface.
But you should never use it for browsing the normal *grouprise* user interface, since many interface widgets will look weird and confusing (due to the lack of permission handling).


## Access the django-admin web interface

The django-admin web interface is accessible below `/stadt/admin/` in your *grouprise* website.

It is advisable to use a sandbox environment (e.g. a *private* or *incognito* browser window), in order to to not confuse it with your regular *grouprise* user account.
