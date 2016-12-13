from core import tests
from django.conf import settings
from features.gestalten import tests as gestalten


class Test(gestalten.GestaltMixin, tests.Test):
    def test(self):
        import difflib

        print(settings.CACHES)
        r1a = self.client.get('/')
        self.client.force_login(self.gestalt.user, 'django.contrib.auth.backends.ModelBackend')
        r2a = self.client.get('/')
        self.client.logout()
        
        settings.CACHES['default']['BACKEND'] = 'django.core.cache.backends.locmem.LocMemCache'
        print(settings.CACHES)
        r1b = self.client.get('/')
        self.client.force_login(self.gestalt.user, 'django.contrib.auth.backends.ModelBackend')
        r2b = self.client.get('/')
        
        delta = difflib.unified_diff(r1a, r1b)
        print(r1a.content == r1b.content, r2a.content == r2b.content)
