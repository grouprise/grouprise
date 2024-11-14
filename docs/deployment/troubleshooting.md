# Troubleshooting

## Status of grouprise service

```shell
systemctl status grouprise
```

The service should be "active".

Try `service grouprise restart`, if the service is currently not active.


## Grouprise service log

Check the service log:
```shell
journalctl -u grouprise
```

The above log output may be almost empty (only startup and stop events).

In this case the *real* log is stored in `/var/log/grouprise/uwsgi.log`.

Here you can find the access log (HTTP requests) as well as unexpected errors within grouprise.

## Other services

List the currently configured *grouprise*-related services:
```shell
systemctl list-units "grouprise*"

```

Check their status (`systemctl status SERVICE_NAME`) or look into their logs
(`journalctl -u SERVICE_NAME`) if you encounter problems with these services.
