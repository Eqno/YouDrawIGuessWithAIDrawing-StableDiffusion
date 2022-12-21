# -*- coding: utf-8 -*-

import os
import json
import flask
import pathlib
from .utils import generate_return_data, StatusCode

data_base_path = pathlib.Path(os.getcwd()) / 'data'
msg_data_path = data_base_path / 'msg'
user_data_path = data_base_path / 'user'
filename_suffix = '.json'


def backend_init():
    for _dir in (data_base_path, msg_data_path, user_data_path):
        if not _dir.exists():
            os.mkdir(_dir)


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

    user_file_path = user_data_path / (username + filename_suffix)

    if user_file_path.exists():
        with open(user_file_path, 'r') as f:
            user_data = json.load(f)
            if username == user_data['username'] and password == user_data[
                    'password']:
                session_set_username(username)
                return generate_return_data(StatusCode.SUCCESS)

    return generate_return_data(
        StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG)


def api_account_signup():
    data = flask.request.get_json()
    username = data['username']
    password = data['password']

    user_file_path = user_data_path / (username + filename_suffix)

    if user_file_path.exists():
        return generate_return_data(StatusCode.ERR_ACCOUNT_USERNAME_EXISTED)

    with open(user_file_path, 'w') as f:
        user_data = {}
        user_data['username'] = username
        user_data['password'] = password
        user_data['friends'] = []
        json.dump(user_data, fp=f)
        session_set_username(username)

    return generate_return_data(StatusCode.SUCCESS)


def api_account_logout():
    username = session_get_username()

    if username:
        if session_del_username():
            return generate_return_data(StatusCode.SUCCESS)
        return generate_return_data(StatusCode.ERR_SERVER_UNKNOWN)
    return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)


def api_account_userinfo():
    data = flask.request.get_json()
    username = data['username']

    user_file_path = user_data_path / (username + filename_suffix)

    if not user_file_path.exists():
        return generate_return_data(
            StatusCode.ERR_ACCOUNT_USERNAME_NOT_EXISTED)

    with open(user_file_path, 'r') as f:
        raw_user_info = json.load(f)
        userinfo = {}
        userinfo['username'] = raw_user_info['username']
        userinfo['avatar'] = '/static/avatar.png'
        return generate_return_data(StatusCode.SUCCESS, {'userinfo': userinfo})


def api_account_add_friend():
    data = flask.request.get_json()

    current_username = session_get_username()
    current_filepath = user_data_path / (current_username + filename_suffix)

    if not current_filepath.exists():
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    target_username = data['username']
    target_filepath = user_data_path / (target_username + filename_suffix)

    if not target_filepath.exists():
        return generate_return_data(
            StatusCode.ERR_ACCOUNT_USERNAME_NOT_EXISTED)

    if current_username == target_username:
        return generate_return_data(
            StatusCode.ERR_ACCOUNT_DO_NOT_ADD_SELF_AS_FRIEND)

    with open(current_filepath, 'r+') as f:
        user_info = json.load(f)
        # This is slow but we do not care it currently
        friends_set = set(user_info['friends'])
        friends_set.add(target_username)
        user_info['friends'] = list(friends_set)
        f.seek(0)
        json.dump(user_info, fp=f)
        f.truncate()
    with open(target_filepath, 'r+') as f:
        user_info = json.load(f)
        # This is slow but we do not care it currently
        friends_set = set(user_info['friends'])
        friends_set.add(current_username)
        user_info['friends'] = list(friends_set)
        f.seek(0)
        json.dump(user_info, fp=f)
        f.truncate()

    return generate_return_data(StatusCode.SUCCESS)


# TODO: get status from game
def api_account_get_friends():
    username = session_get_username()

    if not username:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    user_file_path = user_data_path / (username + filename_suffix)
    if not user_file_path.exists():
        return generate_return_data(StatusCode.ERR_SERVER_UNKNOWN)
    with open(user_file_path, 'r') as f:
        user_info = json.load(f)
        friends = list({
            'name': name,
            'status': 'offline'
        } for name in user_info['friends'])
        return generate_return_data(StatusCode.SUCCESS, {'friends': friends})


def api_game_core_image():
    result = {'url': '/static/capoo.png'}
    return generate_return_data(0, result)


backend_pages = {
    '/api/account/username': api_account_username,
    '/api/account/userinfo': {
        'view_func': api_account_userinfo,
        'methods': ['POST']
    },
    '/api/account/login': {
        'view_func': api_account_login,
        'methods': ['POST']
    },
    '/api/account/signup': {
        'view_func': api_account_signup,
        'methods': ['POST']
    },
    '/api/account/logout': api_account_logout,
    '/api/account/add_friend': {
        'view_func': api_account_add_friend,
        'methods': ['POST']
    },
    '/api/account/get_friends': api_account_get_friends,
    '/api/game/core/image': api_game_core_image,
}
