#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='macropolo',
    version='0.3.0',
    author='CFPB',
    author_email='tech@cfpb.gov',
    packages=find_packages(),
    test_suite = 'macropolo.tests',
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
        'mock',
    ],
)
