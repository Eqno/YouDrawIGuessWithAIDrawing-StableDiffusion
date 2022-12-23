# -*- coding: utf-8 -*-

__import__('os').environ['FLASK_ENV'] = 'development'
from website import Server

def main():

    server = Server(game_app_name=__name__, heart_app_name=__name__+'_heart')
    server.run()

if __name__ == '__main__':
    main()