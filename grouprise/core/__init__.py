from django.utils.module_loading import autodiscover_modules

default_app_config = 'core.apps.CoreConfig'


def autodiscover():
    for module_name in ['rules', 'signals']:
        autodiscover_modules(module_name)
