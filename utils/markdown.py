from features.groups import models as groups
import markdown
from markdown import inlinepatterns

RE_GROUP_REF = r'@([a-zA-Z_-]+)'


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
