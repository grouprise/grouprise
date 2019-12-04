import os
import re
from setuptools import setup, find_packages


# parse dependencies from requirements.txt
def get_requirements():
    # replace git-based URLs (e.g. "git+https://github.com/jazzband/django-taggit.git")
    git_http_regex = re.compile(r"^git\+https?://.*/(?P<name>[^/]+?)(?:\.git)?$")
    with open('requirements.txt') as f:
        for line in f.read().splitlines():
            line = line.strip()
            if not line.startswith('#'):
                line = line.split('#')[0].strip()
                line = git_http_regex.sub(r'\g<name>', line)
                yield line


def get_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()


def get_version():
    with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
        return f.read().strip()


setup(
    name='grouprise',
    version=get_version(),
    description='grouprise is a platform that encourages and enables '
                'social action and solidarity',
    long_description=get_readme(),
    url='https://git.hack-hro.de/stadtgestalten/stadtgestalten.git',
    author='grouprise Maintainers',
    author_email='mail@grouprise.org',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: End Users/Desktop',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: German',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=list(get_requirements()),
    data_files=(
        ('.', (
            'manage.py', 'README.md', 'LICENSE', 'CONTRIBUTORS.md', 'CONTRIBUTING.md',
        )),
    ),
)
