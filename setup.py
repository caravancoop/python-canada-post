#!/usr/bin/env python

from setuptools import find_packages, setup
from canada_post import VERSION

setup(
    name='python-canada-post',
    version=VERSION,
    author='Tomas Neme',
    author_email='lacrymology@gmail.com',
    url='http://github.com/Lacrymology/python-canada-post-dev-prog',
    description='Canada Post Developer Tools API interface for python',
    packages=find_packages(),
    include_package_data=True,
    install_requires = [
        'requests>=0.8',
        "lxml",
    ],
)
