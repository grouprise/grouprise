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


## Overriding Styles

FIXME: Revise this section after adding theming support.

If you want to override styles or colors you can do that by adding
a custom stylesheet. The easiest way to do this is to add the following line to your local configuration (or `/etc/grouprise/settings.py`):

```python
from core.assets import add_style_reference
add_style_reference('stadt/custom.css')
```

This will add a stylesheet reference to `/stadt/static/stadt/custom.css`. On your local machine this matches the `$PROJECT_DIR/build/static/custom.css` path. On a production server you would add a configuraton to the webserver that creates an alias for the mentioned path to the local filesystem. A simple nginx example:

```nginx
location /stadt/static/stadt/custom.css {
    alias /var/www/custom.css;
}
```

Take a look at the next section about style variables to learn about easy style overrides with CSS variables.

Note: Please refrain vom using the `add_style_inline` function from the `core.assets` module as it will break JavaScript-generated inline-styles in HTML.
 

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
