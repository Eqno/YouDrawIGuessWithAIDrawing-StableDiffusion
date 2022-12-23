# -*- coding: utf-8 -*-

import os, flask, datetime
from flask_sock import Sock
from . import frontend, backend, utils

__all__ = ['frontend', 'backend', 'Server']


class Server(object):
    app = None
    sock = None

    hostname = ''
    port = 0
    debug = False

    def __init__(self,
                 name,
                 hostname='127.0.0.1',
                 port=80,
                 template_folder='../app/templates',
                 static_folder='../app/static'):
        self.hostname = hostname
        self.port = port
        self.debug = os.environ['FLASK_ENV'] == 'development'
        self.app = None
        self.sock = None
        self.server = None

        # init frontend and backend
        frontend.frontend_init()
        backend.backend_init()

        # create flask instance
        app = flask.Flask(name,
                          template_folder=template_folder,
                          static_folder=static_folder)
        sock = Sock(app)

        # init session
        app.secret_key = 'session_key_0xdeadbeef'
        app.config['SESSION_TYPE'] = 'filesystem'

        # set global templates
        def make_session_permanent():
            flask.session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(days=1)

        app.context_processor(lambda: utils.template_variables)
        app.before_request(make_session_permanent)

        sock.route('/test')(backend.echo_socket)
        # sock.add_url_rule('/test', None, backend.echo_socket)

        # add pages
        for pages in (frontend.frontend_pages, backend.backend_pages):
            for k, v in pages.items():
                if isinstance(v, dict):
                    app.add_url_rule(k, **v)
                else:
                    app.add_url_rule(k, view_func=v)

        self.app = app
        self.sock = sock

    def run(self):
        self.app.run(host=self.hostname, port=self.port, debug=self.debug)
        self.server.serve_forever()