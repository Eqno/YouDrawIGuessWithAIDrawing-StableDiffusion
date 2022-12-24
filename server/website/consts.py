# -*- coding: utf-8 -*-

import os
import pathlib

cwd = pathlib.Path(os.getcwd())
if os.path.basename(cwd) == 'server':
    cwd = cwd.parent

avatar_file_name = 'avatar.png'

data_base_path = cwd / 'data'
user_data_path = data_base_path / 'user'

default_avatar_path = cwd / 'app' / 'static' / 'avatar.png'
default_ranking = 1000
