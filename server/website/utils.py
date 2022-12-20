# -*- coding: utf-8 -*-

import json
from enum import IntEnum

template_variables = {
    # generic
    'send': '发送',
    # nav
    'title_suffix': '你画我猜',
    'app_name': '你画我猜',
    'game_menu': '游戏',
    'friends_page': '好友',
    'about_page': '关于',
    'test_page': '测试页面',
    'match_mode': '匹配模式',
    'custom_mode': '自定义模式',
    'ranking': '排行榜',
    'login': '登录',
    'signup': '注册',
    'user_info': '用户信息',
    'logout': '注销',
    # login
    'username': '账号',
    'password': '密码',
    'password_again': '再次输入密码',
    'please_input_username': '请输入账号',
    # game
    'guess_the_image': '快来猜图片！',
    'hint_prefix': '提示：',
    'submit': '提交',
    'abandon': '放弃',
    # friends
    'friend_list': '好友列表',
    'join_game': '加入游戏',
    'delete_friend': '删除好友',
}


class StatusCode(IntEnum):
    SUCCESS = 0
    ERR_SERVER_UNKNOWN = 100
    ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG = 200
    ERR_ACCOUNT_USERNAME_EXISTED = 201
    ERR_ACCOUNT_NOT_LOGINED = 202
    ERR_ACCOUNT_USERNAME_NOT_EXISTED = 203

error_msg = {
    StatusCode.SUCCESS: '',
    StatusCode.ERR_SERVER_UNKNOWN: '服务器异常',
    StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG: '用户名或密码错误',
    StatusCode.ERR_ACCOUNT_USERNAME_EXISTED: '用户名已存在',
    StatusCode.ERR_ACCOUNT_NOT_LOGINED: '用户未登录',
    StatusCode.ERR_ACCOUNT_USERNAME_NOT_EXISTED: '用户名不存在',
}

default_errno = StatusCode.ERR_SERVER_UNKNOWN


def generate_return_data(errno: StatusCode, msg=None) -> str:
    if errno not in error_msg:
        errno = default_errno
    ret = {'code': int(errno), 'message': error_msg[errno]}
    if isinstance(msg, dict):
        ret.update(msg)
    return json.dumps(ret)
