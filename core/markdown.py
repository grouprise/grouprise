from markdown.extensions import nl2br, sane_lists, fenced_code
from pymdownx import magiclink
from mdx_unimoji import UnimojiExtension
import utils.markdown

markdown_extensions = [
    magiclink.MagiclinkExtension(),
    nl2br.Nl2BrExtension(),
    utils.markdown.ExtendedLinkExtension(),
    sane_lists.SaneListExtension(),
    fenced_code.FencedCodeExtension(),
    utils.markdown.CuddledListExtension(),
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
