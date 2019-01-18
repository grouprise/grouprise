*********************
Configuration Options
*********************

Django Options
==============

Error Handling
--------------

When an error occurs, an email is sent to the ``ADMINS``.

``ADMINS``
  see https://docs.djangoproject.com/en/stable/ref/settings/#admins

``SERVER_EMAIL``
  see https://docs.djangoproject.com/en/stable/ref/settings/#server-email

Sending E-Mail
--------------

When any part of the application sends an email, the sender defaults to ``DEFAULT_FROM_EMAIL``.

``DEFAULT_FROM_EMAIL``
  see https://docs.djangoproject.com/en/stable/ref/settings/#default-from-email


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
  Age in days, after which activity counts as *not active*. Group ordering is based on
  acitivity. Defaults to ``0``.

``UPLOAD_MAX_FILE_SIZE``
  File size in MB to which uploads are restricted. Set the value allowed by the webserver to
  a higher value. Defaults to ``0``.

Special Users and Groups
------------------------

``FEED_IMPORTER_GESTALT_ID``
  ID of the user (gestalt), which is set by the RSS feed importer as the author of imported
  content. Defaults to ``1``.

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


Other Options
=============

``ACCOUNT_DEFAULT_HTTP_PROTOCOL``
  Used to generate links sent via email. Defaults to ``'http'``. You probably want to set it
  to ``'https'``.

