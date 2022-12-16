# -*- coding: utf-8 -*-

import os

os.environ['FLASK_ENV'] = 'development'
import json
import flask
from enum import IntEnum

app = flask.Flask(__name__)

# ---- init ----


@app.context_processor
def template_global_variables():
    vars = {}
    vars['title_suffix'] = '你说我猜'
    vars['app_name'] = '你说我猜'
    vars['home_page'] = '首页'
    vars['game_menu'] = '游戏'
    vars['match_mode'] = '匹配模式'
    vars['custom_mode'] = '自定义模式'
    vars['ranking'] = '排行榜'
    vars['about_page'] = '关于'
    vars['login'] = '登录'
    vars['register'] = '注册'
    vars['username'] = '账号'
    vars['password'] = '密码'
    vars['please_input_username'] = '请输入账号'
    vars['guess_the_image'] = '快来猜图片！'
    vars['hint_prefix'] = '提示：'
    vars['submit'] = '提交'
    vars['abandon'] = '放弃'
    return vars


# ---- front end ----


@app.route('/')
def page_index():
    return flask.render_template('index.html',
                                 title='首页',
                                 base_url=flask.request.base_url)


@app.route('/login')
def page_login():
    return flask.render_template('login.html',
                                 title='登录',
                                 base_url=flask.request.base_url)


@app.route('/game')
def page_game():
    return flask.render_template('game.html',
                                 title='游戏',
                                 base_url=flask.request.base_url)


@app.route('/image/<filename>')
def image_get_image(filename):
    return flask.send_file('static/' + filename, mimetype='image/png')


# --- utils ---


class StatusCode(IntEnum):
    SUCCESS = 0
    ERR_SERVER_UNKNOWN = 100
    ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG = 200
    ERR_ACCOUNT_USERNAME_EXISTED = 201


error_msg = {
    StatusCode.SUCCESS: '',
    StatusCode.ERR_SERVER_UNKNOWN: '服务器异常',
    StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG: '用户名或密码错误',
}

default_errno = StatusCode.ERR_SERVER_UNKNOWN

user_database = {
    # admin, administrator
    'admin': '200ceb26807d6bf99fd6f4f0d1ca54d4'
}


def generate_return_data(errno: StatusCode, res=None) -> str:
    if errno not in error_msg:
        errno = default_errno
    ret = {'code': int(errno), 'message': error_msg[errno]}
    if isinstance(res, dict):
        ret.update(res)
    return json.dumps(ret)


# ---- back end ----


@app.route('/api/account/login', methods=['POST'])
def api_account_login():
    data = flask.request.get_json()
    username = data['username']
    password = data['password']
    if username in user_database:
        if user_database[username] == password:
            return generate_return_data(StatusCode.SUCCESS)
    return generate_return_data(
        StatusCode.ERR_ACCOUNT_USERNAME_OR_PASSWORD_WRONG)


@app.route('/api/game/core/image')
def api_game_core_image():
    result = {'url': '/static/capoo.png'}
    return generate_return_data(0, result)


if __name__ == '__main__':
    app.run('127.0.0.1', 80, debug=True)
