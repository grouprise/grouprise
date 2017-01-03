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
import markdown
from markdown import blockprocessors, inlinepatterns


class CuddledListProcessor(blockprocessors.BlockProcessor):
    RE = re.compile(r'\n([*+-]|1\.)[ ]')

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        before = block[:m.start()]
        self.parser.parseBlocks(parent, [before])
        after = block[m.start():]
        self.parser.parseBlocks(parent, [after])


class CuddledListExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add(
                'cuddledlist', CuddledListProcessor(md.parser), '<paragraph')


class ExtendedLinkPattern(inlinepatterns.LinkPattern):
    _EXTENSIONS = []

    def __init__(self, pattern, markdown_instance=None):
        super().__init__(pattern, markdown_instance)

    def handleMatch(self, m):
        el = super().handleMatch(m)
        for extension in self._EXTENSIONS:
            el = extension.process_link(el)
        return el

    # in order to avoid any tampering with the original implementation
    # of LinkPattern we use sanitize_url to provide us with special
    # group url that we use to pass around group information
    def sanitize_url(self, url):
        for extension in self._EXTENSIONS:
            new_url = extension.process_url(url)
            if new_url:
                return new_url

        return super().sanitize_url(url)

    @classmethod
    def register_extension(cls, extension):
        cls._EXTENSIONS.append(extension)


class ExtendedLinkExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['link'] = ExtendedLinkPattern(inlinepatterns.LINK_RE, md)
