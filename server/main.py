# -*- coding: utf-8 -*-

__import__('os').environ['FLASK_ENV'] = 'development'
from website import Server

def main():
    server = Server(__name__)
    server.run()

if __name__ == '__main__':
    main()
