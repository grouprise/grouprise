import re
import markdown
from features.groups import models as groups
from markdown import blockprocessors, inlinepatterns

RE_GROUP_REF = r'@([a-zA-Z_-]+)'


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


class GroupReferencePattern(inlinepatterns.ReferencePattern):
    def handleMatch(self, m):
        slug = m.group(2)
        try:
            group = groups.Group.objects.get(slug=slug)
        except groups.Group.DoesNotExist:
            return None
        return self.makeTag(group.get_absolute_url(), None, str(group))


class GroupReferenceExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['group_reference'] = GroupReferencePattern(RE_GROUP_REF, md)
