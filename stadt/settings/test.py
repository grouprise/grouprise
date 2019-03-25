STADTGESTALTEN_IN_TEST = True
SECRET_KEY = "ENE MENE MUH"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
GROUPRISE_UNKNOWN_GESTALT_ID = 1
HUEY = {
    'always_eager': True,
}
SYNC_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
ASYNC_EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
