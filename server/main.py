# -*- coding: utf-8 -*-

__import__('os').environ['FLASK_ENV'] = 'development'
import flask
from website import frontend, backend, utils


def app_init():
    app = flask.Flask(__name__,
                      template_folder='../app/templates',
                      static_folder='../app/static')
    # init
    app.config["DEBUG"] = True
    app.config["PORT"] = 80

    # set global templates
    app.context_processor(lambda: utils.template_variables)

    # add pages
    for pages in (frontend.frontend_pages, backend.backend_pages):
        for k, v in pages.items():
            if isinstance(v, dict):
                app.add_url_rule(k, **v)
            else:
                app.add_url_rule(k, view_func=v)

    return app


if __name__ == '__main__':
    app = app_init()
    app.run('127.0.0.1')
