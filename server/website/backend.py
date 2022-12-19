# -*- coding: utf-8 -*-

import flask
from .utils import generate_return_data, StatusCode

user_database = {
    # admin, administrator
    'admin': '200ceb26807d6bf99fd6f4f0d1ca54d4'
}


def session_get_username():
    return flask.session.get('username', None)


def session_set_username(username: str):
    flask.session['username'] = username


def session_del_username():
    return flask.session.pop('username')


def api_account_username():
    username = session_get_username()
    if username:
        return generate_return_data(StatusCode.SUCCESS, {'username': username})
    return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)


def api_account_login():
    data = flask.request.get_json()
    username = data['username']
    password = data['password']
    if username in user_database:
        if password == user_database[username]:
            session_set_username(username)
            return generate_return_data(StatusCode.SUCCESS)
    return generate_return_data(
        StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG)

def api_account_signup():
    data = flask.request.get_json()
    username = data['username']
    password = data['password']
    if username in user_database:
        return generate_return_data(StatusCode.ERR_ACCOUNT_USERNAME_EXISTED)
    user_database[username] = password
    session_set_username(username)
    return generate_return_data(StatusCode.SUCCESS)

def api_account_logout():
    username = session_get_username()
    if username:
        if session_del_username():
            return generate_return_data(StatusCode.SUCCESS)
        else:
            return generate_return_data(StatusCode.ERR_SERVER_UNKNOWN)
    return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)


def api_game_core_image():
    result = {'url': '/static/capoo.png'}
    return generate_return_data(0, result)


backend_pages = {
    '/api/account/username': api_account_username,
    '/api/account/login': {
        'view_func': api_account_login,
        'methods': ['POST']
    },
    '/api/account/signup': {
        'view_func': api_account_signup,
        'methods' : ['POST']
    },
    '/api/account/logout': api_account_logout,
    '/api/game/core/image': api_game_core_image,
}
