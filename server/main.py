# -*- coding: utf-8 -*-

__import__('os').environ['FLASK_ENV'] = 'development'
from website import Server

def main():

    game_app = Server(game_app_name=__name__)
    game_app.run()

if __name__ == '__main__':
    main()