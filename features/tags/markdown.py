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
"""

import re
from django.core import urlresolvers
from markdown import inlinepatterns, Extension
from core.markdown import markdown_extensions
from utils.markdown import ExtendedLinkPattern
from .models import Tag
from . import RE_TAG_REF


class TagLinkExtension:
    def process_url(self, url):
        match = re.match(RE_TAG_REF, url)
        if match:
            tag_name = match.group(1)
            tag_slug = Tag.slugify(tag_name)
            return urlresolvers.reverse('tag', args=[tag_slug])

    def process_link(self, a):
        return a


class TagReferencePattern(inlinepatterns.ReferencePattern):
    def handleMatch(self, m):
        name = m.group(2)
        slug = Tag.slugify(name)
        return self.makeTag(urlresolvers.reverse('tag', args=[slug]), None, '#%s' % name)


class TagReferenceExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['tag_reference'] = TagReferencePattern(RE_TAG_REF, md)


ExtendedLinkPattern.register_extension(TagLinkExtension())
markdown_extensions.append(TagReferenceExtension())
