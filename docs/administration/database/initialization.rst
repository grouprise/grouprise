.. _database-initialization:

Database Initialization
-----------------------

grouprise stores most of its data in a database. By default an SQLite database is configured.
For a more scalable setup you should consider switching to another database engine later.

All database engines except SQLite require the creation of a database in advance.
The following sections demonstrate this step for various databases.

After creating the database, you need to populate its structure (:code:`grouprisectl migrate`) or
import existing data (see :ref:`database-move`).


PostgreSQL
^^^^^^^^^^

.. code-block:: sql

    CREATE ROLE grouprise LOGIN PASSWORD 'some_secret_password';
    CREATE DATABASE grouprise OWNER grouprise;


MySQL / MariaDB
^^^^^^^^^^^^^^^

.. code-block:: sql

    CREATE USER grouprise IDENTIFIED BY 'some_secret_password';
    CREATE DATABASE grouprise CHARACTER SET = 'utf8' COLLATE = 'utf8_general_ci';
    GRANT ALL PRIVILEGES ON grouprise.* TO grouprise;
    FLUSH PRIVILEGES;
