import hashlib
import base64
import re
from urllib.parse import urlparse, urlencode, parse_qsl
from django.http.response import HttpResponse
from django.templatetags.static import static
from django.utils.functional import cached_property
from django.conf import settings

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


class CascadingStyleSheetAsset(Asset):
    pass


class JavaScriptReference(JavaScriptAsset):
    def __init__(self, src, defer, async, stage):
        super().__init__(stage)
        self.src = src
        self.is_absolute = bool(re.match(r'^https?://', src))
        self.defer = defer
        self.async = async

    @cached_property
    def clean_source(self):
        if self.is_absolute:
            return self.src
        else:
            url = _urlparse_to_dict(urlparse(static(self.src)))
            qs = parse_qsl(url['query'])
            qs.append(('v', settings.ASSET_VERSION))
            url['query'] = urlencode(qs)
            return _build_url(url)

    def create_tag(self):
        return '<script src="{src}"{async}{defer}></script>'.format(
            src=self.clean_source,
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


def add_csp_directive(directive, value):
    _CSP_DIRECTIVES.append(CSPDirectiveItem(directive, value))


def add_javascript_reference(src, defer=True, async=True, stage='late'):
    _ASSETS.append(JavaScriptReference(src, defer, async, stage))


def add_javascript_inline(content, stage='late'):
    _ASSETS.append(JavaScriptInline(content, stage))


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


# add core assets
add_javascript_reference('stadt/js/app.js')
add_javascript_inline('document.documentElement.setAttribute("class", "js")', stage='early')
