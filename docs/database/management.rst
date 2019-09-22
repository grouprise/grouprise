Database Management
-------------------

.. _database-move:

Move to a different database or engine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use cases:

* move to a different database storage (e.g. provided by a different database host)
* change the database engine (e.g. from SQLite to PostgreSQL)

.. info:

    The procedure described below requires manual adjustments of the dumped data due to
    https://git.hack-hro.de/stadtgestalten/stadtgestalten/issues/629. Thus it is currently only
    suitable for very small sets of data.

Procedure:

1. stop the running grouprise service (e.g. :code:`service uwsgi stop`)
2. dump the current database in a database-neutral format: :code:`grouprisectl dumpdata --natural-primary --natural-foreign --exclude sessions --exclude admin.logentry --exclude contenttypes.contenttype --exclude auth.permission >grouprise-export.json`
3. change the database settings in :code:`/etc/grouprise/settings.py` (see 
4. create new database (see :ref:`database-initialization`)
5. populate the database structure: :code:`grouprisectl migrate`
6. load the export data: :code:`grouprisectl loaddata --format=json - <grouprise-export.json`
7. start the grouprise service (e.g. :code:`service uwsgi start`)
