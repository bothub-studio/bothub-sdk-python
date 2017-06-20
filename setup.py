#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='bothub',
    version='0.1.14',
    description=u'Build serverless chatbot on BotHub.Studio',
    long_description=LONG_DESCRIPTION,
    author='Jeongsoo Park',
    author_email='jeongsoo.park@bothub.studio',
    url='https://github.com/bothub-studio/bothub',
    license="AGPL v3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'zmq',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'requests-mock',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Utilities'
    ],
    keywords='bothub serverless chatbot framework',
)
