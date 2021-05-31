#!/usr/bin/env python2.7

# Copyright (c) 2015, VMRaid Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import os
import vmraid
vmraid.connect(site=os.environ.get("site"))