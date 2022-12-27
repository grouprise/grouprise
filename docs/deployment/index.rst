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
            uwsgi [label = "uWSGI"]
            worker [label = "Task Runner"]
            lmtp [label = "LMTP Server"]
        }
        {
            rank = "min"
            web_server [label = "Web Server"]
            mail_server [label = "Mail Server"]
            matrix_server [label = "Matrix Server"]
        }

        web_server -- uwsgi -- django -- database [dir = "both"]
        worker -- django [dir = "both"]
        mail_server -- lmtp -- django [dir = "forward"]
        django -- matrix_server [dir = "forward"]
        django -- mail_server [dir = "forward"]
        media -- web_server [dir = "forward"]
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

uWSGI
  The `uWSGI <http://projects.unbit.it/uwsgi/>`_ application server connects *grouprise* with the web server.

Web Server
  The web server (e.g. apache2 or nginx) serves the content provided by *grouprise* to its users.

LMTP Server
  The integrated LTMP server handles incoming mails and injects them into the *grouprise* application.

Mail Server
  The external mail server (e.g. Postfix or Exim) delivers outgoing emails to external recipients
  and transfers incoming mails to the integrated LTMP Server.

Matrix Server
  `grouprise` can send notifications into [Matrix](https://matrix.org/) chat rooms
  (see `Matrix-Chat <../administration/matrix_chat.html>`_).
  In addition it is possible to manage grouprise content (e.g. delete spam, manage groups) by
  talking to the `Matrix Commander <../management/matrix_commander.html>`_ (a chat bot).

The `deployment based on deb packages <./deb.html>`_ configures most of these components.
