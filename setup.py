#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" distribute- and pip-enabled setup.py for ratslam """

from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension
import os, sys

import re



setup(
    name='ratslam',

    version='dev',

    scripts=['scripts/ratslam'],

    include_package_data=True,
    
    #install_requires=parse_requirements('requirements.txt'),
    #dependency_links=parse_dependency_links('requirements.txt')
)
