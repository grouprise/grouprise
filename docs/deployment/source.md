# Installation aus den Quellen

In den meisten Fällen möchtest du grouprise als [deb-Paket installieren](/deployment/deb).
Falls dies nicht möglich sein sollte oder du spezielle Anforderungen haben solltest, dann folge der untenstehenden Beschreibung zur Installation aus den Quellen.


## Abhängigkeiten installieren

Folgende Software wird benötigt:

* `python3`
* `pip`
* `virtualenv`
* `nodejs`

Hinzu kommt ein passendes DBMS, wir empfehlen `postgresql` mit Python-Bindings (`python3-psycopg2`).

Außerdem verwenden wir in dieser Anleitung eine Konfiguration mit UWSGI und Nginx:

* `uwsgi`
* `uwsgi-plugin-python3`
* `nginx`

Für einige Funktionen von grouprise wird weitere Software benötigt:

* `python3-xapian` (für die Suchfunktion)
* `redis-server` (für asynchronen Nachrichtenversand)


## Quelltext installieren

Das aktuelle stabile Release findest du unter [git.hack-hro.de](https://git.hack-hro.de/grouprise/grouprise/tags).

Kopiere den Quelltext in ein passendes Verzeichnis deiner Wahl, wir verwenden hier `/usr/local/share/grouprise`.


## Virtualenv und Assets installieren

Die folgenden Zeilen verändern ausschließlich Dateien im grouprise-Verzeichnis.

```bash
cd /usr/local/share/grouprise
make virtualenv-update
. build/venv/bin/activate
make
```


## Konfigurationsdatei installieren

Erzeuge eine [Konfigurationsdatei](/configuration/files) unter `/etc/grouprise/conf.d/`.

Falls du PostgreSQL verwendest, helfen dir die folgenden Zeilen beim Einrichten der Datenbank:

```sql
CREATE USER grouprise WITH PASSWORD 'xxxxx';
CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;
```

Eventuell musst du zuvor das Locale `de_DE.UTF8` aktivieren: `dpkg-reconfigure locales`.

Nun kannst du einen Link setzen, damit grouprise die Konfiguration findet und die Datenbank initialisiert:

```bash
cd /usr/local/share/grouprise
python manage.py migrate
```

Anschließend kannst du grouprise zum ersten Mal ausprobieren (`yourhostname.org:8000`):

```bash
python manage.py runserver 0.0.0.0:8000
```

(Wenn du temporär in den Einstellungen `DEBUG = True` setzt, sieht die Seite auch hübsch aus. Vergiss nicht, die Einstellung zurückzusetzen!)


## UWSGI und Nginx einrichten

* install nginx and UWSGI (being remmomendations of the grouprise package): `apt install nginx uwsgi uwsgi-plugin-python3`
* create an UWSGI configuration
    * see [debian/grouprise.uwsgi.ini](https://git.hack-hro.de/grouprise/grouprise/-/blob/master/debian/grouprise.uwsgi.ini)
* create a systemd service for *grouprise*
    * see [debian/grouprise.service](https://git.hack-hro.de/grouprise/grouprise/-/blob/master/debian/grouprise.service)
    * alternative SysVinit script: [debian/grouprise.init](https://git.hack-hro.de/grouprise/grouprise/-/blob/master/debian/grouprise.init)
* start the *grouprise* service: `service grouprise start`
* copy the nginx site example configuration: `cp /usr/share/doc/grouprise/examples/nginx.conf /etc/nginx/sites-available/grouprise`
* set a suitable `server_name`: `edit /etc/nginx/sites-available/grouprise`
    * or remove the `default` nginx site (if it is not in use) in order to let the `grouprise` site be picked irrespective of the requested hostname
* enable the site: `ln -s ../sites-available/grouprise /etc/nginx/sites-enabled/`
* restart nginx: `service nginx restart`
* visit the fresh grouprise instance: `http://localhost/` (or use a suitable hostname)


## Weitere Dienste einrichten

Für einige Funktionen werden weitere Dienste benötigt. Anleitung folgt.
