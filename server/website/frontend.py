# -*- coding: utf-8 -*-

import flask


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


def friends():
    return flask.render_template('friends.html',
                                 title='好友',
                                 base_url=flask.request.base_url)


def get_image(filename):
    return flask.send_file('static/' + filename, mimetype='image/png')


frontend_pages = {
    '/': index,
    '/login': login,
    '/game': game,
    '/signup': signup,
    '/friends': friends,
    '/image/<filename>': get_image,
}
