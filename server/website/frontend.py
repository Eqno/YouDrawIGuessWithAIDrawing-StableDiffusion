# -*- coding: utf-8 -*-

import flask

def frontend_init():
    pass

def index():
    return flask.render_template('index.html',
                                 title='首页',
                                 base_url=flask.request.base_url)

def login():
    return flask.render_template('login.html',
                                 title='登录',
                                 base_url=flask.request.base_url)

def signup():
    return flask.render_template('signup.html',
                                 title='注册',
                                 base_url=flask.request.base_url)

def game():
    return flask.render_template('game.html',
                                 title='游戏',
                                 base_url=flask.request.base_url)

def match():
    return flask.render_template('match.html',
                                 title='匹配',
                                 base_url=flask.request.base_url)

def custom():
    return flask.render_template('custom.html',
                                 title='建房',
                                 base_url=flask.request.base_url)

def selectrole():
    return flask.render_template('selectrole.html',
                                 title='身份',
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

def get_image(filename):
    return flask.send_file('static/' + filename, mimetype='image/png')

frontend_pages = {
    '/': index,
    '/login': login,
    '/signup': signup,

    '/game': game,
    '/match': match,
    '/custom': custom,
    '/selectrole': selectrole,
    
    '/friends': friends,
    '/user/<username>': userinfo,
    '/image/<filename>': get_image,
}