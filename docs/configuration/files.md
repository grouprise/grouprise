# Configuration Files

*grouprise* is looking for configuration files in the following locations:

* filename or directory specified in environment variable `GROUPRISE_CONFIG`
* `grouprise.yaml` (in the current directory)
* `~/.config/grouprise/conf.d/` (in user's home directory)
* `/etc/grouprise/conf.d/` (system-wide configuration)

The first location, that contains any [yaml](https://yaml.org/) files is selected.
Files in subsequent locations are ignored.
If the location is a directory, then all files within this directory (filenames ending in `.yaml` and consisting only of alphanumeric characters and hyphens) are parsed in alphabetical order.
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
        logo_backdrop: /stadt/media/example.org/logo_backdrop.svg
        logo_favicon: /stadt/media/example.org/favicon.ico
        logo_square: /stadt/media/example.org/logo_large.svg
        logo_text: /stadt/media/example.org/logo_text.svg

backup_path: /var/backups/grouprise

extra_django_settings_filenames:
        - /etc/grouprise/django_settings.py
```

## Grouprise settings

Take a look at the [list of grouprise settings](/configuration/options).


## Advanced settings

It is possible to configured advanced Django features (not specific to *grouprise*) by using Django's configuration format:

1. specify a filename in `extra_django_settings_filenames` (see the example above)
2. add any [Django configuration settings](https://docs.djangoproject.com/en/stable/ref/settings/) to this file
