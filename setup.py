import re
import os

from setuptools import setup, find_packages


def find_version(*file_paths):
    with open(os.path.join(*file_paths)) as fo:
        version_file = fo.read()
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]$',
                              version_file, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


package_name = 'pydbpedia'

setup(
    name=package_name,
    description='pyDBpedia is a simple python wrapper for querying dbpedia',

    version=find_version(package_name, '__init__.py'),
    packages=find_packages(exclude=('tests',)),
    author='Matteus Tanha',
    author_email='matteus.tanha@gmail.com',
    url='https://github.com/MatteusT/pyDBpedia',
    download_url='https://github.com/MatteusT/pyDBpedia/archive/v0.0.1.tar.gz',
    keywords=['DBpedia', 'knowledge base'],
    install_requires=(
        'requests==2.22.0',
    ),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    license="Apache 2.0",
    python_requires=">=3.6",
)
