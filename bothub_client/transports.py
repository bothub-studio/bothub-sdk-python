# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import requests
import zmq


class HttpTransport(object):
    def __init__(self, base_url=''):
        self.session = requests.Session()
        self.base_url = base_url

    def get(self, path):
        return self.session.get('{}{}'.format(self.base_url, path)).json()

    def post(self, path, data=None):
        return self.session.post('{}{}'.format(self.base_url, path), json=data)

    def put(self, path, data=None):
        return self.session.put('{}{}'.format(self.base_url, path), json=data)


class ZmqTransport(object):
    def __init__(self, address):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(address)

    def send_json(self, data):
        return self.socket.send_json(data)

    def send_multipart(self, data):
        return self.socket.send_multipart(data)
