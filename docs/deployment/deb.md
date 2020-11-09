# Installation mittels deb-Paket

Die Installation von grouprise mit Hilfe der deb-Pakete, die wir bereitstellen, dürfte für die
meisten Anwendungen der einfachste Weg sein.


## Pakete installieren

Die aktuellen Grouprise-deb-Pakete sind in folgendem Repository zu finden:
```shell
deb https://deb.grouprise.org/ unstable main
```

Die obige Zeile kannst du in `/etc/apt/sources.list` eintragen.

Importiere anschließend den Repository-Schlüssel in deinen lokalen apt-Schlüsselring:
```shell
wget -O /etc/apt/trusted.gpg.d/deb.grouprise.org.asc https://deb.grouprise.org/keys/repository.asc
```

Nun kannst du den Paketindex via `apt update` aktualisieren.

Falls das Basis-System *Debian Buster* ist, sind zur Erfüllung aller Abhängigkeiten einige wenige
*backports*-Pakete erforderlich.  Diese sind in der folgende Quelle zugänglich:

```shell
deb http://deb.debian.org/debian buster-backports main
```

Pakete installieren:
```shell
apt install grouprise python3-django/buster-backports python3-django-filters/buster-backports
```



## Datenbank einrichten

Falls du PostgreSQL verwendest, helfen dir die folgenden Zeilen beim Einrichten der Datenbank (`sudo -u postgres psql`):

```sql
CREATE USER grouprise WITH PASSWORD 'xxxxx';
CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;
```

Eventuell musst du zuvor das Locale `de_DE.UTF8` aktivieren: `dpkg-reconfigure locales`.

Trage die Angaben zur Datenbank in `/etc/grouprise/settings.py` ein. Ändere dort auch alle anderen Angaben entsprechend. Ein weiteres Beispiel für eine Deployment-Konfiguration findest du [im Repository](https://git.hack-hro.de/stadtgestalten/stadtgestalten/tree/master/grouprise/settings.py.production).

Anschließend kannst du grouprise zum ersten Mal ausprobieren (`yourhostname.org:8000`):

```bash
stadtctl runserver 0.0.0.0:8000
```

(Wenn du temporär in den Einstellungen `DEBUG = True` setzt, sieht die Seite auch hübsch aus. Vergiss nicht, die Einstellung zurückzusetzen!)


## UWSGI und Nginx einrichten

Nun musst du grouprise nur noch via Webserver verfügbar machen. Eine UWSGI-Konfiguration ist bereits installiert. Aktiviere sie mit `ln -s ../apps-available/stadtgestalten.ini /etc/uwsgi/apps-enabled`. Nun kannst du UWSGI mit `service uwsgi restart` neustarten.

Kopiere anschließend die Datei `/usr/share/doc/stadtgestalten/examples/nginx.conf` nach `/etc/nginx/sites-available/stadtgestalten`. Passe den Hostnamen an. Nun nur noch die Konfiguration aktivieren (`ln -s ../sites-available/stadtgestalten /etc/nginx/sites-enabled/stadtgestalten`) und den Webserver neustarten (`service nginx restart`). Yeah!
