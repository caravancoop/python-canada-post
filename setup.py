#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='python-canada-post',
    version='0.0.0',
    author='Tomas Neme',
    author_email='lacrymology@gmail.com',
    url='http://github.com/Lacrymology',
    description='Canada Post Developer Tools API interface for python',
    packages=find_packages(),
    provides=['canada_post',],
    include_package_data=True,
    install_requires = [
        'requests>=0.8',
    ],
)