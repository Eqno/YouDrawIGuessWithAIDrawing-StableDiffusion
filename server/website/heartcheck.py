# # -*- coding: utf-8 -*-

# from flask import Flask, jsonify, request  # 引入核心处理模块
# import json
# from flask_sockets import Sockets
# import time
# import sys
# import os
# from gevent import monkey
# from gevent import pywsgi
# from geventwebsocket.handler import WebSocketHandler

# print('已进入')

# sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
# sys.path.append("..")

# monkey.patch_all()

# sockets = Sockets(app)

# now = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))

# @sockets.route('/test')
# def echo_socket(ws):
#     while not ws.closed:
#         ws.send(str(111111111))
#         message = ws.receive()
#         if message is not None:
#             print("%s receive msg==> " % now, str(json.dumps(message)))
#             ws.send(str(json.dumps(message)))
#         else: print(now, "no receive")

# class Server:

#     def run(self):
        
#         server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
#         print('server start')
#         server.serve_forever()