# grouprise Deployment (Version 2.X.X)

Idealerweise kannst du grouprise via deb-Paket installieren. Falls das nicht geht, hilft dir die folgende Anleitung.


## Abhängigkeiten installieren

Folgende Software wird benötigt:

* `python3`
* `pip`
* `virtualenv`
* `nodejs`

Ein passendes DBMS, wir empfehlen `postgresql` mit Python-Bindings (`python3-psycopg2`).

Außerdem verwenden wir in dieser Anleitung eine Konfiguration mit uWSGI und NGINX:

* `uwsgi`
* `uwsgi-plugin-python3`
* `nginx`

Für einige Funktionen von grouprise wird weitere Software benötigt:

* `python3-xapian` (für die Suchfunktion)
* `redis-server` (für asynchronen Nachrichtenversand)


## Quelltext installieren

Das aktuelle stabile Release findest du unter [git.hack-hro.de](https://git.hack-hro.de/stadtgestalten/stadtgestalten/tags).

Kopiere den Quelltext in ein passendes Verzeichnis deiner Wahl, wir verwenden hier `/usr/local/share/grouprise`.


## Virtualenv und Assets installieren

Die folgenden Zeilen verändern ausschließlich Dateien im grouprise-Verzeichnis.

```bash
cd /usr/local/share/grouprise
make virtualenv_create
. build/venv/bin/activate
make
```


## Konfigurationsdatei installieren

Kopiere die [Beispieldatei](https://git.hack-hro.de/stadtgestalten/stadtgestalten/tree/master/docs/deployment/settings.py) nach `/etc/grouprise/settings.py`. Passe die Einstellungen an.

Falls du PostgreSQL verwendest, helfen dir die folgenden Zeilen beim Einrichten der Datenbank:

```sql
CREATE USER grouprise WITH PASSWORD 'xxxxx';
CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;
```

(Dafür muss das Locale `de_DE.UTF8` für PostgreSQL installiert sein.)

Nun kannst du einen Link setzen, damit grouprise die Konfiguration findet und die Datenbank initialisieren:

```bash
cd /usr/local/share/grouprise
ln -s /etc/grouprise/settings.py stadt/settings/local.py
python manage.py migrate
```

Anschließend kannst du grouprise zum ersten Mal ausprobieren (`yourhostname.org:8000`):

```bash
python manage.py runserver 0.0.0.0:8000
```

(Wenn du in den Einstellungen `DEBUG = True` setzt, sieht die Seite auch hübsch aus. Vergiss nicht, die Einstellung zurückzusetzen!)


## uWSGI und NGINX einrichten

* install NGINX and uWSGI (being recommendations of the grouprise package): `apt install nginx uwsgi uwsgi-plugin-python3`
* enable the uWSGI service: `ln -s ../apps-available/grouprise.ini /etc/uwsgi/apps-enabled/`
* start uWSGI: `service uwsgi start`
* copy the NGINX site example configuration: `cp /usr/share/doc/grouprise/examples/nginx.conf /etc/nginx/sites-available/grouprise`
* set a suitable `server_name`: `edit /etc/nginx/sites-available/grouprise`
    * or remove the `default` NGINX site (if it is not in use) in order to let the `grouprise` site be picked irrespective of the requested hostname
* enable the site: `ln -s ../sites-available/grouprise /etc/nginx/sites-enabled/`
* restart NGINX: `service nginx restart`
* visit the fresh grouprise instance: `http://localhost/` (or use a suitable hostname)


## Weitere Dienste einrichten

Für einige Funktionen werden weitere Dienste benötigt. Anleitung folgt.
