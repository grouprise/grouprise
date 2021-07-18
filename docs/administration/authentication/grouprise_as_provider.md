# Grouprise as an Identity Provider

*grouprise* can act as an identity provider.
This allows third party applications to use *grouprise* as an authentication backend.
Users may use their *grouprise* login credentials (or even their active session) for accessing
these third party applications.

Possible third party applications are:

* [Matrix](https://matrix.org/): instant messaging
* [gitlab](https://docs.gitlab.com/ce/administration/auth/oidc.html): issues and wiki
* [MediaWiki](https://www.mediawiki.org/wiki/Extension:OpenID_Connect): wiki
* ... and many more.



## Implementations

A variety of implementations exist.
The provided protocol needs to be supported by the third party application.
Multiple implementations (for different protocols) may be used in parallel.

The following list of Django applications implementing the various protocols is not exhaustive.


### SAML

* [djangosaml2idp](https://github.com/OTA-Insight/djangosaml2idp):
    * no Debian package
    * not very active development, probably it is feature-complete


### OpenID-Connect

* [django-oidc-provider](https://github.com/juanifioren/django-oidc-provider):
    * no Debian package
    * not very active development, probably it is feature-complete
* [django-openid-op](https://github.com/mesemus/django-openid-op):
    * no Debian package
    * maintainer describes it as *Under development, please do not use yet*


### CAS

* [CAS Server](https://github.com/nitmir/django-cas-server):
    * [Debian package](https://packages.debian.org/python3-django-cas-server/) is available
    * a separate login activity is required, since the grouprise session is not related to the CAS
      session (see [django-cas-server#70](https://github.com/nitmir/django-cas-server/issues/70))


### OAuth

OAuth is focussed on authorization.  Thus maybe it is not a suitable choice for authentication.

* [Django OAuth Toolkit](https://github.com/jazzband/django-oauth-toolkit/):
    * [Debian package](https://packages.debian.org/python3-django-oauth-toolkit/) is available


## Configuration

The above example implementations can be configured just like any other Django application in
*grouprise*'s settings file.
