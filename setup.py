#!/usr/bin/env python

"""
distutils/setuptools install script.
"""
import os
import re

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


requires = [
    'requests>=2.21.0',
    'gevent==1.4.0',
]


def get_version():
    init = open(os.path.join(ROOT, 'apyllo', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='apyllo',
    version=get_version(),
    description='The Apollo Config Center SDK for Python',
    long_description=open('README.md').read(),
    author='Jacky Wu',
    url='https://github.com/Colstuwjx/apyllo',
    scripts=[],
    packages=find_packages(exclude=['tests*']),
    package_data={},
    include_package_data=True,
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
