# Asset Management

The frontend assets for *grouprise* are compiled during build time.
If you want to use additional assets you can add them via the theming mechanism (overriding templates).


## Adjusting CSP directives

If you add new assets (e.g. scripts or styles) to your setup, you have to check your CSP setup.
See the [Django-CSP documentation](https://django-csp.readthedocs.io/en/latest/configuration.html) for all options.

See *grouprise*'s [CSP-related settings](/administration/configuration/options.html#content-security-policy-csp).


## Templates

You may override any grouprise template.

In [deb-based deployments](/deployment/deb), you may place templates below `/etc/grouprise/templates/`.

Alternatively you may specify alternative locations for [templates](options.html#template-directories):
```yaml
template_directories:
    - /opt/grouprise-templates/
```


## Adding Scripts or Stylesheets

### Configure additional scripts or CSS files

See *grouprise*'s relevant settings:

* [`scripts`](/administration/configuration/options.html#scripts)
* [`stylesheets`](/administration/configuration/options.html#stylesheets)


### Manually override HTML `head` content via templates

The following procedure (overriding templates) is necessary only under very rare circumstances.
Take a look at `scripts`, `stylesheets` or the CSP settings mentioned above.

If you want to add more than just scripts or CSS files, then you should override the header file `core/_head.html`.
By default, *grouprise* ships an empty file with that name.
Just add a file `core/_head.html` to your local template directory (by default: `/etc/grouprise/templates/`) and add local stylesheet and link definitions to that file.
Don't forget to adjust the CSP directives as described in the previous section.

Take a look at the next section about style variables to learn about easy style overrides with CSS variables.


## Style Variables

To ease the process of overriding styles, grouprise supports CSS variables where applicable. CSS variables are a nice thing because with a single rule you can override a setting on the entire platform. Please mind that support for these type of variables is a browser feature and rather new, so you may still want to override individual styles depending on your target audience.

### Supported Variables

The following variables are supported:

`--color-primary`
 : used throughout the platform as brand color. determines the appearance of links, buttons, focus rings, etc.

`-color-primary-dark`
 : used for active states where `--color-primary` is used. if you override `--color-primary` you want to override this variable.

### CSS Example

```
:root {
    --color-primary: red;
    --color-primary-dark: crimson;
}
```
