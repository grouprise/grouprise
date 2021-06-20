Database Engines
----------------

grouprise stores most of its data in an SQL database. Only uploaded media files are stored in the
filesystem.

All databases supported by `Django <https://www.djangoproject.com/>`_ are usable for grouprise, e.g.:

* SQLite
* PostgreSQL
* MySQL / MariaDB

See the
`Django Database documentation <https://docs.djangoproject.com/en/stable/ref/settings/#databases>`_
for all settings related to the database connection.

By default grouprise uses the SQLite backend.  A public site should probably use one of the other
database backends instead, in order to improve performance.

The database engine and its details are configured below :code:`/etc/grouprise/conf.d/`.


Example Configurations
^^^^^^^^^^^^^^^^^^^^^^

SQLite
~~~~~~

.. code-block:: yaml

    database:
            engine: sqlite
            name: '/var/lib/grouprise/db.sqlite3'

PostgreSQL
~~~~~~~~~~

.. code-block:: yaml

    database:
        engine: postgresql
        name: 'mydatabase'
        user: 'mydatabaseuser'
        password: 'mypassword'
        host: '127.0.0.1'
        port: 5432

MySQL / MariaDB
~~~~~~~~~~~~~~~

.. code-block:: python

    database:
        engine: mysql
        name: 'mydatabase'
        user: 'mydatabaseuser'
        password: 'mypassword'
        host: '127.0.0.1'
        port: 3306

In case of MySQL before v5.7: please read
`Django hints for the setting 'sql_mode' <https://docs.djangoproject.com/en/stable/ref/databases/#mysql-sql-mode>`_.
