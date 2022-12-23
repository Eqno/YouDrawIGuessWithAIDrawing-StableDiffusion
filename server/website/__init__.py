# -*- coding: utf-8 -*-

import os, flask, datetime
from threading import Thread
from gevent import monkey, pywsgi
from flask_sockets import Sockets
from . import frontend, backend, utils
from geventwebsocket.handler import WebSocketHandler

__all__ = ['frontend', 'backend', 'Server']

class Server(object):
    game_app = None
    heart_app = None

    hostname = ''
    game_port = 0
    heart_port = 0
    debug = False

    def __init__(self,
                 game_app_name,
                 heart_app_name,
                 hostname='127.0.0.1',
                 game_port=80,
                 heart_port=81,
                 template_folder='../app/templates',
                 static_folder='../app/static'):
        self.hostname = hostname
        self.game_port = game_port
        self.heart_port = heart_port
        self.debug = os.environ['FLASK_ENV'] == 'development'

        # init game app server
        self.__init_game_app__(game_app_name,
                               template_folder,
                               static_folder)

        # init hear app server
        self.__init_heart_app__(heart_app_name)

    def __init_game_app__(self,
                          game_app_name,
                          template_folder='../app/templates',
                          static_folder='../app/static'):

        # init frontend and backend
        frontend.frontend_init()
        backend.backend_init()

        # create flask instance
        game_app = flask.Flask(game_app_name,
                               template_folder=template_folder,
                               static_folder=static_folder)

        # init session
        game_app.secret_key = 'session_key_0xdeadbeef'
        game_app.config['SESSION_TYPE'] = 'filesystem'

        # set global templates
        def make_session_permanent():
            flask.session.permanent = True
            game_app.permanent_session_lifetime = datetime.timedelta(days=1)

        game_app.context_processor(lambda: utils.template_variables)
        game_app.before_request(make_session_permanent)

        # add pages
        for pages in (frontend.frontend_pages, backend.backend_pages):
            for k, v in pages.items():
                if isinstance(v, dict):
                    game_app.add_url_rule(k, **v)
                else:
                    game_app.add_url_rule(k, view_func=v)
        
        self.game_app = game_app
    
    def __init_heart_app__(self, heart_app_name):

        # init socket io
        monkey.patch_all()

        # create flask instance
        heart_app = flask.Flask(heart_app_name)

        # create sockets instance
        sockets = Sockets(heart_app)

        # add socks
        for k, v in backend.backend_socks.items():
            sockets.add_url_rule(k, _=None, f=v, websocket=True)

        self.heart_app = heart_app

    def run(self):

        Thread(target=lambda: self.game_app.run(self.hostname, port=self.game_port, debug=self.debug)).start()
        server = pywsgi.WSGIServer((self.hostname, self.heart_port), self.heart_app, handler_class=WebSocketHandler)
        server.serve_forever()
        