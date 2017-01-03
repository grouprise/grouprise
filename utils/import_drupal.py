#!/usr/bin/env python3

"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.


Dump-Quellen:

  dump=/tmp/image.txt; rm -f "$dump"
  echo "select image.nid, files.fid, files.filepath
        from image, files where image.fid = files.fid
        INTO OUTFILE '$dump' FIELDS TERMINATED BY ',';" | mysql drupal_stadtgest
"""

from __future__ import print_function

import os
import re
import csv
import sys
import pytz
import datetime
import io
import socket
import urllib
from html.parser import HTMLParser
from django.db import IntegrityError
from django.conf import settings


# DEFAULT_TIMEZONE = pytz.timezone("UTC")
DEFAULT_TIMEZONE = pytz.timezone("Europe/Berlin")
DEFAULT_TIMESTAMP = datetime.datetime(year=2000, month=1, day=1, tzinfo=DEFAULT_TIMEZONE)
# fuer Bild-Importe
DRUPAL_SITE_BASE = "/data/drupal"
# die aktuelle und die urspruengliche URL koennen abweichen
# (Texte in der Datenbank vs. aktuelle Erreichbarkeit)
DRUPAL_SITE_URL_ORIGINAL = "http://stadtgestalten.org"
DRUPAL_SITE_URL = "http://stadtgestalten.org"

DUMP_FILES_BASE_DIR = os.path.expanduser("~/dump")
DUMP_FILE_NODE_REVISIONS = os.path.join(DUMP_FILES_BASE_DIR, "node_revisions.txt")
DUMP_FILE_NODES = os.path.join(DUMP_FILES_BASE_DIR, "node.txt")
DUMP_FILE_IMAGES = os.path.join(DUMP_FILES_BASE_DIR, "image.txt")
DUMP_FILE_FILES = os.path.join(DUMP_FILES_BASE_DIR, "files.txt")

NODE_FIELDNAMES = (
        "nid", "vid", "type", "language", "title", "uid", "status",
        "created", "changed", "comment", "promote", "moderate", "sticky",
        "tnid", "translate")
NODE_REVISION_FIELDNAMES = (
        "nid", "vid", "uid", "title", "body", "teaser",
        "log", "timestamp", "format")
IGNORE_NODE_IDS = (737, 1389, 1390, 1394, 1395)
IMAGE_FIELDNAMES = ("nid", "file_id", "local_name")
FILE_FIELDNAMES = ("file_id", "uid", "local_name", "path", "mime", "size", "status", "timestamp")
NEW_USER_DEFAULT_PASSWORD = 'Eehuyaish0aikee7CohngeeVohbaezai'
USERNAME_INVALID_REGEX = re.compile(r"[^a-zA-Z0-9-_\.]")
TEASER_LENGTH = 256
SITE_DOMAIN = "stadtgestalten.org"

THUMBNAIL_ARTICLE = "article_image"
ENCODING = "utf8"


def _convert_dict_values(dict_obj, keys, converter):
    for key in keys:
        dict_obj[key] = converter(dict_obj[key])


def _strip_dict_values(dict_obj, keys):
    for key in keys:
        dict_obj[key] = dict_obj[key].strip(r'\N').strip()


def get_import_user():
    from entities.models import Gestalt
    return Gestalt.objects.get(user=Gestalt.user.field.related_model.objects.get(
        username="hafasel"))


class TeaserTruncateParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        try:
            self._level_counter += 1
        except AttributeError:
            self._level_counter = 1

    def handle_endtag(self, tag):
        try:
            self._level_counter -= 1
        except AttributeError:
            self._level_counter = 0
        if self._level_counter == 0:
            # drei Zeichen extra fuer die Klammern des schliessenden Tags
            position = self.getpos()[1] + len(tag) + 3
            try:
                self._level_even.append(position)
            except AttributeError:
                self._level_even = [position]


def _truncate_teaser(body, teaser, target_length):
    max_factor = 1.2
    get_max = lambda items, maximum: max([item for item in items if item < maximum])  # NOQA: E731
    if not teaser:
        teaser = body
    if len(teaser) > max_factor * target_length:
        parser = TeaserTruncateParser()
        input_text = "".join(body.splitlines())
        parser.feed(input_text)
        even_list = getattr(parser, "_level_even", [])
        try:
            max_length = get_max(even_list, target_length)
        except ValueError:
            try:
                max_length = get_max(even_list, max_factor * target_length)
            except ValueError:
                max_length = 0
        teaser = input_text[:max_length]
    return teaser


def _full_name(name):
    ''' TODO:
        - Umlaute und andere Sonderzeichen ordentlich behandeln
          (aktuell gelten sie fuer "title" als whitespace und fuehren zu unnoetigen
          Grossbuchstaben)
    '''
    name = name.title()
    tokens = name.split()
    if len(tokens) > 1:
        first_name = " ".join(tokens[:-1])
        last_name = tokens[-1]
    else:
        first_name = name
        last_name = ""
    return first_name, last_name


def _get_clean_username(username):
    """ Sonderzeichen aus Nutzernamen entfernen """
    return USERNAME_INVALID_REGEX.sub("_", username)


def clear_db():
    return
    from entities.models import GestaltContent
    from django.contrib.sites.models import Site
    from entities.models import Gestalt as Author
    from django.contrib.auth.models import Group
    from locations.models import EventLocation
    for item_class in (GestaltContent, Author, Group, EventLocation, Site):
        # User-Loeschung klappt gerade nicht: no such table: userena_userenasignup
        if item_class is Author:
            continue
        for item in item_class.objects.iterator():
            item.delete()


def get_revisions(filename=DUMP_FILE_NODE_REVISIONS):
    revisions = {}
    for rev in csv.DictReader(
            open(filename), fieldnames=NODE_REVISION_FIELDNAMES,
            escapechar="\\"):
        _convert_dict_values(rev, ("nid", "vid", "uid"), int)
        # _convert_dict_values(rev, ("teaser", "body"), lambda text: text.decode(ENCODING))
        rev["teaser"] = _truncate_teaser(rev["body"], rev["teaser"], TEASER_LENGTH)
        rev["text_replacements"] = []
        revisions[rev["nid"], rev["vid"]] = rev
    return revisions


def epoch2time(epoch):
    return datetime.datetime.fromtimestamp(int(epoch), tz=DEFAULT_TIMEZONE)


def get_nodes(filename=DUMP_FILE_NODES):
    posts = Nodes()
    content = open(filename, "rb").read().decode(ENCODING)
    # Seltsame Zeilenumbruchsmaskierungen entfernen
    content = content.replace('\r\\', '')
    for post in csv.DictReader(
            io.StringIO(content),
            fieldnames=NODE_FIELDNAMES, dialect="excel", strict=True,
            escapechar="\\"):
        try:
            if post["type"] == "blog":
                _convert_dict_values(post, ("nid", "vid", "uid"), int)
                _convert_dict_values(post, ("changed", "created"), epoch2time)
                if not post["nid"] in IGNORE_NODE_IDS:
                    posts.append(post)
        except KeyError:
            print(post)
            sys.exit(1)
    return posts


def get_files(filename=DUMP_FILE_FILES):
    files = {}
    for row in csv.DictReader(open(filename), fieldnames=FILE_FIELDNAMES):
        _convert_dict_values(row, ("file_id", "uid", "size", "status"), int)
        _convert_dict_values(row, ("timestamp", ), epoch2time)
        # _convert_dict_values(row, ("local_name", "path", "mime"),
        # lambda text: text.decode(ENCODING))
        files[row["file_id"]] = row
    return files


def get_images(files, nodes, revisions, filename=DUMP_FILE_IMAGES):
    images_dict = {}
    for row in csv.DictReader(open(filename), fieldnames=IMAGE_FIELDNAMES):
        _convert_dict_values(row, ("nid", "file_id"), int)
        # _convert_dict_values(row, ("local_name", ), lambda text: text.decode(ENCODING))
        row["image"] = files[row["file_id"]]
        images_dict[row["nid"]] = row

    def url_cleaner(url):
        # maps = [
        #    ("/Freiraum.tut_.gut_.jpg", "/Freiraum.tut_.gut_.preview.jpg"),
        #    ("/rathausbrand1.img_assist_properties.jpg", "/rathausbrand1.preview.jpg"),
        #    ("/rathausbrand2.img_assist_properties.jpg", "/rathausbrand2.preview.jpg"),
        #    ("/sement-tun-sein.jpg", "/sement-tun-sein.preview.jpg"),
        #    ("/homer.jpg", "/homer.preview.jpg"),
        #  ("/stadtgestalten_treffen_juni_2010", "/stadtgestalten_treffen_juni_2010.preview.jpg"),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        #    ("", ""),
        # ]
        dot_split = url.split(u".")
        if (len(dot_split) > 2) and (dot_split[-2] in ("thumbnail", "preview")):
            dot_split.pop(-2)
            url = u".".join(dot_split)
        url = url.replace("http://stadtgestalten.org/", "http://geschichte.stadtgestalten.org/")
        url = re.sub(r"\.(jpeg|JPG)$", r".jpg", url)
        url = re.sub(r"/(IMG_[^/]+)(\.jpg)$", r"/\1.preview.\2", url)
        # url = re.sub(
        # r"(sites/stadtgestalten.org/files/images)/([^/]+).(jpg|JPG|png)",
        # r"\1/\2.preview.\3", url)
        url = url[:6] + urllib.parse.quote(url[6:].encode("utf-8"))
        # irgendwie tauchen mehrfache Prozent-Escaper auf
        url = url.replace("%2525", "%")
        return url

    def get_url_with_retry(url, retry=2):
        url = url_cleaner(url)
        try:
            return urllib.request.urlopen(url, timeout=5).read()
        except (urllib.error.URLError, socket.timeout) as err:
            if retry <= 0:
                print("Skipped broken URL: %s" % str(url), file=sys.stderr)
                return None
            else:
                return get_url_with_retry(url, retry - 1)

    def get_img_assistant_obj(nid=None, title=None, description=None):
        # image assistant: [img_assist|nid=1603|title=Aneignung_Beispiel-3_201311|
        # desc=|link=none|align=left|width=440|height=329]
        result = {}
        if title:
            result["title"] = title
        if description:
            result["description"] = description
        nid = int(nid)
        if nid not in images_dict:
            print(images_dict.keys())
        path = images_dict[nid]["image"]["path"]
        if not path.startswith("/"):
            fullpath = os.path.join(DRUPAL_SITE_BASE, path)
        else:
            fullpath = path
        # in Umgebungen ohne utf-8-locale scheint diese Forcierung erforderlich zu sein
        fullpath = fullpath.encode("utf-8")
        if os.path.isfile(fullpath):
            data = file(path, "rb").read()  # NOQA: F821
        else:
            url = "%s/%s" % (DRUPAL_SITE_URL.rstrip("/"), path.lstrip("/"))
            data = get_url_with_retry(url)
        result["data"] = data
        result["timestamp"] = images_dict[nid]["image"]["timestamp"]
        result["author"] = get_import_user()
        return result

    def get_url_obj(url=None):
        # ein paar URLs haben fuehrende Leerzeichen (html-escaped)
        url = urllib.parse.unquote(url).strip()
        if url.startswith("/"):
            url = DRUPAL_SITE_URL.rstrip("/") + url
        data = get_url_with_retry(url)
        return {"data": data}

    # Bild-Import
    image_assistant_regex = (
            r"\[img_assist\|nid=(?P<nid>[0-9]+)(?:\|"
            r"title=(?P<title>[^\|]+))?(?:\|desc=(?P<description>[^\|]+))?[^\]]*\]")
    # nur lokale Bilder
    image_url_regex = (
            r"<img[^>]*src=\"(?P<url>(?:%s)?[^\"]+\.(?:jpg|jpeg|gif|png))\"[^>]*(?:/>|</img>)"
            % DRUPAL_SITE_URL_ORIGINAL.rstrip("/"))
    parsers = ((re.compile(image_assistant_regex, flags=re.IGNORECASE), get_img_assistant_obj),
               (re.compile(image_url_regex, flags=re.IGNORECASE), get_url_obj))
    images = Images()
    for node in nodes:
        try:
            revision = revisions[node["nid"], node["vid"]]
        except KeyError:
            print("Skipped: %s" % str(node), file=sys.stderr)
            continue
        text = revision["body"]
        for parser_regex, parser_func in parsers:
            for match in re.finditer(parser_regex, text):
                text_match = text[match.start():match.end()]
                image = parser_func(**match.groupdict())
                if image:
                    image["post_nid"] = node["nid"]
                    image["post_vid"] = node["vid"]
                    image["text_match"] = text_match
                    images.append(image)
    return images


class MultiIndexList(list):

    def get_by(self, key, value):
        for item in self:
            if item[key] == value:
                yield item

    def get_first_by(self, key, value):
        for item in self.get_by(key, value):
            return item
        else:
            return None


class Places(MultiIndexList):

    def export_to_django(self):
        from locations.models import EventLocation
        for item in self:
            try:
                place = EventLocation(title=item["title"])
                place.geom = "POINT(%f %f)" % (item["latitude"], item["longitude"])
                place.website = item["url"]
                place.content = str(item["attributes"])
                place.save()
            except IntegrityError as msg:
                print(
                        "Ort '%s' (node %d) fehlgeschlagen: %s" % (
                            item["title"], item["nid"], msg),
                        file=sys.stderr)


class Nodes(MultiIndexList):

    def export_posts_to_django(self, revisions):
        from entities.models import GestaltContent
        from content.models import Article
        from django.template.defaultfilters import slugify

        substitute_maps = [(
            re.compile(pattern, re.IGNORECASE), template) for pattern, template in (
                (
                    r"""<a [^>]*href="(?P<url>[^"]+)"[^>]*>(?P<label>[^<]+)</a>""",
                    r"""[\g<label>](\g<url>)"""),
                (
                    r"""<img [^>]*src="(?P<url>[^"]+)"[^>]*alt="(?P<label>[^"]+)"[^>]*>""",
                    r"""![\g<label>](\g<url>)"""),
                (r"""<img [^>]*src="(?P<url>[^"]+)"[^>]*>""", r"""![Bild](\g<url>)"""),
                (r"http://stadtgestalten\.org/", "http://geschichte.stadtgestalten.org/"),
                (r"<p><!--break--></p>", ""),
                (r"<p>", ""),
                (r"</p>", "\n\n"),
            )]

        # site_id = get_or_create_site()

        def update_post(post):
            user = get_import_user()
            slug = slugify(post["title"])
            try:
                GestaltContent.objects.get(content__slug=slug).delete()
            except GestaltContent.objects.model.DoesNotExist:
                pass
            # es mag auch Fragmente von Content ohne ein GestaltContent-Objekt geben
            try:
                Article.objects.get(slug=slug).delete()
            except Article.objects.model.DoesNotExist:
                pass
            try:
                revision = revisions[post["nid"], post["vid"]]
            except KeyError:
                print("Passende Revision nicht gefunden: %d, %d" % (post["nid"], post["vid"]))
                return
            substituted_text = revision["body"]
            for pattern, template in substitute_maps:
                substituted_text = pattern.sub(template, substituted_text)
            for before, after in revision["text_replacements"]:
                substituted_text = substituted_text.replace(before, after)
            content = Article.objects.create(title=post["title"], text=substituted_text,
                                             date_created=post["created"], slug=slug,
                                             author=user, public=True)
            # content.save()
            # entry = GestaltContent(content=content, gestalt=user)
            # entry.save()
            revisions[post["nid"], post["vid"]]["django_content"] = content
        for item in self:
            try:
                update_post(item)
            except IntegrityError as msg:
                print("Post #%d (revision %d) fehlgeschlagen: %s" % (
                            item["nid"], item["vid"], msg), file=sys.stderr)
                break


class Images(MultiIndexList):

    def export_images_to_django(self, revisions):
        from content.models import Image
        for item in self:
            data = io.BytesIO(item["data"])
            if not data:
                print("Konnte Bild <%s> nicht laden - es ist leer." % str(item), file=sys.stderr)
                continue
            post = revisions[(item["post_nid"], item["post_vid"])]
            image = Image()
            image.title = item.get("title", "")
            image.description = item.get("description", "")
            image.owner = get_import_user()
            timestamp = item.get("timestamp", DEFAULT_TIMESTAMP)
            image.uploaded_at = timestamp
            image.modified_at = timestamp
            image.content = post["django_content"]
            image.save()
            # "save" erwartet ein Attribut "size"
            data.size = len(data.getvalue())
            image.file.save("foo", data)
            # TODO: Link auf ein thumbnail?
            html_snippet = ((
                    """<img src="{0}" alt="{1}" title="{2}" class="image_article" """
                    """style="max-width:70%"/>""")
                    .format(image.file.url, image.description, image.title))
            post["text_replacements"].append((item["text_match"], html_snippet))


def get_or_create_site():
    # unsere Domain finden
    from django.contrib.sites.models import Site
    for site in Site.objects.all():
        if site.domain == SITE_DOMAIN:
            break
    else:
        # ... oder unsere Domain erzeugen
        site = Site.objects.create()
        site.name = SITE_DOMAIN
        site.domain = SITE_DOMAIN
        site.save()
        print("CREATING A NEW SITE: %s" % str(site), file=sys.stderr)
    # seit Django 1.7 muss die SITE_ID zwangsweise korrekt sein
    settings.SITE_ID = site.id
    return site.id


def run_import():
    # Vorbereitung der django-Umgebung - sonst schlaegt der Author-Modul-Import fehl
    clear_db()
    # Daten einlesen
    get_or_create_site()
    files = get_files()
    revisions = get_revisions()
    nodes = get_nodes()
    # Django-Export
    # Bilder muessen vor den nodes importiert werden, da die nodes-Texte sich aendern
    images = get_images(files, nodes, revisions)
    nodes.export_posts_to_django(revisions)
    images.export_images_to_django(revisions)
