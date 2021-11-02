# Import and Export

The *grouprise* content submitted by users is stored in two locations:

* database: text-based content
* media directory: file-based content (e.g. images or file uploads)


## Export

The data can be exported:

```shell
service grouprise stop
grouprisectl database_dump
grouprisectl media_dump
service grouprise start
```

The default backup directory is defined by the [backup_path](../configuration/options.html#backup-path).
It can be overridden for the above `database_dump` and `media_dump` operations via the `--output-dir` argument.

The above `database_dump` command creates a dump, which is bound to the current database engine.
See :ref:`database-move` for a database-neutral export format.


## Import

The following steps import the media and the database content:

```shell
service grouprise stop
grouprisectl media_import --filename MEDIA_ARCHIVE.tar.gz
# drop all tables (or create a new database) before importing the archived data
zcat DATABASE_DUMP.sql.gz | grouprisectl dbshell
service grouprise start
```
