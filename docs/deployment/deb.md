# grouprise Deployment

This guide helps you to install *grouprise* on Debian or one of its derivates like Ubuntu.
If you do not want to use a Debian-based system or wish to install *grouprise* manually, then you
should follow the [separate instructions for manual deployments](/deployment/source).

We would also like to support Docker deployments, but we do not have enough knowledge in that
specific domain and some reservations regarding security.
However we will happily accept documentation proposals on this matter, so feel free to open a
merge/pull request.


## Installation with apt

You can install *grouprise* from our `deb` package repository.

Execute the following lines as root on the server host:

```shell
mkdir -p /etc/grouprise
touch /etc/grouprise/apt-keyring.gpg
wget -q -O - https://deb.grouprise.org/keys/repository.asc | gpg --no-default-keyring --keyring /etc/grouprise/apt-keyring.gpg --import
echo "deb [signed-by=/etc/grouprise/apt-keyring.gpg] https://deb.grouprise.org/ unstable main" >/etc/apt/sources.list.d/grouprise.list
apt update
apt install grouprise grouprise-db-postgresql
```

You will be prompted for some details during the package installation procedure.


## Database Configuration

The following statements are suitable for creating a database in postgreSQL:

```sql
CREATE USER grouprise WITH PASSWORD 'xxxxx';
CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;
```

You may need to enable the locale `de_DE.UTF8` before: `dpkg-reconfigure locales`.

Add the corresponding configuration settings somewhere below `/etc/grouprise/conf.d/`.


## Configuration

This is outlined in the separate [configuration documentation](/administration/configuration/index).
