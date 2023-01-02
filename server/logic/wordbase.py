# -*- coding: utf-8 -*-

import os
from . import consts

WORD_BASE_PATH = consts.cwd / 'data' / 'wordbase'

if not WORD_BASE_PATH.exists():
    os.makedirs(WORD_BASE_PATH)

print(WORD_BASE_PATH)


# 返回所有词集的名称
def get_set_list() -> list:
    return os.listdir(WORD_BASE_PATH)


def load_word_set(name: str):
    filepath = WORD_BASE_PATH / name
    if not filepath.exists():
        print('word set not exist')
        return []

    with open(filepath, 'rt') as f:
        word_set = []
        for line in f:
            word_set.append(line)


def create_word_set(name: str, data: list):
    filepath = WORD_BASE_PATH / name
    if filepath.exists():
        print('word set already exist')
        return

    with open(filepath, 'wt') as f:
        f.write('\n'.join(data))


def append_word_set(name: str, data: list):
    filepath = WORD_BASE_PATH / name
    if not filepath.exists():
        print('word set not exist')

    with open(filepath, 'a') as f:
        f.write('\n'.join(data))
