# Configuration Files

*grouprise* is looking for configuration files in the following locations:

* filename or directory specified in environment variable `GROUPRISE_CONFIG`
* `grouprise.conf.d` (in the current directory)
* `grouprise.yaml` (in the current directory)
* `~/.config/grouprise/conf.d/` (in user's home directory)
* `/etc/grouprise/conf.d/` (system-wide configuration)

The first location, that contains any [yaml](https://yaml.org/) files is selected.
Files in subsequent locations are ignored.
If the location is a directory, then all of its children (files and directories) are processed in alphabetical order:

* A file is parsed, if the filename ends in `.yaml` and consists only of alphanumeric characters and hyphens.
* A directory is processed recursively irrespective of its name.
* Items are processed down to their deepest level, before the next item at the same level is processed (depth-first - not breadth-first).

If the location is a file, then only this file is parsed.

Settings in earlier files are overwritten by settings with the same name in later files.

## Example configuration

```yaml
domain: example.org
log_recipient_emails:
        - grouprise@admin.example.org
database:
        engine: postgresql
        host: localhost
        name: grouprise_example_org
        user: grouprise_example_org
        password: "SECRET_DATABASE_PASSWORD"
secret_key: "SOME_RANDOM_SECRET_KEY"
feed_importer_gestalt_id: 1
operator_group_id: 1
unknown_gestalt_id: 32

mailinglist_enabled: True

branding:
        logo_backdrop: /-/site/logo_backdrop.svg
        logo_favicon: /-/site/favicon.ico
        logo_square: /-/site/logo_large.svg
        logo_text: /-/site/logo_text.svg

backup_path: /var/backups/grouprise

extra_django_settings_filenames:
        - /etc/grouprise/django_settings.py
```

## Grouprise settings

Take a look at the [list of grouprise settings](/administration/configuration/options).


## Advanced settings

It is possible to configured advanced Django features (not specific to *grouprise*) by using Django's configuration format:

1. specify a filename in `extra_django_settings_filenames` (see the example above)
2. add any [Django configuration settings](https://docs.djangoproject.com/en/stable/ref/settings/) to this file
