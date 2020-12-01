*********************
Configuration Options
*********************

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

  The ordering or groups and users in certain places is based on their activity.  The
  ``SCORE_CONTENT_AGE`` settings limits, how old content may be in order to be included in the
  calculation of this activity score.  Older content has no impact at all.
  Defaults to ``100`` days.

``UPLOAD_MAX_FILE_SIZE``

  File size in MB to which uploads are restricted. Set the value allowed by the webserver to
  a higher value. Defaults to ``0``.

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

``DEFAULT_DISTINCT_FROM_EMAIL``

  Email address used as ``From`` address for user content notifications. Defaults to
  ``'noreply+{slug}@localhost'``.

``DEFAULT_REPLY_TO_EMAIL``

  Email address written to the ``Reply-To`` header of user content notifications. Defaults to
  ``'reply+{reply_key}@localhost'``.

``MAILBOX_DELIVERED_TO_EMAIL``

  When using mailbox delivery, set this to the address of the ``Delivered-To`` header set by
  the mailer for incoming mail. Defaults to ``mailbox@localhost``.

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
