# Templates for grouprise

Under some circumstances it may be helpful to override specific templates within *grouprise*.

You will need to find the relevant template file on your own and adjust (or replace) it according
to your needs.

The list of grouprise's builtin template files can be retrieved:

```shell
find /usr/share/grouprise/python-lib/grouprise -type d -name templates \
    | xargs -I '{}' find '{}' -type f
```

You can override any of these files by placing a file with the same name (and the same directory
hierarchy above it) below one of the configured
[template directories](https://docs.grouprise.org/administration/configuration/options.html#template-directories).
By default `/etc/grouprise/templates` is configured in a [deb-based deployment](/deployment/deb).

See [Django's documentation for templates](https://docs.djangoproject.com/en/stable/topics/templates/)
for additional information.
