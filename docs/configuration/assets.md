# Asset Management

grouprise assets are compiled during build time. If you want to use additional assets you can add them via the theming mechanism (overriding templates). You should as well adjust the CSP directives.


## Adjusting CSP directives

If you add new assets (e.g. scripts oder styles) to your setup, you have to check your CSP setup. See the [Django-CSP documentation](https://django-csp.readthedocs.io/en/latest/configuration.html) for all options.

Local external assets are allowed by default. If you want to add assets from another host, add something to your config like:

```python
CSP_DEFAULT_SRC += ("https://sub.example.org",)

CSP_SCRIPT_SRC += ("https://sub.example.org",)
```

You can also use inline scripts in local templates:

```python
CSP_SCRIPT_SRC += ("'sha256-0123456789abdcef'",)
```

Use [Sentry](https://sentry.io/) to track CSP errors:

```python
CSP_REPORT_URI = ("https://sentry.example.org/api/2/csp-report/?sentry_key=0123456789abcdef",)
```


## Adding Scripts or Stylesheets

You may override any grouprise template. To do so, add something like the following line to `/etc/grouprise/settings.py`:

```python
TEMPLATES[0]['DIRS'] += ['/var/www/mysite/templates/']
```

For adding scripts or stylesheets the hook include `core/_head.html` is especially useful. Just add a file `core/_head.html` to your local template directory as defined by the line above and add local stylesheet and link definitions to that file. Don't forget to adjust the CSP directives as described in the previous section.

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

```css
:root {
    --color-primary: red;
    --color-primary-dark: crimson;
}
```
