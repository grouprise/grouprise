# grouprise Deployment

This guide helps you to install *grouprise* on Debian or one of its derivates like Ubuntu.
If you don’t want to use a Debian-based system or wish to install *grouprise* by hand see
the [separate instructions for manual deployments](./manual_deployment.md).

We would also like to support Docker deployments, but have not enough knowledge in that
specific domain and some reservations regarding security. We will however gladly accept
any documentation on this matter, so feel free to open a merge/pull request.


## Installation with apt

You can install *grouprise* from our deb repository.

Execute the following lines as root on the server host:

```bash
# This installs the https-transport. Debian only supports http-based repositories by default.
apt update && apt install apt-transport-https
# This registers our gpg key, so apt won’t reject our packages as untrusted.
wget -qO- https://deb.grouprise.org/keys/repository.asc | apt-key add -
# This adds our deb repository to the list of repositories in your system.
echo "deb https://deb.grouprise.org/ unstable main" >/etc/apt/sources.list.d/grouprise.list
# Update the package index and install grouprise
apt update && apt install grouprise
```


## Configuration

This is outlined in the separate [configuration documentation](./configuration.md).
Follow the [Quick Steps](./configuration.md#quick-steps) if you just want to
get started fast.


## Manual Installation

This is outlined in the separate [documentation on manual deployments](./manual_deployment.md).
