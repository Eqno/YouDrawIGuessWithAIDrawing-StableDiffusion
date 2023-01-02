# -*- coding: utf-8 -*-

import flask
from . import consts


def frontend_init():
    pass


def index():
    return flask.render_template('index.html',
                                 title='首页',
                                 need_login=False,
                                 base_url=flask.request.base_url)


def login():
    return flask.render_template('login.html',
                                 title='登录',
                                 need_login=False,
                                 base_url=flask.request.base_url)


def signup():
    return flask.render_template('signup.html',
                                 title='注册',
                                 need_login=False,
                                 base_url=flask.request.base_url)


def host():
    return flask.render_template('host.html',
                                 title='游戏',
                                 heartbeat_gaming=True,
                                 base_url=flask.request.base_url)


def guest():
    return flask.render_template('guest.html',
                                 title='游戏',
                                 heartbeat_gaming=True,
                                 base_url=flask.request.base_url)


def match():
    return flask.render_template('match.html',
                                 title='匹配',
                                 heartbeat_gaming=True,
                                 base_url=flask.request.base_url)


def custom():
    return flask.render_template('custom.html',
                                 title='建房',
                                 base_url=flask.request.base_url)


def selectrole():
    return flask.render_template('selectrole.html',
                                 title='身份',
                                 heartbeat_gaming=True,
                                 base_url=flask.request.base_url)

def settlement():
    return flask.render_template('settlement.html',
                                 title='结算',
                                 heartbeat_gaming=True,
                                 base_url=flask.request.base_url)

def friends():
    return flask.render_template('friends.html',
                                 title='好友',
                                 base_url=flask.request.base_url)

def userinfo(username):
    return flask.render_template('userinfo.html',
                                 title='用户信息',
                                 username=username,
                                 base_url=flask.request.base_url)

def user_avatar(username):
    avatar = consts.user_data_path / username / consts.avatar_file_name
    if avatar.exists():
        return flask.send_file(avatar, mimetype='image/png')
    return flask.send_file(consts.default_avatar_path, mimetype='image/png')


def get_image(filename):
    return flask.send_file(consts.cwd / 'static' / filename, mimetype='image/png')


frontend_pages = {
    '/': index,
    '/login': login,
    '/signup': signup,
    '/host': host,
    '/guest': guest,
    '/match': match,
    '/custom': custom,
    '/friends': friends,
    '/selectrole': selectrole,
    '/settlement': settlement,
    '/user/<username>': userinfo,
    '/avatar/<username>': user_avatar,
    '/image/<filename>': get_image,
}
