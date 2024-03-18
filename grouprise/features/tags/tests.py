import re

from django.core import mail
from django.urls import reverse
from taggit.models import Tag

from . import RE_TAG_REF
from grouprise.core.tests import RenderingTest, Test
from grouprise.core.tests import get_url
from grouprise.features.associations.models import Association
from grouprise.features.groups.tests.mixins import GroupMixin
from grouprise.features.imports.tests.test_mail import MailInjectLMTPMixin
from grouprise.features.memberships.test_mixins import AuthenticatedMemberMixin


class TaggedGroupMixin(GroupMixin):
    def setUp(self):
        super().setUp()
        self.group.tags.add("test")


class BasicTagTests(AuthenticatedMemberMixin, MailInjectLMTPMixin, Test):
    def test_tag_page_has_group_tag_link(self):
        self.client.get(get_url("tag", "test"))
        # self.assertContainsLink(r, get_url('tag-group', 'test'))

    def test_tag_group_renders_ok(self):
        r = self.client.get(get_url("tag-group", "test"))
        self.assertEqual(r.status_code, 200)

    def test_tag_group_redirects_to_tag_page(self):
        r = self.client.post(
            get_url("tag-group", "test"), data={"group": self.group.id}
        )
        self.assertRedirects(r, get_url("tag", "test"))

    def test_tag_group_tags_group(self):
        self.client.post(get_url("tag-group", "test"), data={"group": self.group.id})
        self.assertTrue(self.group.tags.filter(slug="test").exists())

    def test_receive_conversation_contribution_with_tag_by_mail(self):
        # create incoming mail with tag (#302)
        self.client.post(
            reverse("create-group-conversation", args=(self.group.pk,)),
            {"subject": "Subject", "text": "Text"},
        )
        reply_to = mail.outbox[0].extra_headers["Reply-To"]
        self.inject_mail(self.gestalt.user.email, [reply_to], data="Text with #tag")

    def test_receive_content_contribution_with_tag_by_mail(self):
        # create incoming mail with tag (#302)
        self.client.post(
            reverse("create-group-article", args=(self.group.slug,)),
            {"title": "Test", "text": "Test"},
        )
        reply_to = mail.outbox[0].extra_headers["Reply-To"]
        self.inject_mail(self.gestalt.user.email, [reply_to], data="Text with #tag")

        # check, that tag page contains link to article
        r = self.client.get(reverse("tag", args=("tag",)))
        self.assertContains(
            r,
            'href="{}"'.format(
                Association.objects.get(content__title="Test").get_absolute_url()
            ),
        )


class TagPatternTests(Test):
    def test_text_examples(self):
        for text, expected_tags in (
            ("Lore ipsum #foo bar", ["foo"]),
            ("Lore ipsum #foo, bar", ["foo"]),
            ("Lore ipsum #foo\nbar", ["foo"]),
            ("Lore ipsum\n#foo bar", ["foo"]),
            ("Lore ipsum '#foo' bar", ["foo"]),
            ('Lore ipsum "#foo" bar', ["foo"]),
            ("Lore ipsum (#foo) bar", ["foo"]),
            ("Lore ipsum /#foo/ bar", []),
            ("Lore ipsum #foo. bar", ["foo"]),
            ("Lore ipsum #foo", ["foo"]),
            ("ipsum #foo", ["foo"]),
            ("#foo bar", ["foo"]),
            ("#foo", ["foo"]),
            ("Lore ipsum #foo-12 bar", ["foo-12"]),
            ("Lore ipsum 12-#foo bar", ["foo"]),
            ("Lore ipsum abc-#foo bar", ["foo"]),
            ("Lore ipsum #foo-abc bar", ["foo-abc"]),
            ("Lore ipsum #foo_abc bar", ["foo_abc"]),
            ("Lore ipsum #foo.abc bar", ["foo"]),
            ("Lore ipsum #foo- bar", ["foo"]),
            ("Lore ipsum #foo: bar", ["foo"]),
            ("Lore ipsum #foo_ bar", ["foo_"]),
            ("Lore ipsum 12#foo bar", []),
            ("Lore ipsum abc#foo bar", []),
            ("Lore https://example.org/#foo bar", []),
        ):
            with self.subTest(text=text, expected_tags=expected_tags):
                found_items = re.findall(RE_TAG_REF, text)
                self.assertEqual(expected_tags, found_items)


class TaggedGroupTests(TaggedGroupMixin, AuthenticatedMemberMixin, Test):
    def test_show_settings_page(self):
        r = self.client.get(
            "{}?group={}".format(reverse("group-settings"), self.group.slug)
        )
        self.assertEqual(r.status_code, 200)


class TagRenderingTests(RenderingTest):
    SIMPLE_TAG_HTML = (
        '<a class="tag" href="/stadt/tags/my-simple-tag/" data-tag-slug="my-simple-tag">'
        '<span class="tag-hash">#</span>'
        '<span class="tag-name">my-simple-tag</span>'
        "</a>"
    )
    GROUP_TAG_HTML = (
        '<a class="tag" href="/stadt/tags/newyearresolutionbekind/" data-tag-slug="newyearresolutionbekind" data-tag-group-key="newyearresolution">'  # noqa: E501
        '<span class="tag-group">'
        '<span class="tag-hash">#</span>NewYearResolution:'
        "</span>"
        '<span class="tag-name">BeKind</span>'
        "</a>"
    )

    def _render_tag_template(self, tag: Tag):
        return self.get_rendered_raw("{% tag my_tag %}", {"my_tag": tag})

    def test_render_simple_tag(self):
        tag = Tag.objects.create(name="my-simple-tag")
        self.assertHTMLEqual(self._render_tag_template(tag), self.SIMPLE_TAG_HTML)
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"#{tag.name}"),
            f"<p>{self.SIMPLE_TAG_HTML}</p>",
        )

    def test_render_group_tag(self):
        tag = Tag.objects.create(name="NewYearResolution:BeKind")
        self.assertHTMLEqual(self._render_tag_template(tag), self.GROUP_TAG_HTML)
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"#{tag.name}"),
            f"<p>{self.GROUP_TAG_HTML}</p>",
        )

    def test_unknown_tags_in_markdown_do_not_raise(self):
        tag_name = "ThisTagDoesNotExistYet"
        # Make sure this tag does not exist so the actual test is worthwhile.
        with self.assertRaises(Tag.DoesNotExist):
            Tag.objects.get(name=tag_name)
        try:
            self.get_rendered_markdown(f"#{tag_name}")
        except Tag.DoesNotExist:
            self.fail("Unknown tags in markdown should not raise exceptions.")

    def test_tags_in_markdown_are_case_insensitive_but_retain_custom_casing(self):
        """We want to ensure that authors using tags in markdown have full authorship control
        meaning we don’t apply seemingly arbitrary transformation.
        In essence: both "#MyTag" and "#mytag" should point to the same tag, but
        should be rendered the way the author has written them.
        """
        name_1 = "ThIsTAgHAsWEIrdCAsIng"
        name_2 = "THiSTaGHaSWeiRDCaSiNG"
        tag = Tag.objects.create(name=name_1)
        tag_url = reverse("tag", args=[tag.slug])
        markdown_html = self.get_rendered_markdown(f"#{name_2}")
        self.assertIn(name_2, markdown_html)
        self.assertIn(f'href="{tag_url}"', markdown_html)

    def test_indirect_tag_link(self):
        tag = Tag.objects.create(name="foo")
        slug = tag.slug
        self.assertHTMLEqual(
            self.get_rendered_markdown(f"foo [tag {slug}](#{slug}) bar"),
            f'<p>foo <a href="/stadt/tags/{slug}/"><span>tag {slug}</span></a> bar</p>',
        )
