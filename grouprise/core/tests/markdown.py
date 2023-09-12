from . import RenderingTest


class CoreRenderingTest(RenderingTest):
    EXAMPLE_TAG_HTML = """
        <a class="tag" href="/stadt/tags/foo/">
          <span class="tag-hash">#</span>
          <span class="tag-name">foo</span>
        </a>
    """

    def test_hash_header(self):
        self.assertHTMLEqual(
            self.get_rendered_markdown("# foo"),
            """<h1 id="foo">foo</h1>""",
        )
        # vanilla markdown would render "#foo" as a first level heading, but for us it is a tag
        self.assertHTMLEqual(
            self.get_rendered_markdown("#foo"),
            f"""<p>{self.EXAMPLE_TAG_HTML}</p>""",
        )

    def test_cuddled_list(self):
        """our CuddledListExtension detects a list even if it is not prefixed by an empty line"""
        self.assertHTMLEqual(
            self.get_rendered_markdown("Text:\n- foo\n- bar"),
            """<p>Text:</p><ul><li><p>foo</p></li><li><p>bar</p></li></ul>""",
        )

    def test_email_links(self):
        """detect email addresses and render them as mailto (done by Magiclink)"""
        self.assertHTMLEqual(
            self.get_rendered_markdown("foo joe@example.org bar"),
            """<p>foo <a href="mailto:joe@example.org">joe@example.org</a> bar</p>""",
        )

    def test_weird_input(self):
        for md_input, html_output in (("foo [bar] baz", """<p>foo [bar] baz</p>"""),):
            with self.subTest(md_input=md_input):
                self.assertHTMLEqual(self.get_rendered_markdown(md_input), html_output)
