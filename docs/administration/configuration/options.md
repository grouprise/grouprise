# Configuration Options

## General

### `database`
Configure the database connection to be used for storing grouprise's data.
By default an [sqlite](https://sqlite.org/) database is configured:
```yaml
database:
  engine: sqlite
  name: ~/grouprise.sqlite
```

The supported engines are:

* `mysql`
* `postgresql`
* `sqlite`

The `sqlite` database requires the additional parameter `name`, which specifies the path of the database file.
The `mysql` and `postgresql` database engines accept the additional parameters `host`, `port`, `name`, `user` and `password`.

See [database engines](/administration/database/engines) for examples and details.

### `debug`
Boolean setting for temporarily enabling debug-friendly settings.
This setting should not be enabled in production.

See [Django's documentation of `DEBUG`](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEBUG) for details.

### `debug_toolbar_clients`
Enable [django-debug-toolbar](https://github.com/jazzband/django-debug-toolbar) for a specific list of client addresses.

The *django-debug-toolbar* may be useful for debugging performance issues.

The client list may contain any combination of IPv4/IPv6 addresses or networks.

Example (enabling the toolbar for all clients):
```yaml
debug_toolbar_clients:
- "0.0.0.0/0"
- "::/0"
```

### `domain`
The name of the domain ([FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name)), which is served by your grouprise instance (e.g. `our-local-community.org`).

### `extra_allowed_hosts`
Additional domain names, that should be tolerated by Django's request handler.
Django's related `ALLOWED_HOSTS` list is pre-filled with the `domain` setting (see above).
Thus this setting is rarely necessary.

See [Django's documentation of `ALLOWED_HOSTS`](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-ALLOWED_HOSTS) for details.

### `language_code`
Select the primary language to be used within grouprise and other components (e.g. the search indexer).

See the [list of language codes](http://www.i18nguy.com/unicode/language-identifiers.html) for the range of allowed settings.

Default: `de-de`

### `media_root`
Uploaded files are stored in this directory.

See [Django's documentation of the related setting](https://docs.djangoproject.com/en/stable/ref/settings/#media-root) for details.

### `secret_key`
Specify a random secret key to be used for encryption and signing around form and session handling.

See [Django's documentation of `SECRET_KEY`](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-SECRET_KEY) for details.

### `session_cookie_age`
Expiry time of cookie-based sessions in seconds.
By default the expiration period is two weeks (1209600 seconds).

### `time_zone`
Specify the time zone used for storing timestamps in the database and for visualizing dates and times.

See [Django's configuration](https://docs.djangoproject.com/en/stable/ref/settings/#time-zone) for details.

Default: `Europe/Berlin`

### `transport_security`
Select one of `disabled`, `reverse-proxy` and `integrated`.

The choice `disabled` allows the login procedure to happen via HTTP instead of requiring HTTPS (see [ACCOUNT_DEFAULT_HTTP_PROTOCOL](https://django-allauth.readthedocs.io/en/latest/configuration.html)).
Choose this setting, if your *grouprise* instance is supposed to be served over HTTP only.
The lack of transport encryption should be a source of concern under almost all circumstances.

The choice `integrated` enforces the usage of HTTPS.
This setting assumes, that SSL termination happens within the Django application itself (e.g. via [django-sslserver](https://github.com/teddziuba/django-sslserver)).

The choice `reverse-proxy` enforces the usage of HTTPS, but it relies on an external proxy server for SSL termination.
This is probably the most common usage scenario.
Most webserver implementations feature SSL termination (e.g. *apache2* and *nginx*).
Django assumes, that the request header `HTTP_X_FORWARDED_PROTO` with the value `HTTPS` is injected by the proxy server.

Default: `reverse-proxy`


## Email: delivery of outgoing messages
### `email_submission → backend`
Select a backend to be used for sending emails (e.g. for debugging or development purposes).
By default, emails are delivered via STMP.
It is possible to select one of the following backends:

* `dummy`: outgoing mails are simply discarded
* `console`: outgoing mails are written to the standard output of the grouprise process (e.g. for debugging the handling of confirmation tokens)
* `smtp`: use a local or remote SMTP service for real email delivery (default)

See [Django's configuration](https://docs.djangoproject.com/en/stable/ref/settings/#email-backend) for details.

Default: `smtp`

### `email_submission → host`
Select an SMTP host to be used for delivering outgoing emails.
This setting is only used, if `email_submission → backend` is configured as `smtp`.

Default: `localhost`

### `email_submission → port`
Select the remote port of the SMTP host (see `email_submission → host`) for for delivering outgoing emails.
This setting is only used, if `email_submission → backend` is configured as `smtp`.

The default port depends on the `email_submission → encryption` setting.

### `email_submission → user`
Specify a username to used for authentication during SMTP handshake for outgoing emails.
This setting is only used, if `email_submission → backend` is configured as `smtp`.
Authentication is disabled by default.
The password (`email_submission → password`) needs to be configured, too.

### `email_submission → password`
Specify a password to used for authentication during SMTP handshake for outgoing emails.
This setting is only used, if `email_submission → backend` is configured as `smtp`.
Authentication is disabled by default.
The password (`email_submission → user`) needs to be configured, too.

### `email_submission → encryption`
Specify the transport encryption to be used for outgoing messages.
The values `plain`, `ssl` and `starttls` are available.
The value `plain` disables transport encryption (port 25, no encryption), which is suitable only for local submission.
The value `ssl` is used for *implicit encryption* (port 465, TLS is used unconditionally).
The value `starttls` is used for *explicit encryption* (port 587, TLS is enabled after the `STARTTLS` handshake).

Default: `plain`


## Email: addresses

### `default_distinct_from_email`
Outgoing emails related to specific groups use this email address pattern in their `From` field, if no response is expected.

Default: `"noreply+{slug}@{domain}`

### `default_from_email`
Outgoing emails (content notifications or administration messages) use this address in their `From` field.

This email address is used for the following Django settings:

* [`SERVER_EMAIL`](https://docs.djangoproject.com/en/stable/ref/settings/#server-email)
* [`DEFAULT_FROM_EMAIL`](https://docs.djangoproject.com/en/stable/ref/settings/#default-from-email)

Default: `noreply@{domain}`

### `default_reply_to_email`
Outgoing emails related to specific content items or events use this email address pattern in their `From` field, if a response can be expected.

Default: `reply+{reply_key}@{domain}`

### `log_recipient_emails`
Log messages can be configured for sending email notifications for each outgoing log message.

See [`AdminEmailHandler` in Django's documentation](https://docs.djangoproject.com/en/stable/topics/logging/#django.utils.log.AdminEmailHandler) for details.

### `postmaster_email`
Email address of the domain's postmaster.

Default: `postmaster@{domain}`


## Email: handling of incoming messages

### `mailinglist_enabled`
Members of a group may start a conversation with the other group members by sending an email message to `{slug}@{domain}`.
This setting controls the availability of this feature.

Default: `false`

### `collector_mailbox_address`
All incoming mails are expected to be delivered to this single mail address and processed via the *Scripted processing* ("dot-forward") approach described in [mail setup](/administration/mail_setup).
This setting may be left empty, if a different method for mail reception is used.

Default: empty


## Features

### `events → enable_repetitions`
Enable form widgets for creating copies of an event based on a given period.
This represents a trivial approach for supporting recurring events.

Default: `false`

### `events → enable_attendance`
Enable form widgets for indicating the willigness to attend an event.
This may be useful for populating the personal calendar with events of interest.
In addition hosters of events gain an indicator for estimating the number of participants.

Default: `false`


## Special groups and users

### `feed_importer_gestalt_id`
ID of the user (gestalt), which is set by the RSS feed importer as the author of imported content.
This user never receives any kind of notifications, thus it should not be a human's user account.

Default: `1`

### `operator_group_id`
ID of the group which is treated as the operator group of the platform.

Default: `1`

### `unknown_gestalt_id`
ID of the user (gestalt), which is set as the author for content by users, which have been deleted.

Default: `1`


## Theme and content customizations

### `branding → logo_backdrop`
This logo is used on the left hand side of the footer.
Generally you should use a type of white mask graphic here.
See the default grouprise backdrop logo for reference.

### `branding → logo_favicon`
This logo is used as the applications favicon that is usually visible on the left hand side of the browser tab right next to the title of the webpage.
We recommend that you use a PNG file for the favicon as support for SVG favicons is still spotty (as of Aug 2020).
You can set this to `None` if you want to embed the favicon through other means.

### `branding → logo_square`
This logo is used in various places like the login form, menus, help pages and other places.
As the name states this logo should be a square image.
Please use an absolute URL if you override this logo as it will be used by external services to reference your site.

### `branding → logo_text`
This logo file is used in the main menu on the top left part of the screen.
It has a fixed height of around 44 pixels and should not occupy more than 230 pixels of width.

### `branding → theme_color`
This is the color that modern browsers (especially on mobile) use to decorate the tab with.
You can set this to `None` if you want to embed the theme color through other means.

Default: `#2a62ac`

### `claims`
A list of verbal claims intended to entertain, inspire or confuse your users.
A random claim is displayed in the top left corner for each request.

Default: `[]` (empty)

### `entity_slug_blacklist`
A list of reserved slugs for users and groups that cannot be chosen by users.
Exclude slugs that you want to use as mail addresses or subdomains.
You should always include `stadt`, which is the root namespace used by grouprise URLs.

Default: `[all, grouprise, info, mail, noreply, postmaster, reply, stadt, webmaster, www]`

### `score_content_age`
The ordering of groups and users in certain places is based on their activity.
The `score_content_age` setting limits, how old (in days) content may be in order to be included in the calculation of this activity score.
Older content has no impact at all.

Default: `100`

### `scripts`
Add custom javascript resources either as inline snippets or by referencing a local URL path.
The `scripts` setting is a list of dictionaries.
Each item needs to contain either a `path` (absolute URL path of the local resource) or a `content` (inline javascript code).
Additionally a `load` value may be added for a `path` value.
A proper CSP hash is automatically configured for a `content` value.
External resources may not be referenced, since this would leak user's data to remote servers.

Default: `[]` (empty)

### `stylesheets`
Add custom CSS stylesheets in order to override specific layout details.
The `stylesheets` setting is a list of dictionaries.
Each item needs to contain a `path` (absolute URL path of the local resource).
Additionally a [`media` value](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link) may be specified (e.g. `print`).

Default: `[]` (empty)

### `template_directories`
You may want to customize grouprise templates in order to add custom widgets or for embedding additional frontend resources.
The `template_directories` setting is a list of directory names, which are used for looking up templates.
Any configured directory has a higher precedence than *grouprise*'s builtin template locations.

Default: `[]` (empty)

### Content Securicy Policy (CSP)
The Content Security Policy is relevant, if you want to execute customized client-side code in the context of your grouprise instance (e.g. visitor tracking via [matomo](https://matomor.org/) or customized frontend features).

*grouprise* provides the following settings:

* `csp → script_src`
* `csp → default_src`
* `csp → connect_src`

See the [Django CSP documentation](https://django-csp.readthedocs.io/en/latest/configuration.html) for details.


## Authentication

### `oidc_provider → enabled`

It is possible to use the *grouprise* instance as an [OIDC](https://en.wikipedia.org/wiki/OIDC) provider.
This could be useful for connecting external services with the *grouprise* instance (e.g. a [Matrix-Synapse](https://github.com/matrix-org/synapse/) server).

Client applications (like the Matrix server) need to be added to the OIDC setup (see `/stadt/admin/`).


## System / hosting

### `backup_path`
Backups are created automatically in this directory during [package upgrades](/deployment/deb).

Default: current directory (depending on the context of process execution)

### `extra_django_settings_filenames`
Names of files to be read during startup.
The files are supposed to contain Django-style configuration settings (see [Django documentation](https://docs.djangoproject.com/en/stable/ref/settings/) for details).
The files are parsed after all other settings are processed, thus it is possible to override any undesired configuration assumption imposed by *grouprise*.

In addition to the general Django configuration, this file (*module*) may also contain a function named `post_load_hook`.
This function (if it exists) is called with the current state of the Django settings dictionary as its first and only parameter.
The function is expected to manipulate this dictionary in place, if necessary (e.g. for adding items to the `INSTALLED_APPS` list).

Default: `[]` (empty)

### `hook_script_paths`
A list of paths to executables to be called upon certain events.
It is receiving JSON data describing the event as the first argument.
The following events are supported:

* event types: `created`, `changed`, `deleted`
* object types: `Group`

Example data looks like this:
```json
{
  "eventType": "created",
  "objectType": "Group",
  "objectData": {
    "id": 4,
    "slug": ""
  }
}
```

Default: `[]` (empty)

### `upload_max_file_size`
File size in MB to which uploads are restricted.
Set the value allowed by the webserver to a higher value.

Default: `10`
