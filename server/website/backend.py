# -*- coding: utf-8 -*-

import flask
from .utils import generate_return_data, StatusCode

user_database = {
    # admin, administrator
    'admin': '200ceb26807d6bf99fd6f4f0d1ca54d4'
}


def api_account_login():
    data = flask.request.get_json()
    username = data['username']
    password = data['password']
    if username in user_database:
        if user_database[username] == password:
            return generate_return_data(StatusCode.SUCCESS)
    return generate_return_data(
        StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG)


def api_game_core_image():
    result = {'url': '/static/capoo.png'}
    return generate_return_data(0, result)


backend_pages = {
    '/api/account/login': {
        'view_func': api_account_login,
        'methods': ['POST']
    },
    '/api/game/core/image': api_game_core_image,
}