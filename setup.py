import os
from setuptools import setup, find_packages

from stadt import VERSION


# parse dependencies from requirements.txt
def get_requirements():
    with open('requirements.txt') as f:
        return [
            line.split('#')[0].strip() for line in f.read().splitlines()
            if not line.strip().startswith('#')
        ]


def get_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
        return f.read()


def include_recursive(directory):
    result = {}
    for dirpath, dirnames, filenames in os.walk(directory):
        if filenames:
            result[dirpath] = [os.path.join(dirpath, fname) for fname in filenames]
    return tuple(result.items())


def get_root_packages():
    return [pkg for pkg in find_packages() if '.' not in pkg]


static_files = include_recursive('static')
offline_website = include_recursive('offline-website')

setup(
    name='stadtgestalten',
    version=VERSION,
    description='Stadtgestalten is a platform that encourages and enables '
                'social action and solidarity',
    long_description=get_readme(),
    url='https://git.hack-hro.de/stadtgestalten/stadtgestalten.git',
    author='Stadtgestalten Maintainers',
    author_email='wir@stadtgestalten.org',
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
    install_requires=get_requirements(),
    data_files=(
        ('.', ('manage.py', 'README.md', 'LICENSE', 'CONTRIBUTORS.md', 'CONTRIBUTING.md')),
    ) + static_files + offline_website,
)
