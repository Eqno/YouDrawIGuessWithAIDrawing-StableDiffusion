# -*- coding: utf-8 -*-

import json
from enum import IntEnum

template_variables = {
    'title_suffix': '你画我猜',
    'app_name': '你画我猜',
    'game_menu': '游戏',
    'friends_page': '好友',
    'about_page': '关于',
    'match_mode': '匹配模式',
    'custom_mode': '自定义模式',
    'ranking': '排行榜',
    'login': '登录',
    'register': '注册',
    'username': '账号',
    'password': '密码',
    'please_input_username': '请输入账号',
    'guess_the_image': '快来猜图片！',
    'hint_prefix': '提示：',
    'submit': '提交',
    'abandon': '放弃',
}


class StatusCode(IntEnum):
    SUCCESS = 0
    ERR_SERVER_UNKNOWN = 100
    ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG = 200
    ERR_ACCOUNT_USERNAME_EXISTED = 201


error_msg = {
    StatusCode.SUCCESS: '',
    StatusCode.ERR_SERVER_UNKNOWN: '服务器异常',
    StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG: '用户名或密码错误',
}

default_errno = StatusCode.ERR_SERVER_UNKNOWN


def generate_return_data(errno: StatusCode, res=None) -> str:
    if errno not in error_msg:
        errno = default_errno
    ret = {'code': int(errno), 'message': error_msg[errno]}
    if isinstance(res, dict):
        ret.update(res)
    return json.dumps(ret)
