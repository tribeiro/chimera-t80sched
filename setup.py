#! /usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os
import sys
import glob
import re

# read version.py file to get version and metadata information
here = os.path.abspath(os.path.dirname(__file__))
version_py = os.path.join(here, "src/t80sched/core/version.py")
execfile(version_py)

# chimera scripts
t80sched_scripts = ['src/scripts/chimera-t80sched',
					'src/scripts/chimera-setupdb']

# platform specific requirements
platform_deps = []

# go!
setup(
    name='t80sched-python',
    version=_t80sched_version_,
    description=_t80sched_description_,
    long_description=open("docs/site/index.rst").read(),
    url=_t80sched_url_,

    author=_t80sched_author_,
    author_email=_t80sched_author_email_,

    license=_t80sched_license_,

    package_dir={"": "src"},
    packages=find_packages("src", exclude=["*.tests"]),

    include_package_data=True,

    scripts=t80sched_scripts,

    tests_require=["astropy","chimera"],
)
