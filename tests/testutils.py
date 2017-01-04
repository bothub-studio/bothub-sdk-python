# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class MockTransport(object):
    def __init__(self):
        self.recorded = []

    def record(self, data):
        self.recorded.append(data)

    def put(self, url, data):
        return self.recorded.pop(0) if self.recorded else None

    def get(self, url, data):
        return self.recorded.pop(0) if self.recorded else None
