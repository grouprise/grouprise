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
    'p', 'em', 'strong', 'br', 'a', 'img',
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
    '*': 'title',
    'a': ['href', 'title', 'data-component', 'data-grouplink-ref'],
    'code': ['class'],
    'img': ['src', 'alt']
}
