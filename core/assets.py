import hashlib
import base64
import re
from urllib.parse import urlparse, urlencode, parse_qsl
from django.http.response import HttpResponse
from django.templatetags.static import static
from django.utils.functional import cached_property

_ASSETS = []
_CSP_DIRECTIVES = []


def _build_url(urlparsedict, origin_only=False):
    result = ''

    if urlparsedict['scheme']:
        result += urlparsedict['scheme'] + ':'
    if urlparsedict['netloc']:
        result += '//' + urlparsedict['netloc']

    if not origin_only:
        if urlparsedict['path']:
            result += urlparsedict['path']
        if urlparsedict['params']:
            result += ';' + urlparsedict['params']
        if urlparsedict['query']:
            result += '?' + urlparsedict['query']
        if urlparsedict['fragment']:
            result += '#' + urlparsedict['fragment']

    return result


def _urlparse_to_dict(parsed_url):
    return dict(zip(
        ('scheme', 'netloc', 'path', 'params', 'query', 'fragment'),
        tuple(parsed_url)
    ))


def _dict_to_xmlattributes(data: dict):
    result = ''
    for name, value in data.items():
        result += ' {name}="{value}"'.format(name=name, value=value)
    return result


def _is_absolute(src):
    return bool(re.match(r'^https?://', src))


def _clean_source(src):
    if _is_absolute(src):
        return src
    else:
        url = _urlparse_to_dict(urlparse(static(src)))
        qs = parse_qsl(url['query'])
        url['query'] = urlencode(qs)
        return _build_url(url)


class Asset:
    def __init__(self, stage):
        if stage not in ('early', 'late'):
            raise ValueError('invalid stage "%s". should be "early" or "late"' % stage)
        self.stage = stage


class CSPDirectiveItem:
    def __init__(self, directive, value):
        self.directive = directive
        self.value = value

    @staticmethod
    def script(value):
        return CSPDirectiveItem('script-src', value)

    @staticmethod
    def default(value):
        return CSPDirectiveItem('default-src', value)

    @staticmethod
    def style(value):
        return CSPDirectiveItem('style-src', value)


class JavaScriptAsset(Asset):
    pass


class JavaScriptReference(JavaScriptAsset):
    def __init__(self, src, defer, async, stage):
        super().__init__(stage)
        self.src = src
        self.is_absolute = _is_absolute(src)
        self.defer = defer
        self.async = async

    @cached_property
    def clean_src(self):
        return _clean_source(self.src)

    def create_tag(self):
        return '<script src="{src}"{async}{defer}></script>'.format(
            src=self.clean_src,
            async=(' async' if self.async else ''),
            defer=(' defer' if self.defer else '')
        )

    @cached_property
    def csp_directive(self):
        if self.is_absolute:
            url = urlparse(self.src)
            return CSPDirectiveItem.script(
                _build_url(_urlparse_to_dict(url), origin_only=True)
            )
        else:
            return None


class JavaScriptInline(JavaScriptAsset):
    def __init__(self, content, stage):
        super().__init__(stage)
        self.content = content

    def create_tag(self):
        return '<script>{}</script>'.format(self.content)

    @cached_property
    def csp_directive(self):
        return CSPDirectiveItem.script(_csp_hash(self.content))


class Link(Asset):
    def __init__(self, href, rel, **attributes):
        super().__init__('early')
        self.href = href
        self.rel = rel
        self.is_absolute = _is_absolute(href)
        self.attributes = attributes

    @cached_property
    def clean_href(self):
        return _clean_source(self.href)

    def create_tag(self):
        return '<link rel="{rel}" href="{href}"{attributes}>'.format(
            rel=self.rel, href=self.clean_href,
            attributes=_dict_to_xmlattributes(self.attributes)
        )

    @property
    def csp_directive(self):
        return None


class StyleAsset(Asset):
    pass


class StyleReference(Link, StyleAsset):
    def __init__(self, href, media, **attributes):
        super().__init__(href, 'stylesheet', media=media, **attributes)

    @cached_property
    def csp_directive(self):
        if self.is_absolute:
            url = urlparse(self.href)
            return CSPDirectiveItem.style(
                _build_url(_urlparse_to_dict(url), origin_only=True)
            )
        else:
            return super().csp_directive


class StyleInline(StyleAsset):
    def __init__(self, content, media, scoped):
        super().__init__('early')
        self.content = content
        self.media = media
        self.scoped = scoped

    def create_tag(self):
        return '<style media="{media}" {scoped}>{content}</style>'.format(
            media=self.media, scoped=('scoped' if self.scoped else ''),
            content=self.content
        )

    @cached_property
    def csp_directive(self):
        return CSPDirectiveItem.style(_csp_hash(self.content))


class Meta(Asset):
    def __init__(self, name, content):
        super().__init__(stage='early')
        self.name = name
        self.content = content

    def create_tag(self):
        return '<meta name="{name}" content="{content}">'.format(
            name=self.name, content=self.content
        )

    @property
    def csp_directive(self):
        return None


def add_csp_directive(directive, value):
    _CSP_DIRECTIVES.append(CSPDirectiveItem(directive, value))


def add_javascript_reference(src, defer=True, async=True, stage='late'):
    _ASSETS.append(JavaScriptReference(src, defer, async, stage))


def add_javascript_inline(content, stage='late'):
    _ASSETS.append(JavaScriptInline(content, stage))


def add_style_reference(src, media='all', **attributes):
    _ASSETS.append(StyleReference(src, media, **attributes))


def add_style_inline(content, media='all', scoped=False):
    _ASSETS.append(StyleInline(content, media, scoped))


def add_link(href, rel, **attributes):
    _ASSETS.append(Link(href, rel, **attributes))


def add_meta(name, content):
    _ASSETS.append(Meta(name, content))


def get_assets(stage):
    return [asset for asset in _ASSETS if asset.stage == stage]


def _csp_hash(content):
    digest = hashlib.sha256(content.encode('utf-8')).digest()
    return "'sha256-{}'".format(base64.b64encode(digest).decode('utf-8'))


class CSPMiddleware(object):
    directives = (
        CSPDirectiveItem.default("'self'"),
        CSPDirectiveItem.script("'self'"),
        CSPDirectiveItem.style("'self'"),
        CSPDirectiveItem.style("'unsafe-inline'"),
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def create_csp_policy(self):
        result = {}

        def append_directive(item: CSPDirectiveItem):
            if item.directive in result:
                result[item.directive] = result[item.directive] + (item.value, )
            else:
                result[item.directive] = (item.value, )

        for directive in self.directives:
            append_directive(directive)
        for directive in _CSP_DIRECTIVES:
            append_directive(directive)
        for asset in _ASSETS:
            if asset.csp_directive is not None:
                append_directive(asset.csp_directive)

        return tuple(result.items())

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, HttpResponse):
            response['Content-Security-Policy'] = '; '.join([
                '{type} {policies}'.format(type=directive[0], policies=' '.join([
                    policy for policy in directive[1] if policy
                ])) for directive in self.create_csp_policy()
            ])
        return response


# add javascript assets
add_javascript_inline('document.documentElement.setAttribute("class", "js")', stage='early')
