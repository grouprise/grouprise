import grouprise.core.tests
from grouprise.features.articles.tests import ArticleMixin
from grouprise.features.gestalten.tests.mixins import GestaltMixin
from grouprise.features.groups.tests.mixins import GroupMixin


class TestUrls(grouprise.core.tests.Test):
    def test_stadt_404(self):
        r = self.client.get(self.get_url("entity", "non-existent"))
        self.assertEqual(r.status_code, 404)


class TestEntityGestaltLinks(GestaltMixin, grouprise.core.tests.RenderingTest):
    def test_gestalt_link(self):
        username = self.gestalt.user.username
        user_pk = self.gestalt.user.pk
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo @{username} bar"),
            (
                f'<p>foo <a data-component="gestaltlink" href="http://example.com/{username}/"'
                f' data-gestaltlink-ref="{user_pk}" title="{username}">@{username}</a> bar</p>'
            ),
        )

    def test_unknown_entity(self):
        self.assertHTMLEqual(
            self.get_rendered_markdown("foo @nonexistent bar"),
            """<p>foo <span>@nonexistent (unbekannte Gruppe/Gestalt)</span> bar</p>""",
        )


class TestEntityArticleLinks(ArticleMixin, grouprise.core.tests.RenderingTest):
    ARTICLE_TITLE = "Test-Article"

    def test_article_link(self):
        username = self.gestalt.user.username
        content_slug = self.association.slug
        title = self.association.container.title
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo @{username}/{content_slug} bar"),
            (
                f'<p>foo <a href="http://example.com/{username}/{content_slug}/"'
                f' title="{title}">@{username}/{content_slug}</a> bar</p>'
            ),
        )


class TestEntityGroupLinks(GroupMixin, grouprise.core.tests.RenderingTest):
    def test_group_link(self):
        slug = self.group.slug
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo @{slug} bar"),
            (
                f'<p>foo <a data-component="grouplink" href="http://example.com/{slug}/"'
                f' data-grouplink-ref="{self.group.pk}"'
                f' title="{self.group.name}">@{slug}</a> bar</p>'
            ),
        )

    def test_indirect_group_link(self):
        slug = self.group.slug
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo [group {slug}](@{slug}) bar"),
            (
                f'<p>foo <a data-component="grouplink" href="http://example.com/{slug}/"'
                f' data-grouplink-ref="{self.group.pk}"'
                f' title="{self.group.name}"><span>group {slug}</span></a> bar</p>'
            ),
        )
