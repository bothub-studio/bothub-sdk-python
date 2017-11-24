# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class MockTransport(object):
    def __init__(self):
        self.recorded = []
        self.executed = []

    def record(self, data):
        self.recorded.append(data)

    def put(self, url, data):
        self.executed.append(('put', {'url': url, 'data': data}))
        return self.recorded.pop(0) if self.recorded else None

    def get(self, url):
        self.executed.append(('get', {'url': url}))
        return self.recorded.pop(0) if self.recorded else None
