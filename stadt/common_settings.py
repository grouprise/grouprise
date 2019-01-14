import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Django Basics
# https://docs.djangoproject.com/en/stable/

INSTALLED_APPS = [
    # grouprise features
    'features.articles',
    'features.associations',
    'features.contributions',
    'features.conversations',
    'features.content',
    'features.events',
    'features.files',
    'features.galleries',
    'features.gestalten',
    'features.gestalten.auth',
    'features.groups',
    'features.images',
    'features.imports',
    'features.memberships',
    'features.polls',
    'features.sharing',
    'features.stadt',
    'features.subscriptions',
    'features.tags',

    # grouprise core
    'core',

    # third-party packages
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'crispy_forms',
    'django_filters',
    'django_mailbox',
    'huey.contrib.djhuey',
    'haystack',
    'imagekit',
    'mailer',
    'rest_framework',

    # contributed django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    
    # basic django apps
    'django.forms',
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = '/stadt/static/'


# Haystack
# https://django-haystack.readthedocs.io/

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'xapian_backend.XapianEngine',
        'PATH': os.path.join(BASE_DIR, 'xapian_index'),
    },
}

HAYSTACK_XAPIAN_LANGUAGE = 'german2'


# grouprise Tags

GROUPRISE_TAGS_TAGGABLE = (
    {
        'entity': 'content2.Content',
        'props': ['title'],
        'tag_self': True,
    },
    {
        'entity': 'content2.Version',
        'props': ['text'],
        'tag_related': [lambda v: v.content],
    },
    {
        'entity': 'contributions.Contribution',
        'props': ['contribution__text'],
        'tag_related': [lambda c: c.container],
        'constraint': lambda c: (not c.container.is_conversation
                                 and hasattr(c.contribution, 'text')),
    },
)
