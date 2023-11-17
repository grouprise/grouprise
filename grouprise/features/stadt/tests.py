import typing

import grouprise.core.tests
from grouprise.features.articles.tests import ArticleMixin
from grouprise.features.gestalten.tests.mixins import GestaltMixin
from grouprise.features.groups.tests.mixins import GroupMixin


class TestUrls(grouprise.core.tests.Test):
    def test_stadt_404(self):
        r = self.client.get(self.get_url("entity", "non-existent"))
        self.assertEqual(r.status_code, 404)


class TestEntityGestaltLinks(GestaltMixin, grouprise.core.tests.RenderingTest):
    def _get_gestalt_link(self, label: typing.Optional[str] = None):
        username = self.gestalt.user.username
        user_pk = self.gestalt.user.pk
        if label is None:
            label = f"@{username}"
        return (
            f"<a"
            f' data-component="gestaltlink"'
            f' href="http://example.com/{username}/"'
            f' data-gestaltlink-ref="{user_pk}"'
            f' title="{username}"'
            f">{label}</a>"
        )

    def test_gestalt_link(self):
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo @{self.gestalt.user.username} bar"),
            f"<p>foo {self._get_gestalt_link()} bar</p>",
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

    def test_unknown_article(self):
        username = self.gestalt.user.username
        user_pk = self.gestalt.user.pk
        bad_content_slug = "nonexistent"
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo @{username}/{bad_content_slug} bar"),
            (
                f'<p>foo <span><span><a data-component="gestaltlink"'
                f' data-gestaltlink-ref="{user_pk}" title="{username}"'
                f' href="http://example.com/test/">@{username}</a></span>/{bad_content_slug}'
                f" (Inhalt nicht gefunden)</span> bar</p>"
            ),
        )


class TestEntityGroupLinks(GroupMixin, grouprise.core.tests.RenderingTest):
    def _get_group_link(self, label: typing.Optional[str] = None):
        if label is None:
            label = f"@{self.group.slug}"
        return (
            f"<a"
            f' data-component="grouplink"'
            f' href="http://example.com/{self.group.slug}/"'
            f' data-grouplink-ref="{self.group.pk}"'
            f' title="{self.group.name}"'
            f">{label}</a>"
        )

    def test_group_link(self):
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo @{self.group.slug} bar"),
            f"<p>foo {self._get_group_link()} bar</p>",
        )

    def test_indirect_group_link(self):
        slug = self.group.slug
        label = f"<span>group {slug}</span>"
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo [group {slug}](@{slug}) bar"),
            f"<p>foo {self._get_group_link(label)} bar</p>",
        )
