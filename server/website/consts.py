# -*- coding: utf-8 -*-

import os
import pathlib

cwd = pathlib.Path(os.getcwd())

avatar_file_name = 'avatar.png'

data_base_path = cwd / 'data'
user_data_path = data_base_path / 'user'

default_avatar_path = cwd / 'app' / 'static' / 'avatar.png'
