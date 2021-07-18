# Matrix-Commander

The *Matrix-Commander* is a simple bot for the [Matrix](https://matrix.org/) protocol.
You may invite it into a room and execute common administrative actions by talking to it.

Communication is rather simple:
```
# request
grouprise-commander-bot user show alice

# response
Username: alice
Email: alice@example.org
Contributions: 403
Group memberships: 27
Latest contribution: 2021-07-12 15:02:33+00:00
```

This Matrix bot is not related to the *matrix_chat* feature of *grouprise*.
The matrix bot can either be an account on you local Matrix server or on any extern Matrix somewhere.


## Configuration

Follow these steps:

1. Generate a bot account and retrieve its access token:
    * In case you are running a local Matrix server for the *matrix_chat* feature:
        ```shell
        GROUPRISE_USER=root grouprisectl matrix_register_grouprise_bot --print-only --bot-username=grouprise-commander-bot
        ```
    * If you are not running a local Matrix server, you may just register an account on any Matrix server and retrieve this account's access token (e.g. in the *element* web client below *Profile -> Help and About*).
1. Invite the bot (`@grouprise-commander-bot:example.org`) into a new matrix room (e.g. via the *element* web client)
1. Create the matrix-commander configuration (e.g. `/etc/grouprise/conf.d/300-matrix_commander.yaml`):
    ```yaml
    matrix_commander:
            enabled: true
            bot_id: "@grouprise-commander-bot:example.org"
            bot_access_token: "ACCESS_TOKEN_GENERATED_ABOVE"
            admin_rooms:
                    - "!lTcmhpFGnyuvwYyeCH:example.org"
    ```
    * The room ID (see above `admin_rooms`) can be found in the *Room Settings* within the *Advanced* tab.
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

Whenever you want to talk to the matrix-commander bot, you need to start the line with its name:
```
grourise-commander-bot help
```

You may also use its full name (here: `@grouprise-commander-bot:example.org`) - this can be easily accomplished by relying on the auto-completion feature of your matrix client (e.g. typing `gro` followed by the `tabulator` key).

All available actions of the bot are explained in the output of the `help` command.
