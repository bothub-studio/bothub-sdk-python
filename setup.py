#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


setup(
    name='bothub-client',
    version='0.0.1',
    description=u'',
    author='Jeongsoo Park',
    author_email='toracle@gmail.com',
    url='https://github.com/toracle/bothub-client',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'requests-mock',
    ],
    dependency_links=[
    ],
    entry_points={
        'console_scripts': [
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
)
