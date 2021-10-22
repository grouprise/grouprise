# Import and Export

The *grouprise* content submitted by users is stored in two locations:

* database: text-based content
* media directory: file-based content (e.g. images or file uploads)

The data can be exported:

```shell
service grouprise stop
grouprisectl database_dump
grouprisectl media_dump
service grouprise start
```

The default backup directory is defined by the [backup_path](../configuration/options.html#backup-path).
It can be overridden for the above `database_dump` and `media_dump` operations via the `--output-dir` argument.
