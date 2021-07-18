Authentication
==============

.. toctree::
    :maxdepth: 1

    grouprise_as_provider
    external_providers


*grouprise* offers all authentication features provided by
`Django <https://docs.djangoproject.com/en/stable/topics/auth/customizing/>`_
(e.g. internal database, LDAP or others).

Additionally it is possible to use external authentication sources
(e.g. social platforms). This allows users to re-use existing external accounts
instead of memorizing another password for a local account.
Details are described in `External Authentication Providers <./external_providers.html>`_.

*grouprise* can also act as an identity provider.
This allows third party applications to use *grouprise* as an authentication backend.
Users may use their *grouprise* login credentials (or even their active session) for accessing
these third party applications.
Details are described in `Grouprise as an Identity Provider <./grouprise_as_provider.html>`_.

By default *grouprise* manages user accounts independent from external entities (in its database).
