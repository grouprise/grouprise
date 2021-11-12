# Matrix Chat Integration

[Matrix](https://matrix.org/) is a chat communication protocol.
It can be used for real-time communication (with end-to-end encryption) between grouprise users
and also external Matrix users.
Matrix supports [federation](https://en.wikipedia.org/wiki/Federation_(information_technology)).
Thus grouprise users may use either their existing Matrix account (hosted by an external provider)
or they can use a new Matrix account, which is based on their grouprise account.

## Usage

The Matrix integration of grouprise provides the following features (compared with a separate
Matrix homeserver):

* the grouprise user account (name and password) can be used for logging into the Matrix homeserver
  (there is no need for a separate Matrix account)
* a local instance of the [Element](https://github.com/vector-im/element-web) web client is
  provided
* a public and a private Matrix room is automatically created for each grouprise group
* all members of a grouprise group are automatically invited to the group's rooms
* new content (articles, events, discussions, ...) are mentioned (with a link) in their
  corresponding Matrix rooms (internal messages are announced in the private room, only)
* personal messages from other users trigger Matrix notifications, which are sent directly to the
  user
* the group overview page in grouprise provides links to the group's Matrix rooms

Additionally the usual benefits of the Matrix system are available:

* users from external homeservers can join the public rooms and can be invited to the private rooms
* new rooms and communities can be created freely on the homeserver
* direct communication between Matrix users (local and external) is possible
* any [Matrix client](https://matrix.org/clients/) (e.g. on mobile devices) can be used

The web client is accessible via `https://YOUR_DOMAIN/stadt/chat`.


## Administration

### Setup

The following steps are based on the [deb-based deployment](../deployment/deb) and require
Debian Bullseye (or a similar derivative distribution release).

1. add the `bullseye-backports` repository to your apt packages sources (see [instructions](https://backports.debian.org/Instructions/))
1. update the package cache: `apt update`
1. install the matrix server: `apt install matrix-synapse/bullseye-backports`
1. create the postgresql database connection for matrix-synapse:
```
CREATE USER grouprise_matrix WITH password 'YOUR_SECRET_RANDOM_PASSWORD';
CREATE DATABASE grouprise_matrix ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C' template=template0 OWNER grouprise_matrix;
```
1. configure this database connection (e.g. in `/etc/matrix-synapse/conf.d/database.yaml`):
```yaml
database:
  name: psycopg2
  args:
    user: grouprise_matrix
    password: "YOUR_SECRET_RANDOM_PASSWORD"
    database: grouprise_matrix
    host: YOUR_DATABASE_SERVER
    cp_min: 5
    cp_max: 10
```
1. start matrix-synapse: `service matrix-synapse start`
1. install the matrix integration package for grouprise: `apt install grouprise-matrix`
1. answer the configuration questions during package installation:
    * matrix-synapse:
        * server: the name of your grouprise domain (e.g. `example.org`)
    * element-web-installer:
        * webserver configuration: *none* (configuration is done by `grouprise-matrix`)
        * default matrix server: the name of your grouprise domain (e.g. `example.org`)
    * grouprise-matrix:
        * webserver configuration: *nginx*
1. Run `grouprisectl matrix_chat_manage configure-rooms` and `grouprisectl matrix_chat_manage invite-room-members` in order to populate the Matrix rooms for all groups.  You may omit this step, since it will happen automatically within one hour, anyway.


### Configuration settings

The following configuration settings are available below the `matrix_chat` path in your grouprise settings file (e.g. `/etc/grouprise/conf.d/local.yaml`).
They are configured automatically during the deb package configuration.

* `domain`: The Matrix domain to be used.  Defaults to the grourise domain.
* `bot_username`: The local name of the Matrix bot used by grouprise.  Defaults to `grouprise-bot`.
* `bot_access_token`: The access token of the Matrix bot used by grouprise.  To be generated via
  `GROUPRISE_USER=root grouprisectl matrix_register_grouprise_bot`.  In case of manual account
  creation, it can be retrieved from the Matrix grouprise database via
  `select token from access_tokens where user_id='@USERNAME:MATRIX_DOMAIN';`.
* `admin_api_url`: An API URL of the Matrix instance, which accepts Synapse admin requests
  (e.g. `/_synapse/admin`).  Defaults to `http://localhost:8008`.
* `public_listener_rooms`: A list of Matrix room identifiers (ID or alias).
  Public content (e.g.  articles or events) is announced in these Matrix rooms.
  The Matrix bot needs to be a member of these rooms.
  Defaults to an empty list.

Example:
```yaml
matrix_chat:
    enabled: true
    bot_username: grouprise-bot
    bot_access_token: 'SECRET_ACCESS_TOKEN'
```


### Authentication via OIDC

It is possible configure *grouprise* as an OIDC authentication provider for *matrix-synapse*.
This allows users to log into their matrix account with their *grouprise* session (e.g. via
the *element* web client).

The steps below are only relevant for the source-based installation of *grouprise*.
The *deb* package provided for *grouprise* automatically handles these steps.

#### Settings for grouprise

##### Dependencies

* install the Python package *django-oauth-toolkit*:
    * Debian: `apt install python3-django-oauth-toolkit`
        * At the moment, this package is only available in Debian Testing (*Bookworm*).
          You need to add this repository to your `sources.list` or use the *pip* approach (see below).
    * *pip* (local Python module installation):
        * `pip3 install --user "django-oauth-toolkit>=1.5.0"`
        * add the line `pythonpath = /root/.local/lib/python3.X/site-packages` to your uwsgi configuration (e.g. `/etc/grouprise/uwsgi.ini`)
            * adjust the Python version according to your setup

##### Configuration

1. set `oidc_provider: {enabled: true}` in the grouprise configuration (e.g. `/etc/grouprise/conf.d/200-matrix_chat.yaml`)
2. add an OAuth client configuration via Django's admin interface (`/stadt/admin`):
    * User: empty
    * Redirect URL: `https://example.org:8448/_synapse/client/oidc/callback`
    * Client Type: *confidential*
    * Authorization Type: Authorization Code
    * Name: *matrix_chat*
    * Skip Authorization: true
    * Algorithm: RSA

#### Settings for matrix-synapse

##### Dependencies

* `apt install python3-authlib`
    * matrix-synapse requires this module, if OIDC is enabled

##### Configuration

Configure the OIDC provider (e.g. in `grouprise-matrix-authentication.yaml`):
```yaml
password_config:
   enabled: false

public_baseurl: "https://example.org:8448/"

oidc_providers:
  - idp_id: example
    idp_name: example.org
    discover: true
    issuer: "https://example.org/stadt/oauth/"
    client_id: "SEE_GROUPRISE_OAUTH_APPLICATION"
    client_secret: "SEE_GROUPRISE_OAUTH_APPLICATION"
    client_auth_method: client_secret_post
    scopes: ["openid"]
    skip_verification: true
    user_mapping_provider:
      config:
        subject_claim: "id"
        localpart_template: "{{ user.id }}"
        display_name_template: "{{ user.display_name }}"
        email_template: "{{ user.email }}"
```
