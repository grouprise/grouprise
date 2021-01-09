# Matrix Chat Integration

[Matrix](https://matrix.org/) is a chat communication protocol.
It can be used for real-time communication (with end-to-end encryption) between grouprise users
and external Matrix users.
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
* the group overview page in grouprise provides links to the group's Matrix rooms

Additionally the usual benefits of the Matrix system are available:

* users from external homeservers can join the public rooms and can be invited to the private rooms
* new rooms and communities can be created freely on the homeserver
* direct communication between Matrix users (local and external) is possible
* any [Matrix client](https://matrix.org/clients/) (e.g. on mobile devices) can be used

The web client is accessible via `https://YOUR_DOMAIN/stadt/chat`.


## Setup

The following steps are based on the [deb-based deployment](deployment/deb).

Warning: currently (January 2021) the required Debian packages are not part of a stable Debian
release (as of now: Debian Buster).
Thus you may need to wait for the next Debian release (*Bullseye*), if you prefer a setup of
packages with proper security support.

1. add the `buster-backports` repository to your apt sources file
   (for the `matrix-synapse` package)
1. install `python3-django-cas-server` from the Debian *testing* repository
   The required version of `python3-django-cas-server` will be part of the *Debian Bullseye* in 2021.
   Hint: do not forget to remove the *testing* repository from your sources list afterwards.
1. install the matrix integration package for grouprise: `apt install grouprise-matrix`
1. answer the configuration questions during package installation:
    * matrix-synapse:
        * server: the name of your grouprise domain (e.g. `example.org`)
    * element-web-installer:
        * webserver configuration: *none* (configuration is done by `grouprise-matrix`)
        * default matrix server: the name of your grouprise domain (e.g. `example.org`)
    * grouprise-matrix:
        * webserver configuration: *nginx*
1. create the postgresql database connection for matrix-synapse:
```
CREATE USER grouprise_matrix WITH password 'YOUR_SECRET_RANDOM_PASSWORD';
CREATE DATABASE grouprise_matrix ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C' template=template0 OWNER grouprise_matrix;
```
1. configure this database connection in `/etc/matrix-synapse/conf.d/grouprise-matrix.yaml`
1. start matrix-synapse: `service matrix-synapse start`
1. generate an administrative access token for matrix-synapse to be used by grouprise: `GROUPRISE_USER=root grouprisectl matrix_register_grouprise_bot`. The resulting access token needs to be configured in `/etc/grouprise/settings.py`:
```python
GROUPRISE["MATRIX_CHAT"] = {
    'ENABLED': True,
    'BOT_USERNAME': 'grouprise-bot',
    'BOT_ACCESS_TOKEN': '_YOUR_BOT_ACCESS_TOKEN_',
}
```
1. Run `grouprisectl matrix_chat_manage create-rooms` and `grouprisectl matrix_chat_manage invite-room-members` in order to populate the Matrix rooms for all groups.

In order to apply all settings properly, it is (for now) necessary to go run the configuration of
the `grouprise-matrix` package manually again:
```shell
dpkg-reconfigure --unseen-only grouprise-matrix
```


## Configuration settings

The following configuration settings are available below the `GROUPRISE["MATRIX_CHAT"]` dictionary
in your grouprise settings file (e.g. `/etc/grouprise/settings.py`):

* `DOMAIN`: The Matrix domain to be used.  Defaults to the grourise domain.
* `BOT_USERNAME`: The local name of the Matrix bot used by grouprise.  Defaults to `grouprise-bot`.
* `BOT_ACCESS_TOKEN`: The access token of the Matrix bot used by grouprise.  To be generated via
  `GROUPRISE_USER=root grouprisectl matrix_register_grouprise_bot`.  In case of manual account
  creation, it can be retrieved from the Matrix grouprise database via
  `select token from access_tokens where user_id='@USERNAME:MATRIX_DOMAIN';`.
* `ADMIN_API_URL`: An API URL of the Matrix instance, which accepts Synapse admin requests
  (e.g. `/_synapse/admin`).  Defaults to `http://localhost:8008`.
