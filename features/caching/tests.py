from core import tests
from django.conf import settings
from django.core import cache
from features.gestalten import tests as gestalten


class Test(gestalten.GestaltMixin, tests.Test):
    def test(self):
        import difflib

        r1a = self.client.get('/')
        self.client.force_login(self.gestalt.user, 'django.contrib.auth.backends.ModelBackend')
        r2a = self.client.get('/')
        self.client.logout()
        
        cache.cache.cache = cache.caches['test']
        r1b = self.client.get('/')
        self.client.force_login(self.gestalt.user, 'django.contrib.auth.backends.ModelBackend')
        r2b = self.client.get('/')
        
        delta = difflib.unified_diff(r1a, r1b)
        print(r1a.content == r1b.content, r2a.content == r2b.content)
