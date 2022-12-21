# -*- coding: utf-8 -*-

import flask, json, os
from .utils import generate_return_data, StatusCode

data_base_path = os.getcwd().replace('\\', '/')+'/data/'
msg_data_path = data_base_path + './msg/'
user_data_path = data_base_path + './user/'

def session_get_username():
    return flask.session.get('username', None)

def session_set_username(username: str):
    flask.session['username'] = username

def session_del_username():
    return flask.session.pop('username')

def api_account_username():
    ret_code, ret_msg = StatusCode.ERR_ACCOUNT_NOT_LOGINED, None
    username = session_get_username()

    if username: ret_code, ret_msg = StatusCode.SUCCESS, {'username': username}
    return generate_return_data(ret_code, ret_msg)

def find_or_create_data_dir(dir:str):

    if not os.path.exists(dir):
        os.makedirs(dir)

def api_account_login():
    ret_code = StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG
    find_or_create_data_dir(user_data_path)

    data = flask.request.get_json()
    username = data['username']
    password = data['password']

    try:
        with open(user_data_path + username + '.json', 'r') as f:
            user_data = json.load(f)

            if username == user_data['username'] and password == user_data['password']:
                session_set_username(username)
                ret_code = StatusCode.SUCCESS
            
            f.close()
    except: pass
    return generate_return_data(ret_code)

def api_account_signup():
    ret_code = StatusCode.ERR_ACCOUNT_USERNAME_EXISTED
    find_or_create_data_dir(user_data_path)

    http_data = flask.request.get_json()
    username = http_data['username']
    password = http_data['password']

    try:
        with open(user_data_path + username + '.json', 'r') as f:
            f.close()
    except:
        with open(user_data_path + username + '.json', 'w') as f:
            user_data = {}

            user_data['username'] = username
            user_data['password'] = password
            user_data['firend_list'] = {}
            
            ret_code = StatusCode.SUCCESS
            session_set_username(username)

            json.dump(user_data, fp=f)
            f.close()

    return generate_return_data(ret_code)

def api_account_logout():
    ret_code = StatusCode.ERR_ACCOUNT_NOT_LOGINED
    username = session_get_username()

    if username is not None:
        if session_del_username():
            ret_code = StatusCode.SUCCESS
        else: ret_code = StatusCode.ERR_SERVER_UNKNOWN
    return generate_return_data(ret_code)

def api_account_userinfo():
    ret_code, ret_msg = StatusCode.ERR_ACCOUNT_USERNAME_NOT_EXISTED, None
    find_or_create_data_dir(user_data_path)

    http_data = flask.request.get_json()
    username = http_data['username']

    try:
        with open(user_data_path + username + '.json', 'r') as f:
            ret_msg = json.load(f)
            ret_code = StatusCode.SUCCESS

            f.close()
    except: pass
    return generate_return_data(ret_code, ret_msg)

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
        'methods' : ['POST']
    },
    '/api/account/logout': api_account_logout,
    '/api/game/core/image': api_game_core_image,
}
