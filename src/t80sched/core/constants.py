#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
from chimera.core import constants as C

SYSTEM_CONFIG_LOG_NAME = os.path.join(C.SYSTEM_CONFIG_DIRECTORY,
									  'chimera-t80sched.log')

DEFAULT_PROGRAM_DATABASE = os.path.join(C.SYSTEM_CONFIG_DIRECTORY,
										'scheduler-t80sched.db')
