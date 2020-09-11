# grouprise Deployment mit deb-Paket (Version 2.4.x)

Idealerweise kannst du grouprise via deb-Paket installieren.


## Abhängigkeiten installieren

Folgende Software wird benötigt:

* `python3`
* `pip`
* `virtualenv`
* `nodejs`

Ein passendes DBMS, wir empfehlen `postgresql` mit Python-Bindings (`python3-psycopg2`).

Außerdem verwenden wir in dieser Anleitung eine Konfiguration mit UWSGI und Nginx:

* `uwsgi`
* `uwsgi-plugin-python3`
* `nginx`

Für einige Funktionen von grouprise wird weitere Software benötigt:

* `python3-xapian` (für die Suchfunktion)


## grouprise installieren

Die aktuellen Grouprise-deb-Pakete sind in folgendem Repository zu finden:
```
deb https://deb.grouprise.org/ unstable main
```

Falls das Basis-System *Debian Buster* ist, sind zur Erfüllung aller Abhängigkeiten einige wenige
*backports*-Pakete erforderlich.  Diese sind über die folgende Quelle zugänglich:

```
deb http://deb.debian.org/debian buster-backports main
```


## Datenbank einrichten

Falls du PostgreSQL verwendest, helfen dir die folgenden Zeilen beim Einrichten der Datenbank (`sudo -u postgres psql`):

```sql
CREATE USER grouprise WITH PASSWORD 'xxxxx';
CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;
```

(Dafür muss das Locale `de_DE.UTF8` für PostgreSQL installiert sein.)

Trage die Angaben zur Datenbank in `/etc/stadtgestalten/settings.py` ein. Ändere dort auch alle anderen Angaben entsprechend. Ein weiteres Beispiel für eine Deployment-Konfiguration findest du [im Repository](https://git.hack-hro.de/stadtgestalten/stadtgestalten/tree/master/docs/deployment/settings.py).

Anschließend kannst du grouprise zum ersten Mal ausprobieren (`yourhostname.org:8000`):

```bash
stadtctl runserver 0.0.0.0:8000
```

(Wenn du in den Einstellungen `DEBUG = True` setzt, sieht die Seite auch hübsch aus. Vergiss nicht, die Einstellung zurückzusetzen!)


## UWSGI und Nginx einrichten

Nun musst du grouprise nur noch via Webserver verfügbar machen. Eine UWSGI-Konfiguration ist bereits installiert. Aktiviere sie mit `ln -s ../apps-available/stadtgestalten.ini /etc/uwsgi/apps-enabled`. Nun kannst du UWSGI mit `service uwsgi restart` neustarten.

Kopiere anschließend die Datei `/usr/share/doc/stadtgestalten/examples/nginx.conf` nach `/etc/nginx/sites-available/stadtgestalten`. Passe den Hostnamen an. Nun nur noch die Konfiguration aktivieren (`ln -s ../sites-available/stadtgestalten /etc/nginx/sites-enabled/stadtgestalten`) und den Webserver neustarten (`service nginx restart`). Yeah!


## Weitere Dienste einrichten

Für einige Funktionen werden weitere Dienste benötigt. Anleitung folgt.
