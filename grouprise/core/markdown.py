import re

import bleach
import markdown
from markdown import blockprocessors, inlinepatterns, util
from markdown.extensions import nl2br, sane_lists, fenced_code
from mdx_unimoji import UnimojiExtension
from pymdownx import magiclink
from xml.etree import ElementTree


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


class SpacedHashHeaderProcessor(blockprocessors.HashHeaderProcessor):
    # this is exactly the same pattern as the original HashHeaderProcessor
    # except that we require at least one space between the hash
    # and the following header text
    RE = re.compile(r'(^|\n)(?P<level>#{1,6})\s+(?P<header>.*?)#*(\n|$)')


class ExtendedLinkPattern(inlinepatterns.LinkPattern):
    _EXTENSIONS = []

    def _atomize(self, el):
        if el.text and not isinstance(el.text, util.AtomicString):
            el.text = util.AtomicString(self.unescape(el.text))
        for child in el:
            self._atomize(child)

    def _processInline(self, el):
        new_text = markdown.markdown(el.text)
        cleaned_text = bleach.clean(new_text, strip=True, tags=('em', 'strong', 'span'))
        children = ElementTree.fromstring('<span>{}</span>'.format(cleaned_text))
        self._atomize(children)
        result = ElementTree.Element('a', el.attrib)
        result.append(children)
        return result

    def handleMatch(self, m):
        el = super().handleMatch(m)
        for extension in self._EXTENSIONS:
            el = extension.process_link(el)
        return self._processInline(el)

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
        md.parser.blockprocessors['hashheader'] = SpacedHashHeaderProcessor(md.parser)


markdown_extensions = [
    magiclink.MagiclinkExtension(),
    nl2br.Nl2BrExtension(),
    ExtendedLinkExtension(),
    sane_lists.SaneListExtension(),
    fenced_code.FencedCodeExtension(),
    CuddledListExtension(),
    UnimojiExtension()
]

content_allowed_tags = (
    # text
    'p', 'em', 'strong', 'br', 'a', 'img', 'sub', 'sup',
    # citation
    'blockquote', 'cite',
    # headings
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    # lists
    'ol', 'ul', 'li',
    # code
    'pre', 'code'
)

content_allowed_attributes = {
    '*': ['id', 'title'],
    'a': ['href', 'title', 'data-component', 'data-grouplink-ref'],
    'code': ['class'],
    'img': ['src', 'alt']
}
