# -*- coding: utf-8 -*-

import os
import pathlib

cwd = pathlib.Path(os.getcwd())
if os.path.basename(cwd) == 'logic':
    cwd = cwd.parent
if os.path.basename(cwd) == 'server':
    cwd = cwd.parent
