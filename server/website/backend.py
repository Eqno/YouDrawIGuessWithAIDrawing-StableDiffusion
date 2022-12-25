# -*- coding: utf-8 -*-

############################### IMPORT ###############################

import os
import sys
import json
import time
import flask
import pathlib
import threading

import logic
from .utils import generate_return_data, StatusCode
from . import consts

sys.path.append(str(consts.cwd / 'model'))
import server_binding as stable_diffusion

############################### PARAMS ###############################

HEARTBEAT_TIMEOUT = 10
HEARTBEAT_INTERVAL = 5
GAMELOOP_INTERVAL = 0.5

msg_data_path = consts.data_base_path / 'msg'
user_data_path = consts.data_base_path / 'user'

info_file_name = 'info.json'

############################## APIS FOR GAME ###############################

# FIXME: using global variables is NOT elegant!
model_instance = None
words = []


def model_init():
    global model_instance
    model_instance = stable_diffusion.Text2image(consts.generated_img_size,
                                                 consts.generated_img_size)


def words_init():
    global words
    if not consts.words_path.exists():
        words = consts.default_words
        with open(consts.words_path, 'w') as f:
            json.dump({'words': words}, fp=f)
    else:
        with open(consts.words_path, 'r') as f:
            json_data = json.load(f)
            words = json_data['words']


def prompt_str_to_list(prompts: str) -> list:
    splited_result = (p.strip() for p in prompts.split(','))
    non_empty_result = list(filter(lambda s: len(s) > 0, splited_result))
    return non_empty_result


def api_core_generate_image():
    username = session_get_username()
    if username is None:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    # TODO: check whether the user is a host
    #assert is_host(username)

    data = flask.request.get_json()
    positive_str = str(data['positive'])
    negative_str = str(data['negative'])
    positive = prompt_str_to_list(positive_str)
    negative = prompt_str_to_list(negative_str)
    positive.append(*consts.default_positive_prompt)
    negative.append(*consts.default_negative_prompt)

    # TODO: generate a random file name and save into game instance
    filename = 'temp'
    status, msg = model_instance.generate_image_with_func_params(
        positive, negative, filename)
    if status:
        return generate_return_data(StatusCode.SUCCESS, {'path': 'TODO'})
    return generate_return_data(StatusCode.ERR_MODEL_UNKNOWN_ERROR,
                                {'message': msg})


############################## HEARTBEAT ###############################

# FIXME: using global variables is NOT elegant!
online_users = {}
gaming_users = {}


def api_heartbeat_imonline():
    global online_users
    username = session_get_username()
    if username is None:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)
    update_time = time.time()
    online_users[username] = update_time
    return generate_return_data(StatusCode.SUCCESS)


def api_heartbeat_imgaming():
    global gaming_users
    username = session_get_username()
    if username is None:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)
    update_time = time.time()
    gaming_users[username] = update_time
    return generate_return_data(StatusCode.SUCCESS)


def user_status_update():
    global online_users
    global gaming_users
    while True:
        now = time.time()
        online_result = {
            k: v
            for k, v in online_users.items() if now - v < HEARTBEAT_TIMEOUT
        }
        gaming_result = {}
        escaped_users = []
        for k, v in gaming_users.items():
            if now - v < HEARTBEAT_TIMEOUT:
                gaming_result[k] = v
            else:
                escaped_users.append(k)
        online_users = online_result
        gaming_users = gaming_result
        print('online: {}'.format(online_users))
        print('gaming: {}'.format(gaming_users))
        print('escaped: {}'.format(escaped_users))
        time.sleep(HEARTBEAT_INTERVAL)


def main_game_loop():
    while True:
        logic.__game_loop__()
        time.sleep(GAMELOOP_INTERVAL)


############################## INITIAL ###############################


def backend_init():
    for _dir in (consts.data_base_path, msg_data_path, user_data_path):
        if not _dir.exists():
            os.mkdir(_dir)

    heartbeat = threading.Thread(target=user_status_update)
    heartbeat.daemon = True
    heartbeat.start()

    gameloop = threading.Thread(target=main_game_loop)
    gameloop.daemon = True
    gameloop.start()


############################# SESSION #############################


def session_get_username():
    return flask.session.get('username', None)


def session_set_username(username: str):
    flask.session['username'] = username


def session_del_username():
    return flask.session.pop('username')


############################ USER DATA ############################


def api_account_username():
    username = session_get_username()

    if username:
        return generate_return_data(StatusCode.SUCCESS, {'username': username})
    return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)


def api_account_userinfo():
    data = flask.request.get_json()
    username = data['username']

    user_file_path = user_data_path / username / info_file_name

    if not user_file_path.exists():
        return generate_return_data(
            StatusCode.ERR_ACCOUNT_USERNAME_NOT_EXISTED)

    with open(user_file_path, 'r') as f:
        raw_user_info = json.load(f)
        userinfo = {}
        userinfo['username'] = raw_user_info['username']
        userinfo['signature'] = raw_user_info.get('signature', '')
        userinfo['ranking'] = raw_user_info.get('ranking',
                                                consts.default_ranking)

        return generate_return_data(StatusCode.SUCCESS, {'userinfo': userinfo})


def api_account_login():
    data = flask.request.get_json()
    username = data['username']
    password = data['password']

    user_info_path = user_data_path / username / info_file_name

    if user_info_path.exists():
        with open(user_info_path, 'r') as f:
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

    user_root_path = user_data_path / username
    user_info_path = user_root_path / info_file_name

    if user_root_path.exists():
        return generate_return_data(StatusCode.ERR_ACCOUNT_USERNAME_EXISTED)
    os.mkdir(user_root_path)

    with open(user_info_path, 'w') as f:
        user_info = {}

        user_info['username'] = username
        user_info['password'] = password

        user_info['ranking'] = consts.default_ranking

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


def api_account_upload_avatar():
    username = session_get_username()
    if username is None:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    data = flask.request.files.get('file', None)
    if data is None:
        return generate_return_data(StatusCode.ERR_SERVER_UNKNOWN)

    avatar = pathlib.Path(user_data_path / username / consts.avatar_file_name)
    with open(avatar, 'wb') as f:
        data.save(f)
    return generate_return_data(StatusCode.SUCCESS)


def api_account_update_signature():
    username = session_get_username()
    if username is None:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    data = flask.request.get_json()
    signature = data['signature']
    user_filepath = user_data_path / username / info_file_name

    with open(user_filepath, 'r+') as f:
        user_info = json.load(f)
        user_info['signature'] = signature
        f.seek(0)
        json.dump(user_info, fp=f)
        f.truncate()
    return generate_return_data(StatusCode.SUCCESS)


############################ FRIENDS ############################


def api_account_add_friend():
    data = flask.request.get_json()

    current_username = session_get_username()
    current_filepath = user_data_path / current_username / info_file_name

    if not current_filepath.exists():
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    target_username = data['username']
    target_filepath = user_data_path / target_username / info_file_name

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


def __get_user_status(username: str):
    if username in gaming_users:
        return 'gaming'
    if username in online_users:
        return 'online'
    return 'offline'


def api_account_get_friends():
    username = session_get_username()

    if not username:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    user_file_path = user_data_path / username / info_file_name
    if not user_file_path.exists():
        return generate_return_data(StatusCode.ERR_SERVER_UNKNOWN)

    with open(user_file_path, 'r') as f:
        user_info = json.load(f)
        friends = list({
            'name': name,
            'status': __get_user_status(name)
        } for name in user_info.get('friends', []))
        return generate_return_data(
            StatusCode.SUCCESS, {
                'friends':
                friends,
                'applications_sent':
                user_info.get('applications_sent', []),
                'applications_received':
                user_info.get('applications_received', []),
            })


def api_account_approved_application():
    data = flask.request.get_json()

    current_username = session_get_username()
    current_filepath = user_data_path / current_username / info_file_name

    if not current_filepath.exists():
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    target_username = data['username']
    target_filepath = user_data_path / target_username / info_file_name

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


# msg: {'username': str, 'content': str, 'timestamp': int}


def get_chat_filename(users) -> str:
    return '.'.join(sorted(users)) + '.json'


def api_account_get_messages():
    # {'username': str, 'timestamp': int}
    # get messages that later than the `timestamp`
    username = session_get_username()
    if username is None:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    data = flask.request.get_json()
    target_username = data['username']
    target_user_path = user_data_path / target_username
    if not target_user_path.exists():
        return generate_return_data(
            StatusCode.ERR_ACCOUNT_USERNAME_NOT_EXISTED)

    chat_filename = get_chat_filename([username, target_username])
    chat_path = msg_data_path / chat_filename

    if not chat_path.exists():
        return generate_return_data(StatusCode.SUCCESS, {'messages': []})

    timestamp = int(data.get('timestamp', 0))

    with open(chat_path, 'r') as f:
        json_data = json.load(f)
        messages = json_data.get('messages', [])
        if timestamp > 0:
            messages = [
                msg for msg in messages if msg['timestamp'] > timestamp
            ]
        return generate_return_data(StatusCode.SUCCESS, {'messages': messages})


def api_account_send_message():
    username = session_get_username()
    if username is None:
        return generate_return_data(StatusCode.ERR_ACCOUNT_NOT_LOGINED)

    data = flask.request.get_json()
    target_username = data['username']
    target_user_path = user_data_path / target_username
    if not target_user_path.exists():
        return generate_return_data(
            StatusCode.ERR_ACCOUNT_USERNAME_NOT_EXISTED)

    chat_filename = get_chat_filename([username, target_username])
    chat_path = msg_data_path / chat_filename

    content = data['content']
    timestamp = int(time.time())

    with open(chat_path, 'r+') as f:
        json_data = {}
        try:
            json_data = json.load(f)
        except:
            pass

        messages = list(json_data.get('messages', []))
        messages.append({
            'username': username,
            'content': content,
            'timestamp': timestamp
        })

        f.seek(0)
        json.dump({'messages': messages}, fp=f)
        f.truncate()

        return generate_return_data(StatusCode.SUCCESS)


############################ GAME ROOM ############################


def api_game_room_get_players():

    current_username = session_get_username()
    retcode, message = logic.player_get_others(current_username)

    if retcode:
        return generate_return_data(StatusCode.SUCCESS, message)
    return generate_return_data(
        StatusCode.ERR_GAME_PLAYER_GET_OTHER_IN_ROOM_FAILED, message)


def api_game_room_join_game():

    data = flask.request.get_json()

    current_username = session_get_username()
    target_username = data.get('username', None)
    current_role = data.get('role', None)

    retcode, message = logic.create_player_instance(current_username)
    if not retcode:
        return generate_return_data(StatusCode.ERR_GAME_PLAYER_NUM_EXCEED_MAX,
                                    {'error_message': message})

    retcode, message = logic.player_join_game(current_name=current_username,
                                              target_name=target_username,
                                              current_role=current_role)

    if not retcode:
        return generate_return_data(
            StatusCode.ERR_GAME_PLAYER_JOIN_GAME_FAILED,
            {'error_message': message})
    return generate_return_data(StatusCode.SUCCESS)


def api_game_room_player_ready():

    data = flask.request.get_json()
    ready = data.get('ready', None)

    username = session_get_username()
    retcode, message = logic.player_set_ready(username, ready)

    if retcode:
        return generate_return_data(StatusCode.SUCCESS, message)
    return generate_return_data(StatusCode.ERR_GAME_PLAYER_SET_READY_FAILED,
                                message)


############################ GAME CORE ############################


def api_game_core_submit_info():

    data = flask.request.get_json()

    info = data.get('info', None)
    negative = data.get('negative', None)
    rand_seed = data.get('rand_seed', None)

    if info is None:
        return generate_return_data(
            StatusCode.ERR_GAME_DID_NOT_COMMIT_ANITHING)

    username = session_get_username()
    retcode, message = logic.game_submit_info(username, info, negative,
                                              rand_seed)
    if retcode:
        return generate_return_data(StatusCode.SUCCESS)
    return generate_return_data(StatusCode.ERR_GAME_COMMIT_INFO_FAILED,
                                message)


def api_game_core_get_info():

    username = session_get_username()
    retcode, message = logic.game_get_info(username)

    if retcode:
        return generate_return_data(StatusCode.SUCCESS, {'message': message})
    return generate_return_data(StatusCode.ERR_GAME_GET_INFO_FAILED, message)


def api_game_core_image():

    result = {'url': '/static/capoo.png'}
    return generate_return_data(StatusCode.SUCCESS, result)


backend_pages = {
    '/api/heartbeat/imonline': api_heartbeat_imonline,
    '/api/heartbeat/imgaming': api_heartbeat_imgaming,
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
    '/api/account/upload_avatar': {
        'view_func': api_account_upload_avatar,
        'methods': ['POST']
    },
    '/api/account/update_signature': {
        'view_func': api_account_update_signature,
        'methods': ['POST']
    },
    '/api/account/get_messages': {
        'view_func': api_account_get_messages,
        'methods': ['POST']
    },
    '/api/account/send_message': {
        'view_func': api_account_send_message,
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
    '/api/game/core/submit_info': {
        'view_func': api_game_core_submit_info,
        'methods': ['POST']
    },
    '/api/game/core/get_info': api_game_core_get_info,
    '/api/game/core/image': api_game_core_image,
}
