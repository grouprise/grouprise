Deployment
==========

.. toctree::
   :maxdepth: 1

   deb
   source


Architecture
------------

*grouprise* consists of several components:

.. graphviz::

    graph {
        rankdir = "TB"

        {
            rank = "max"
            database [label = "Database"]
            media [label = "Media Storage"]
        }
        {
            rank = "same"
            django [label = "Django", shape = "box", style = "filled", width = "5"]
        }
        {
            rank = "same"
            uwsgi [label = "UWSGI"]
            worker [label = "Task Runner"]
            lmtp [label = "LMTP Server"]
        }
        {
            rank = "min"
            webserver [label = "Webserver"]
            mailserver [label = "Mail Server"]
        }

        webserver -- uwsgi -- django -- database [dir = "both"]
        worker -- django [dir = "both"]
        mailserver -- lmtp -- django [dir = "forward"]
        django -- mailserver [dir = "forward"]
        media -- webserver [dir = "forward"]
        django -- media [dir = "both"]
    }

Django
  *grouprise* uses the `Django Framework <https://djangoproject.com/>`_ for most of its operations.

Task Runner
  A worker process executes periodic or time consuming tasks (e.g. sending email notifications).
  It is based on `huey <https://github.com/coleifer/huey/>`_.

Database
  A database (e.g. PostgreSQL, MySQL or SQLite) is used for storing almost everything (except for media uploads).

Media Storage
  Uploaded media (images, documents, ...) are stored locally in the filesystem.

UWSGI
  The `UWSGI <http://projects.unbit.it/uwsgi/>`_ application server connects *grouprise* with the webserver.

Webserver
  The webserver (e.g. apache2 or nginx) serves the content provided by *grouprise* to its users.

LMTP Server
  The integrated LTMP server handles incoming mails and injects them into the *grouprise* application.

Mailserver
  The external mailserver (e.g. Postfix or Exim) delivers outgoing emails to external recipients and transfers incoming mails to the integrated LTMP Server.

The `deployment based on deb packages <./deb.html>`_ configures most of these components.
