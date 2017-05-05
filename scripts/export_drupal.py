#!/usr/bin/python3
"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

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
"""


import csv
import mysql.connector
import os

DB_LOGIN = {
    "host": "database",
    "database": "drupal_stadtgest",
    "user": "drupal_stadtgest",
    "password": "bHXPtAKV9ye9aRct",
}

DUMP_FILES_BASE_DIR = os.path.expanduser("~/dump")
DUMP_FILE_USERS = os.path.join(DUMP_FILES_BASE_DIR, "users.txt")
DUMP_FILE_NODE_REVISIONS = os.path.join(DUMP_FILES_BASE_DIR, "node_revisions.txt")
DUMP_FILE_NODES = os.path.join(DUMP_FILES_BASE_DIR, "node.txt")
DUMP_FILE_IMAGES = os.path.join(DUMP_FILES_BASE_DIR, "image.txt")
DUMP_FILE_FILES = os.path.join(DUMP_FILES_BASE_DIR, "files.txt")
DUMP_FILE_PLACES = os.path.join(DUMP_FILES_BASE_DIR, "content_type_ort.txt")

NODE_FIELDNAMES = (
        "nid", "vid", "type", "language", "title", "uid", "status",
        "created", "changed", "comment", "promote", "moderate", "sticky",
        "tnid", "translate")
NODE_REVISION_FIELDNAMES = (
        "nid", "vid", "uid", "title", "body", "teaser",
        "log", "timestamp", "format")
USER_FIELDNAMES = ("uid", "name", "pass", "mail")
IMAGE_FIELDNAMES = ("nid", "fid", "image_size")
FILE_FIELDNAMES = (
        "fid", "uid", "filename", "filepath", "filemime", "filesize", "status", "timestamp")
PLACE_FIELDNAMES = ("vid", "nid", "longitude", "latitude", "url", "title", "attributes")


if __name__ == "__main__":
    cnx = mysql.connector.connect(**DB_LOGIN)
    cursor = cnx.cursor()
    # TODO: "images" fehlt (join aus "files" und "image")
    for fname, table, fields, condition in (
            (DUMP_FILE_USERS, "users", USER_FIELDNAMES, None),
            (DUMP_FILE_NODES, "node", NODE_FIELDNAMES, "type='blog'"),
            (DUMP_FILE_NODE_REVISIONS, "node_revisions", NODE_REVISION_FIELDNAMES, None),
            (DUMP_FILE_FILES, "files", FILE_FIELDNAMES, None)):
        with open(fname, "w") as target_file:
            target = csv.writer(target_file, delimiter=",")
            if condition:
                query = "SELECT {0} FROM {1} WHERE {2}".format(", ".join(fields), table, condition)
            else:
                query = "SELECT {0} FROM {1}".format(", ".join(fields), table)
            cursor.execute(query)
            for item in cursor:
                target.writerow(item)
    cnx.close()
