# -*- coding: utf-8 -*-

import requests_mock
from bothub_client.transports import HttpTransport
from bothub_client.transports import ZmqTransport


class DummySocket(object):
    def __init__(self):
        self.executed = []

    def connect(self, address):
        self.executed.append({'command': 'connect',
                              'args': {'address': address}})

    def send_json(self, data):
        self.executed.append({'command': 'send_json',
                              'args': {'data': data}})

    def send_multipart(self, data):
        self.executed.append({'command': 'send_multipart',
                              'args': {'data': data}})


class DummyContext(object):
    def __init__(self):
        self._socket = None

    def socket(self, sockettype):
        self.sockettype = sockettype
        if not self._socket:
            self._socket = DummySocket()
        return self._socket


def test_http_get_should_invoke_get():
    with requests_mock.mock() as mock:
        mock.get('localhost:8000/path', text='{"ran":true}')
        t = HttpTransport('localhost:8000')
        response = t.get('/path')
        assert response['ran'] is True
        assert mock.called is True


def test_http_post_should_invoke_post():
    with requests_mock.mock() as mock:
        mock.post('localhost:8000/path', text='{"ran":true}')
        t = HttpTransport('localhost:8000')
        t.post('/path', data='[]')
        assert mock.called is True


def test_http_put_should_invoke_put():
    with requests_mock.mock() as mock:
        mock.put('localhost:8000/path', text='{"ran":true}')
        t = HttpTransport('localhost:8000')
        t.put('/path', data='[]')
        assert mock.called is True


def test_zmq_send_json_should_invoke_send():
    context = DummyContext()
    t = ZmqTransport('localhost', context=context)
    t.send_json('mydata')
    assert context._socket.executed == [{'command': 'connect',
                                         'args': {'address': 'localhost'}},
                                        {'command': 'send_json',
                                         'args': {'data': 'mydata'}}]


def test_zmq_send_multipart_should_invoke_send():
    context = DummyContext()
    t = ZmqTransport('localhost', context=context)
    t.send_multipart('mydata')
    assert context._socket.executed == [{'command': 'connect',
                                         'args': {'address': 'localhost'}},
                                        {'command': 'send_multipart',
                                         'args': {'data': 'mydata'}}]
