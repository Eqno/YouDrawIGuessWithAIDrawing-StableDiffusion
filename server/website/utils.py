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
    'custom_mode': '创建房间',
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
    # game3
    'hint_prefix': '提示：',
    'submit': '提交',
    'select_role': '选择身份',
    'abandon': '放弃',
    'ready': '准    备',
    'start_match': '开始匹配',
    # friends
    'gaming': '游戏中',
    'online': '在线上',
    'offline': '已离线',
    'sent_app': '发送的申请',
    'received_app': '收到的申请',
    'friend_list': '好友列表',
    'add_friend': '添加好友',
    'delete_friend': '删除好友',
    # others
    'page_timer_interval': '500',
}

class StatusCode(IntEnum):
    SUCCESS = 0
    
    ERR_SERVER_UNKNOWN = 100

    ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG = 200
    ERR_ACCOUNT_USERNAME_EXISTED = 201
    ERR_ACCOUNT_NOT_LOGINED = 202
    ERR_ACCOUNT_USERNAME_NOT_EXISTED = 203
    ERR_ACCOUNT_DO_NOT_ADD_SELF_AS_FRIEND = 204
    ERR_ACCOUNT_USERNAME_ALREADY_IN_FRIEND_LIST = 205
    ERR_ACCOUNT_APPLICATION_ALREADY_SENT = 206

    ERR_GAME_PLAYER_NUM_EXCEED_MAX = 207
    ERR_GAME_PLAYER_JOIN_GAME_FAILED = 208
    ERR_GAME_PLAYER_GET_OTHER_IN_ROOM_FAILED = 209
    ERR_GAME_PLAYER_SET_READY_FAILED = 210

error_msg = {
    StatusCode.SUCCESS: '',

    StatusCode.ERR_SERVER_UNKNOWN: '服务器异常',
    
    StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG: '用户名或密码错误',
    StatusCode.ERR_ACCOUNT_USERNAME_EXISTED: '用户名已存在',
    StatusCode.ERR_ACCOUNT_NOT_LOGINED: '用户未登录',
    StatusCode.ERR_ACCOUNT_USERNAME_NOT_EXISTED: '用户名不存在',
    StatusCode.ERR_ACCOUNT_DO_NOT_ADD_SELF_AS_FRIEND: '不能添加自己为好友',
    StatusCode.ERR_ACCOUNT_USERNAME_ALREADY_IN_FRIEND_LIST: '用户已在好友列表中',
    StatusCode.ERR_ACCOUNT_APPLICATION_ALREADY_SENT: '申请已发送，无需重复发送',
    
    StatusCode.ERR_GAME_PLAYER_NUM_EXCEED_MAX: '正在游玩的玩家数量已达最大限制',
    StatusCode.ERR_GAME_PLAYER_JOIN_GAME_FAILED: '加入游戏失败',
    StatusCode.ERR_GAME_PLAYER_GET_OTHER_IN_ROOM_FAILED: '获取房间内其他玩家信息失败',
    StatusCode.ERR_GAME_PLAYER_SET_READY_FAILED: '设置准备状态失败'
}

default_errno = StatusCode.ERR_SERVER_UNKNOWN

def generate_return_data(errno: StatusCode, msg=None) -> str:
    if errno not in error_msg:
        errno = default_errno
    ret = {'code': int(errno), 'message': error_msg[errno]}
    if isinstance(msg, dict):
        ret.update(msg)
    return json.dumps(ret)
