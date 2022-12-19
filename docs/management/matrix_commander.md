# Matrix-Commander

The *Matrix-Commander* is a simple bot for the [Matrix](https://matrix.org/) protocol.
You may invite the bot into a room and execute common administrative actions by talking to it.

Communication is rather simple:
```
# request
!grouprise user show alice

# response
Username: alice
Email: alice@example.org
Contributions: 403
Group memberships: 27
Latest contribution: 2021-07-12 15:02:33+00:00
```

This [Matrix](https://matrix.org/) bot is not related to the *matrix_chat* feature of *grouprise*.
The Matrix bot can either be an account on your local Matrix server or on any external Matrix homeserver somewhere else.

You should take care, that only trusted people (responsible for content maintenance of your grouprise instance) are in the same room as the bot.


## Configuration

Follow these steps:

1. Generate a bot account and retrieve its access token:
    * In case you are running a local Matrix server for the *matrix_chat* feature:
        ```shell
        GROUPRISE_USER=root grouprisectl matrix_register_grouprise_bot --print-only --bot-username=grouprise-commander-bot
        ```
    * If you are not running a local Matrix server, you may just register an account on any Matrix server and retrieve this account's access token (e.g. in the *element* web client below *Profile -> Help and About*).
1. Invite the bot (`@grouprise-commander-bot:example.org`) into a new matrix room (e.g. via the *element* web client)
    * Please note, that the matrix room may *not* be encrypted. At the moment the bot cannot handle encryption.
1. Create the matrix-commander configuration (e.g. `/etc/grouprise/conf.d/300-matrix_commander.yaml`):
    ```yaml
    matrix_commander:
            enabled: true
            bot_id: "@grouprise-commander-bot:example.org"
            bot_access_token: "ACCESS_TOKEN_GENERATED_ABOVE"
            admin_rooms:
                    - "!lTcmhpFGnyuvwYyeCH:example.org"
            backend: nio
    ```
    * The room ID (see above `admin_rooms`) can be found in the *Room Settings* within the *Advanced* tab.
    * The `backend` can be `nio` (default value, a Matrix client library) or `console` (a dummy implementation for debugging).
1. Try to run the bot manually (with verbose logging; stop it via `CTRL-C`):
    ```shell
    grouprisectl matrix_commander --log-level info
    ```
1. enable and start the service:
    ```shell
    # systemd
    systemctl enable grouprise-matrix-commander
    systemctl start grouprise-matrix-commander
    # sysvinit
    update-rc.d grouprise-matrix-commander defaults
    service grouprise-matrix-commander start
    ```

## Usage

### Matrix Client

Whenever you want to talk to the matrix-commander bot, you need to start the message with one of the supported prefixes:

* generic command prefix: `!grouprise help`
* the bot's Matrix ID (optionally followed by a colon): `@grourise-commander-bot@example.org`
* local part of the bot's Matrix ID (optionally followed by a colon): `grourise-commander-bot`

The Matrix ID of the bot can be easily entered by relying on the auto-completion feature of your Matrix client (e.g. typing `gro` followed by the *tabulator* key).

All available actions of the bot are explained in the output of the `help` command:
```
!grouprise help
```


### Local Console

Instead of using a Matrix client for issuing commands, you can also run *Matrix Commander* locally in a shell:
```shell
grouprisectl matrix_commander --console
```
