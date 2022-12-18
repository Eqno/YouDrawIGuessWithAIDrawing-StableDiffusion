# -*- coding: utf-8 -*-

__import__('os').environ['FLASK_ENV'] = 'development'
import website


def main():
    app = website.Server(name=__name__)
    app.run()


if __name__ == '__main__':
    main()
