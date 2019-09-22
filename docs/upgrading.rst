Upgrading grouprise
===================

Packaged Setup
--------------

Users of packaged releases of grouprise (e.g. as a deb package) should only need to upgrade the
installed package.

All other upgrade-related actions (see below for the "Source Setup") were prepared by the package
maintainer in an automatic fashion.


Source Setup
------------

#. Download and extract the source release archive.
#. Stop the grouprise process (e.g. ``service uwsgi stop``).
#. Run `make install` with the same parameters that you used during the first installation.
#. Read the release notes for the relevant versions and adjust the settings
   (in ``/etc/grouprise/``) if necessary.
#. Run `grouprisectl migrate` in order to apply outstanding database migrations.
#. Start the grouprise process (e.g. ``service uwsgi start``)
