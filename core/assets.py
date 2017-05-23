import hashlib
import base64
import re
from urllib.parse import urlparse, urlencode, parse_qsl
from django.http.response import HttpResponse
from django.templatetags.static import static
from django.utils.functional import cached_property
from django.conf import settings

_JS_ASSETS = []


def build_url(urlparsedict, origin_only=False):
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


def urlparse_to_dict(parsed_url):
    return dict(zip(
        ('scheme', 'netloc', 'path', 'params', 'query', 'fragment'),
        tuple(parsed_url)
    ))


class Asset:
    def __init__(self, stage):
        if stage not in ('early', 'late'):
            raise ValueError('invalid stage "%s". should be "early" or "late"' % stage)
        self.stage = stage


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
            url = urlparse_to_dict(urlparse(static(self.src)))
            qs = parse_qsl(url['query'])
            qs.append(('v', settings.ASSET_VERSION))
            url['query'] = urlencode(qs)
            return build_url(url)

    def __repr__(self):
        return '<script src="{src}"{async}{defer}></script>'.format(
            src=self.clean_source,
            async=(' async' if self.async else ''),
            defer=(' defer' if self.defer else '')
        )

    @cached_property
    def csp_hash(self):
        if self.is_absolute:
            url = urlparse(self.src)
            return build_url(urlparse_to_dict(url), origin_only=True)
        else:
            return ''


class JavaScriptInline(JavaScriptAsset):
    def __init__(self, content, stage):
        super().__init__(stage)
        self.content = content

    def __repr__(self):
        return '<script>{}</script>'.format(self.content)

    @cached_property
    def csp_hash(self):
        return csp_hash(self.content)


def add_javascript_reference(src, defer=True, async=True, stage='late'):
    _JS_ASSETS.append(JavaScriptReference(src, defer, async, stage))


def add_javascript_inline(content, stage='late'):
    _JS_ASSETS.append(JavaScriptInline(content, stage))


def get_asset_csp_hashes(asset_type):
    if asset_type == 'js':
        clazz = JavaScriptAsset
    elif asset_type == 'css':
        clazz = CascadingStyleSheetAsset
    else:
        raise ValueError('unknown type')
    return tuple([asset.csp_hash for asset in _JS_ASSETS
                  if isinstance(asset, clazz) and asset.csp_hash])


def get_assets(stage):
    return [asset for asset in _JS_ASSETS if asset.stage == stage]


def csp_hash(content):
    digest = hashlib.sha256(content.encode('utf-8')).digest()
    return "'sha256-{}'".format(base64.b64encode(digest).decode('utf-8'))


class CSPMiddleware(object):
    default_src = ("'self'", )
    script_src = ("'self'", )
    style_src = ("'self'", "'unsafe-inline'", )

    def __init__(self, get_response):
        self.get_response = get_response

    def create_csp_policy(self):
        return (
            ('default-src', self.default_src),
            ('script-src', self.script_src + get_asset_csp_hashes('js') +
             ("'unsafe-eval'" if settings.DEBUG else '', )),
            ('style-src', self.style_src + get_asset_csp_hashes('css')),
        )

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
