Database Engines
----------------

grouprise stores most of its data in an SQL database. Only uploaded media files are stored in the
filesystem.

All databases supported by `Django <https://www.djangoproject.com/>`_ are usable for grouprise, e.g.:

* SQLite
* PostgreSQL
* MySQL / MariaDB

See the
`Django Database documentation <https://docs.djangoproject.com/en/dev/ref/settings/#databases>`_
for all settings related to the database connection.

By default grouprise uses the SQLite backend.  A public site should probably use one of the other
database backends instead, in order to improve performance.

The database engine and its details are configured in :code:`/etc/grouprise/settings.py`.


Example Configurations
^^^^^^^^^^^^^^^^^^^^^^

SQLite
~~~~~~

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/var/lib/grouprise/db.sqlite3',
        }
    }

PostgreSQL
~~~~~~~~~~

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mydatabase',
            'USER': 'mydatabaseuser',
            'PASSWORD': 'mypassword',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

MySQL / MariaDB
~~~~~~~~~~~~~~~

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mydatabase',
            'USER': 'mydatabaseuser',
            'PASSWORD': 'mypassword',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
