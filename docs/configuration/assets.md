# Asset Management

stadtgestalten assets are compiled during build time, but in order to support dynamic setups we support some function to add new assets or add metadata to the markup.


## Function Reference

All following subsections refer to functions in the `core.assets` module. Optional arguments usually refer to element specific attributes with the exception of `stage` that refers to assets and references that are in included in the `head` element (`early` stage) and at the end of the body element (`late` stage).

### add_javascript_reference

Add a `script` element referencing the provided url via the `src` attribute.

Optional arguments: `defer`, `async`, `stage`

### add_javascript_inline

Add a literal JavaScript string that is embedded as a `script` tag.

Optional arguments: `stage`

### add_style_reference

Add a `link` element referencing the provided url via the `href` attribute.

Optional arguments: `media`, `**kwargs` as link attributes

### add_style_inline

Add a literal CSS string that is embedded via a `style` tag.

NOTE: This breaks support for inline styles due to Content-Security-Policy restrictions. You will some JavaScript code in very subtle ways and you’ll most likely won’t notice the problems immediately.

Optional arguments: `media`, `scoped`

### add_link

Add a `link` element to the `head` referencing the provided url via the `href` attribute.

Optional arguments: `rel`, `**kwargs` as link attributes

### add_meta

Add a `meta` element to the `head` with the provided `name` and `content` attribute.

### add_csp_directive

Adds a Content-Security-Policy directive with the provided `directive` (like `style-src`) and `value`. Note that stadtgestalten servers CSP via response headers so you won’t find any of the provided directives in the HTML output.  


## Overriding Styles

If you want to override styles or colors you can do that by adding
a custom stylesheet. The easiest way to do this is to add the following line to your local configuration (or `/etc/stadtgestalten/settings.py`):

```python
from core.assets import add_style_reference
add_style_reference('stadt/custom.css')
```

This will add a stylesheet reference to `/stadt/static/stadt/custom.css`. On your local machine this matches the `$PROJECT_DIR/build/static/custom.css` path. On a production server you would add a configuraton to the webserver that creates an alias for the mentioned path to the local filesystem. In nginx this would look like this:

```nginx
location /stadt/static/stadt/custom.css {
    alias /var/www/custom.css;
}
```

Take a look at the section about style variables

Note: Please refrain vom using the `add_style_inline` function from the `core.assets` module as it will break JavaScript-generated inline-styles in html.
 

## Style Variables

To ease the process of overriding styles, stadtgestalten supports CSS variables where applicable. CSS variables are a nice thing, because with a single rule you can override a setting on the entire platform. Please mind that the support for these variables is a browser feature and rather new so you may still want to override individual styles depending on your target audience. 

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
