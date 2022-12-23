# -*- coding: utf-8 -*-

import os, json, flask, pathlib, sys, time, threading
from .utils import generate_return_data, StatusCode
import simple_websocket

sys.path.append(os.getcwd().replace('\\', '/') + '/../')
from logic import *

SOCKET_ONLINE_TIME_INTERVAL = 0.1
CHECL_ONLINE_TIME_INTERVAL = 5

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
        user_info = {}

        user_info['username'] = username
        user_info['password'] = password

        user_info['state'] = 'offline'

        user_info['friends'] = []
        user_info['applications_sent'] = []
        user_info['applications_received'] = []

        json.dump(user_info, fp=f)
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
        friends_set = set(user_info.get('friends', []))
        if target_username in friends_set:
            return generate_return_data(
                StatusCode.ERR_ACCOUNT_USERNAME_ALREADY_IN_FRIEND_LIST)

        send_apply_set = set(user_info.get('applications_sent', []))
        send_apply_set.add(target_username)
        user_info['applications_sent'] = list(send_apply_set)

        f.seek(0)
        json.dump(user_info, fp=f)
        f.truncate()

    with open(target_filepath, 'r+') as f:
        user_info = json.load(f)

        # This is slow but we do not care it currently
        send_apply_set = set(user_info.get('applications_sent', []))
        if current_username in send_apply_set:

            friends_set = set(user_info.get('friends', []))
            friends_set.add(current_username)
            user_info['friends'] = list(friends_set)

            f.seek(0)
            json.dump(user_info, fp=f)
            f.truncate()

            return generate_return_data(StatusCode.SUCCESS)

        receive_apply_set = set(user_info.get('applications_received', []))
        if current_username in receive_apply_set:
            return generate_return_data(
                StatusCode.ERR_ACCOUNT_APPLICATION_ALREADY_SENT)

        receive_apply_set.add(current_username)
        user_info['applications_received'] = list(receive_apply_set)

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
        } for name in user_info.get('friends', []))
        return generate_return_data(
            StatusCode.SUCCESS, {
                'friends': friends,
                'applications_sent': user_info.get('applications_sent', []),
                'applications_received': user_info.get('applications_received', []),
            })


def api_account_approved_application():
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
        friends_set = set(user_info.get('friends', []))
        friends_set.add(target_username)
        user_info['friends'] = list(friends_set)

        receive_apply_set = set(user_info.get('applications_received', []))
        receive_apply_set.remove(target_username)
        user_info['applications_received'] = list(receive_apply_set)

        f.seek(0)
        json.dump(user_info, fp=f)
        f.truncate()

    with open(target_filepath, 'r+') as f:
        user_info = json.load(f)

        # This is slow but we do not care it currently
        friends_set = set(user_info.get('friends', []))
        friends_set.add(current_username)
        user_info['friends'] = list(friends_set)

        send_apply_set = set(user_info.get('applications_sent', []))
        send_apply_set.remove(current_username)
        user_info['applications_sent'] = list(send_apply_set)

        f.seek(0)
        json.dump(user_info, fp=f)
        f.truncate()

    return generate_return_data(StatusCode.SUCCESS)


def api_game_room_join_game():
    data = flask.request.get_json()

    current_username = session_get_username()
    target_username = data.get('username', None)
    current_role = data.get('role', None)

    retcode, message = create_player_instance(current_username)
    if not retcode:
        return generate_return_data(StatusCode.ERR_GAME_PLAYER_NUM_EXCEED_MAX,
                                    {'error_message': message})

    retcode, message = player_join_game(current_name=current_username,
                                        target_name=target_username,
                                        current_role=current_role)

    if not retcode:
        return generate_return_data(
            StatusCode.ERR_GAME_PLAYER_JOIN_GAME_FAILED,
            {'error_message': message})
    return generate_return_data(StatusCode.SUCCESS)


def api_game_room_get_players():

    current_username = session_get_username()
    retcode, message = player_get_others(current_username)
    if retcode:

        host, guests = message

        if len(host) > 0:
            host['avatar'] = '/static/favicon.png'

        for guest in guests:
            guest['avatar'] = '/static/favicon.png'

        return generate_return_data(StatusCode.SUCCESS, {
            'host': host,
            'guests': guests
        })
    return generate_return_data(
        StatusCode.ERR_GAME_PLAYER_GET_OTHER_IN_ROOM_FAILED, message)


def api_game_room_player_ready():
    data = flask.request.get_json()
    ready = data.get('ready', None)

    username = session_get_username()
    retcode, message = player_set_ready(username, ready)

    if retcode:
        generate_return_data(StatusCode.SUCCESS, message)
    return generate_return_data(StatusCode.ERR_GAME_PLAYER_SET_READY_FAILED,
                                message)


def api_game_core_image():

    result = {'url': '/static/capoo.png'}
    return generate_return_data(0, result)


def socket_online(websocket):
    try:
        while True:
            message = websocket.receive()
            websocket.send(message)

            print(message)

            if message is not None:
                message = json.loads(message)
                if isinstance(message, dict):
                    username = message.get('username', None)
                    if username is not None:
                        quaryinfo = message.get('quaryinfo', None)
                        if quaryinfo is not None:
                            if quaryinfo == 'firends':
                                print(quaryinfo)

            time.sleep(SOCKET_ONLINE_TIME_INTERVAL)

    except simple_websocket.ConnectionClosed:
        print('break')


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
    '/api/account/approved_application': {
        'view_func': api_account_approved_application,
        'methods': ['POST']
    },
    '/api/game/room/join_game': {
        'view_func': api_game_room_join_game,
        'methods': ['POST']
    },
    '/api/game/room/get_players': api_game_room_get_players,
    '/api/game/room/player_ready': {
        'view_func': api_game_room_player_ready,
        'methods': ['POST']
    },
    '/api/game/core/image': api_game_core_image,
}

backend_websocket = {'/socket/online': socket_online}
