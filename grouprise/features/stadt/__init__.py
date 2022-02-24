import re

default_app_config = "grouprise.features.stadt.apps.StadtConfig"
RE_CONTENT_REF = re.compile(r"@([\w\-]+)(?:/([\w\-]+))?")
