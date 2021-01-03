# Installation mittels deb-Paket

Die Installation von grouprise mit Hilfe der deb-Pakete, die wir bereitstellen, dürfte für die
meisten Anwendungen der einfachste Weg sein.


## Pakete installieren

Add the grouprise repository, download its signing key and trust this key for the repository:
Import the grouprise apt repository key and enable it for the grouprise repository:
```shell
mkdir -p /etc/grouprise
touch /etc/grouprise/apt-keyring.gpg
wget -q -O - https://deb.grouprise.org/keys/repository.asc | gpg --no-default-keyring --keyring /etc/grouprise/apt-keyring.gpg --import
echo "deb [signed-by=/etc/grouprise/apt-keyring.gpg] https://deb.grouprise.org/ unstable main" >/etc/apt/sources.list.d/grouprise.list
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

Die Angabe von `LC_COLLATE` und `LC_CTYPE` sind beispielsweise für die korrekte alphabetische Sortierung von Zeichenketten mit Umlauten relevant.
Eventuell musst du zuvor das Locale `de_DE.UTF8` via `dpkg-reconfigure locales` auf dem Datenbank-Host aktivieren (und bei Bedarf den PostgreSQL-Server neustarten).

Trage die Angaben zur Datenbank in `/etc/grouprise/settings.py` ein. Ändere dort auch alle anderen Angaben entsprechend. Ein weiteres Beispiel für eine Deployment-Konfiguration findest du [im Repository](https://git.hack-hro.de/grouprise/grouprise/tree/master/grouprise/settings.py.production).

Anschließend kannst du grouprise zum ersten Mal ausprobieren (`yourhostname.org:8000`):

```bash
grouprisectl runserver 0.0.0.0:8000
```

(Wenn du temporär in den Einstellungen `DEBUG = True` setzt, sieht die Seite auch hübsch aus. Vergiss nicht, die Einstellung zurückzusetzen!)


## UWSGI und Nginx einrichten

Nun musst du grouprise nur noch via Webserver verfügbar machen. Eine UWSGI-Konfiguration ist bereits installiert. Aktiviere sie:
```shell
ln -s ../apps-available/grouprise.ini /etc/uwsgi/apps-enabled/
service uwsgi restart
```

Erzeuge anschließend eine nginx-site-Konfiguration (z.B. `/etc/nginx/sites-available/grouprise`), wobei die Domain anzupassen ist:
```
server {
    server_name example.org;
    include snippets/grouprise.conf;
}
```

Aktiviere diese nginx-site und lade nginx neu:
```shell
ln -s ../sites-available/grouprise /etc/nginx/sites-enabled/
service nginx restart
```

Nun kannst du mit deinem Browser den Webserver besuchen. Herzlichen Glückwunsch!
