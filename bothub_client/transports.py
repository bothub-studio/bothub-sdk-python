# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import requests


class HttpTransport(object):
    def __init__(self):
        self.session = requests.Session()

    def get(self, url, data):
        return self.session.get(url).json()

    def post(self, url, data):
        return self.session.post(url, json=data)

    def put(self, url, data):
        return self.session.put(url, json=data)
