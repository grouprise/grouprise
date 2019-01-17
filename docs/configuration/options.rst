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
  ...

``ENTITY_SLUG_BLACKLIST``
  ...

``SCORE_CONTENT_AGE``
  ...

``UPLOAD_MAX_FILE_SIZE``
  ...

Special Users and Groups
------------------------

``FEED_IMPORTER_GESTALT_ID``
  ...

``OPERATOR_GROUP_ID``
  ...

``UNKNOWN_GESTALT_ID``
  ...

Email-related Settings
----------------------

``DEFAULT_DISTINCT_FROM_EMAIL``
  ...

``DEFAULT_REPLY_TO_EMAIL``
  ...

``MAILBOX_DELIVERED_TO_EMAIL``
  ...

``POSTMASTER_EMAIL``
  ...


Other Options
=============

``ACCOUNT_DEFAULT_HTTP_PROTOCOL``
  Used to generate links sent via email. Defaults to ``'http'``. You probably want to set it
  to ``'https'``.

