# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import requests


class HttpTransport(object):
    def __init__(self, base_url=''):
        self.session = requests.Session()
        self.base_url = base_url

    def get(self, path):
        return self.session.get(self.base_url+path).json()

    def post(self, path, data=None):
        return self.session.post(self.base_url+path, json=data)

    def put(self, path, data=None):
        return self.session.put(self.base_url+path, json=data)
