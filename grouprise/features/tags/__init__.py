import re

default_app_config = "grouprise.features.tags.apps.TagsConfig"

# we do not allow the slash before the hash - otherwise we could misdetect URL paths as tags
RE_TAG_REF = re.compile(r"(?:^|[^\w/])#(\w+(?:[\w:_-]+\w)?)\b")
