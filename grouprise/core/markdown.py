import re
from xml.etree import ElementTree

import bleach
import markdown
from markdown import blockprocessors, inlinepatterns, util
from markdown.extensions import fenced_code, nl2br, sane_lists
from mdx_unimoji import UnimojiExtension
from pymdownx import magiclink


class CuddledListProcessor(blockprocessors.BlockProcessor):
    """detect a list even if it is not prefixed by an empty line

    Plain markdown would require an empty line between a paragraph and a list.
    """

    RE = re.compile(r"\n([*+-]|1\.)[ ]")

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        before = block[: m.start()]
        self.parser.parseBlocks(parent, [before])
        after = block[m.start() :]
        self.parser.parseBlocks(parent, [after])


class CuddledListExtension(markdown.Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            CuddledListProcessor(md.parser), "cuddledlist", 100
        )


class SpacedHashHeaderProcessor(blockprocessors.HashHeaderProcessor):
    # this is exactly the same pattern as the original HashHeaderProcessor
    # except that we require at least one space between the hash
    # and the following header text
    RE = re.compile(r"(^|\n)(?P<level>#{1,6})\s+(?P<header>.*?)#*(\n|$)")


class ExtendedLinkPattern(inlinepatterns.LinkInlineProcessor):
    _EXTENSIONS = []

    def _atomize(self, el):
        if el.text and not isinstance(el.text, util.AtomicString):
            el.text = util.AtomicString(self.unescape(el.text))
        for child in el:
            self._atomize(child)

    def _processInline(self, el):
        """render the link text as markdown

        Custom markdown extensions (e.g. group links) are applied via the `process_link` method in
        `self._EXTENSIONS` items.
        """
        new_text = markdown.markdown(el.text)
        cleaned_text = bleach.clean(new_text, strip=True, tags=("em", "strong", "span"))
        children = ElementTree.fromstring("<span>{}</span>".format(cleaned_text))
        self._atomize(children)
        result = ElementTree.Element("a", el.attrib)
        result.append(children)
        return result

    def handleMatch(self, m, data):
        el, start, end = super().handleMatch(m, data)
        if el:
            for extension in self._EXTENSIONS:
                el = extension.process_link(el)
                if el.tag != "a":
                    # One of the extensions changed the data type.
                    # We cannot proceed now, since our extensions expect an 'a' tag.
                    break
            result_tag = self._processInline(el)
        else:
            # somehow the link processor did not find a match (e.g. `foo [bar] baz`)
            result_tag = el
        return (result_tag, start, end)

    @classmethod
    def register_extension(cls, extension):
        cls._EXTENSIONS.append(extension)


class ExtendedLinkExtension(markdown.Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            ExtendedLinkPattern(inlinepatterns.LINK_RE, md), "link", 100
        )
        # replace the original "hashheader" processor
        md.parser.blockprocessors.register(
            SpacedHashHeaderProcessor(md.parser), "hashheader", 100
        )


markdown_extensions = [
    magiclink.MagiclinkExtension(),
    nl2br.Nl2BrExtension(),
    ExtendedLinkExtension(),
    sane_lists.SaneListExtension(),
    fenced_code.FencedCodeExtension(),
    CuddledListExtension(),
    UnimojiExtension(),
]

content_allowed_tags = (
    # text
    "p",
    "em",
    "strong",
    "br",
    "a",
    "img",
    "sub",
    "sup",
    "span",
    # citation
    "blockquote",
    "cite",
    # headings
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    # lists
    "ol",
    "ul",
    "li",
    # code
    "pre",
    "code",
)

content_allowed_attributes = {
    "*": ["id", "title"],
    "a": [
        "class",
        "href",
        "title",
        "data-component",
        "data-gestaltlink-ref",
        "data-grouplink-ref",
        "data-tag-group-key",
    ],
    "span": ["class"],
    "code": ["class"],
    "img": ["src", "alt"],
}
