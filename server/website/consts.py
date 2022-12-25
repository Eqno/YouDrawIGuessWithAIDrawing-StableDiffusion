# -*- coding: utf-8 -*-

import os
import pathlib

cwd = pathlib.Path(os.getcwd())
if os.path.basename(cwd) == 'server':
    cwd = cwd.parent
avatar_file_name = 'avatar.png'

data_base_path = cwd / 'data'
user_data_path = data_base_path / 'user'
game_data_path = data_base_path / 'game'
pics_data_path = game_data_path / 'pics'

words_path = game_data_path / 'words.json'
default_words = ['咖波', '大黄狗', '小白兔', '蓝猫', '柴犬']
default_positive_prompt = ['detail', 'high quality', 'master works']
default_negative_prompt = ['nsfw', 'aldult', 'porn']

default_avatar_path = cwd / 'app' / 'static' / 'avatar.png'
default_ranking = 1000

generated_img_size = 256
