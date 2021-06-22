:orphan:

*****************************************
Configuration Options for Django (legacy)
*****************************************

.. caution::
   The following configuration approach is deprecated.
   Please take a look at `grouprise options <options.html>`_ instead.
   See `grouprise v4.0 release notes <../releases/4.0.html#new-configuration-format>`_ for migration hints.

Various details of grouprise can be configured in a Django settings file (see [`extra_django_settings_filenames`](configuration/options.html#extra-django-settings-filenames)).
Any generic `Django setting <https://docs.djangoproject.com/en/stable/ref/settings/>`_ may be specified.
Additionally grouprise-specific settings can be added to the ``GROUPRISE`` dictionary.

Please note, that all settings below perform direct manipulations of the Django settings.
Since `grouprise v4.0 <../releases/4.0.html>`_ it is recommended to use `grouprise's yaml-based configuration <options.html>`_ instead.

Setup Wizard
============

On a freshly deployed grouprise site call ``grouprisectl setup_site``. It will ask you some
basic questions, create initial groups and users and prepare a bunch of useful articles.

Django Options
==============

Error Handling
--------------

When an error occurs, an email is sent to the ``ADMINS``.

``ADMINS``

  See `Django (ADMINS) <https://docs.djangoproject.com/en/stable/ref/settings/#admins>`_ for details.

``SERVER_EMAIL``

  See `Django (SERVER_EMAIL) <https://docs.djangoproject.com/en/stable/ref/settings/#server-email>`_ for details.

Sending E-Mail
--------------

When any part of the application sends an email, the sender defaults to ``DEFAULT_FROM_EMAIL``.

``DEFAULT_FROM_EMAIL``

  See `Django (DEFAULT_FROM_EMAIL) <https://docs.djangoproject.com/en/stable/ref/settings/#default-from-email>`_ for details.


grouprise Options
=================

grouprise uses its own dictionary for configuration options. It must be defined in the
grouprise settings file::

  GROUPRISE = {
      'OPTION': value,
      ...
  }

General grouprise Settings
--------------------------

``CLAIMS``

  A list of claims. A random claim is displayed for each request. The default ist ``[]``.

``ENTITY_SLUG_BLACKLIST``

  A list of reserved slugs for users and groups that cannot be chosen by users. Exclude slugs
  that you want to use as mail addresses or subdomains. You should include ``'stadt'`` which
  is the root namespace used by grouprise URLs. Defaults to::

  ['all', 'grouprise', 'info', 'mail', 'noreply', 'postmaster', 'reply', 'stadt', 'webmaster', 'www']

``SCORE_CONTENT_AGE``

  The ordering of groups and users in certain places is based on their activity.  The
  ``SCORE_CONTENT_AGE`` setting limits, how old content may be in order to be included in the
  calculation of this activity score.  Older content has no impact at all.
  Defaults to ``100`` days.

``UPLOAD_MAX_FILE_SIZE``

  File size in MB to which uploads are restricted. Set the value allowed by the webserver to
  a higher value. Defaults to ``10``.

Special Users and Groups
------------------------

``FEED_IMPORTER_GESTALT_ID``

  ID of the user (gestalt), which is set by the RSS feed importer as the author of imported
  content. Defaults to ``1``.  This user never receives any kind of notifications, thus it should
  not be a real user account used by a human.

``OPERATOR_GROUP_ID``

  ID of the group which is treated as the operator group of the plattform. Defaults to ``1``.

``UNKNOWN_GESTALT_ID``

  ID of the user (gestalt), which is set as the author for content by users, which have been
  deleted. Defaults to ``1``.

Email-related Settings
----------------------

See `mail setup <../mail_setup.html>`_ for an overview of mail setup considerations.

``DEFAULT_DISTINCT_FROM_EMAIL``

  Email address used as ``From`` address for user content notifications. Defaults to
  ``'noreply+{slug}@localhost'``.

``DEFAULT_REPLY_TO_EMAIL``

  Email address written to the ``Reply-To`` header of user content notifications. Defaults to
  ``'reply+{reply_key}@localhost'``.

``COLLECTOR_MAILBOX_ADDRESS``

  All mails are expected to be delivered to this single mail address and processed via the
  *Scripted processing* ("dot-forward") approach described in `mail setup <../mail_setup.html>`_.
  Empty by default.


``POSTMASTER_EMAIL``

  Email address of the postmaster, defaults to ``postmaster@localhost``.

``MAILINGLIST_ENABLED``

  If set to ``True``, an email address is displayed for group members on the group page, which
  can be used like a mailing list.

Branding
--------

Grouprise supports a few branding options that allow you to change the look of the website.

For most logos you should use SVG files. These are vector graphics and always look sharp
on any kind of display. If you provide custom logos make sure to account for browser caching
if you later change the logo files on disk. It’s usually sufficient to add a little query
string to the end of the URL (like `?v=1`).

``BRANDING_THEME_COLOR``

  This is the color that modern browsers (especially on mobile) use to decorate the tab with.
  You can set this to `None` if you want to embed the theme color through other means.

``BRANDING_LOGO_TEXT``

  This logo file is used in the main menu on the top left part of the screen.
  It has a fixed height at around ~44px and should not occupy more than 230px of width.

``BRANDING_LOGO_FAVICON``

  This is used as the applications favicon that you usually see on the left hand side
  of the browser tab right next to the title of the webpage. We recommend that you use a
  PNG file for the favicon as support for SVG favicons is still spotty (as of Aug 2020).
  You can set this to `None` if you want to embed the favicon through other means.

``BRANDING_LOGO_BACKDROP``

  This logo is used on the left hand side of the footer. Generally you should use a type
  of white mask graphic here. See the default grouprise backdrop logo for reference.

``BRANDING_LOGO_SQUARE``

  This logo is used in various places like the login form, menus, help pages and other
  places. As the name states this logo should be a square image. Please use an
  absolute URL if you override this logo as it will be used by external services
  to reference your site.


System / hosting
----------------

``BACKUP_PATH``

  Backups are created automatically during `package upgrades <../deployment/deb.html>`_ in this
  directory.

``HOOK_SCRIPT_PATHS``

  A list of paths to an executable called upon certain events. It is receiving JSON data describing the
  event as the first argument. The following events are supported:

  * event types: ``created``, ``changed``, ``deleted``
  * object types: ``Group``

  Example data looks like this::

    {
      "eventType": "created",
      "objectType": "Group",
      "objectData": {
        "id": 4,
        "slug": ""
      }
    }


Other Options
=============

``ACCOUNT_DEFAULT_HTTP_PROTOCOL``

  Used to generate links sent via email. Defaults to ``'http'``. You probably want to set it
  to ``'https'``.

``HAYSTACK_XAPIAN_LANGUAGE``

  The language used by the `Xapian <https://xapian.org/>`_ indexer database (used for search
  operations).  The full list of supported languages is provided in the
  `Xapian documentation <https://xapian.org/docs/apidoc/html/classXapian_1_1Stem.html>`_.

``HUEY``

  grouprise uses `huey <https://huey.readthedocs.io/en/latest/index.html>`_ for tasks to be
  executed independent from HTTP requests (e.g. sending emails). By default a local
  `redis <https://redis.io/>`_ instance is used. Alternative storage methods can be
  `configured <https://huey.readthedocs.io/en/latest/contrib.html#django>`_, e.g.::

    HUEY = {
        'huey_class': 'huey.SqliteHuey',
        'filename': '/var/lib/grouprise/huey.sqlite',
    }

