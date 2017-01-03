"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup, find_packages
from os import path
import glob
from stadt import VERSION


# parse dependencies from requirements.txt
def get_requirements():
    with open('requirements.txt') as f:
        return [
            line.split('#')[0].strip() for line in f.read().splitlines()
            if not line.strip().startswith('#')
        ]


def get_readme():
    with open(path.join(path.dirname(__file__), 'README.md')) as f:
        return f.read()


def include_recursive(directory, query=''):
    result = {}
    for file in glob.iglob('{}/**{}'.format(directory, query), recursive=True):
        if path.isfile(file):
            result.setdefault(path.dirname(file), []).append(file)
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
