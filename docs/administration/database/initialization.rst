.. _database-initialization:

Database Initialization
-----------------------

grouprise stores most of its data in a database. By default an SQLite database is configured.
For a more scalable setup you should consider switching to another database engine later.

All database engines except SQLite require the creation of a database in advance.
The following sections demonstrate this step for various databases.

After creating the database (see below), you need to:

1. configure its access credentials (see :ref:`database-engines`)
1. and populate its structure (:code:`grouprisectl migrate`) or import existing data (see :ref:`database-move`).


PostgreSQL
^^^^^^^^^^

.. code-block:: sql

    CREATE ROLE grouprise LOGIN PASSWORD 'some_secret_password';
    CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;

You may need to enable the locale `de_DE.UTF8` before: `dpkg-reconfigure locales`.

MySQL / MariaDB
^^^^^^^^^^^^^^^

.. code-block:: sql

    CREATE USER grouprise IDENTIFIED BY 'some_secret_password';
    CREATE DATABASE grouprise CHARACTER SET = 'utf8' COLLATE = 'utf8_general_ci';
    GRANT ALL PRIVILEGES ON grouprise.* TO grouprise;
    FLUSH PRIVILEGES;
