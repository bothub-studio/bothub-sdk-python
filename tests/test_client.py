# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import requests_mock

from six import u
from bothub_client.bot import BaseBot
from bothub_client.clients import handle_message
from bothub_client.clients import BaseChannelClient
from bothub_client.clients import ZmqChannelClient
from bothub_client.messages import Message


class Bot(BaseBot):
    def handle_message(self, event, context):
        content = event.get('content')
        self.send_message('hello, you said: {}'.format(content))


class DummyZmqTransport(object):
    def __init__(self):
        self.sent = []

    def send_multipart(self, data):
        self.sent.append(data)


def test_handle_message_should_add_channel_cmd_buff():
    event = {'content': 'hi!',
             'channel': 'mychannel',
             'sender': {'id': 'abcd1234',
                        'name': 'myname'}}

    context = {'channel': {'endpoint': 'http://localhost'}}

    with requests_mock.mock() as m:
        m.post('http://localhost/messages')
        response = handle_message(event, context, Bot)
        assert response['response'] is None
        assert m.called
        assert m.request_history[0].json() == {
            'channel': None,
            'receiver': None,
            'message': 'hello, you said: hi!',
            'event': event,
            'extra': None,
            'context': {'api_key': '', 'project_id': None}
        }


def test_get_channel_obj_should_returns_channel():
    context = {'channel': {'channels': [{'type': 'mychannel'}]}}
    client = BaseChannelClient(10, 'myapikey', 'myurl', context=context)
    channel = client._get_channel_obj('mychannel')
    assert channel == {'type': 'mychannel'}


def test_get_channel_obj_should_returns_none():
    context = {'channel': {'channels': [{'type': 'mychannel'}]}}
    client = BaseChannelClient(10, 'myapikey', 'myurl', context=context)
    channel = client._get_channel_obj('mychannel2')
    assert channel is None


def test_prepare_payload_should_returns_message_data():
    context = {'channel': {'channels': [{'type': 'mychannel'}]}}
    event = {}
    client = BaseChannelClient(10, 'myapikey', 'myurl', context=context)
    message = Message(event)
    data = client._prepare_payload('myid', message, channel='mychannel', event=event)
    assert data == {
        'channel': {'type': 'mychannel'},
        'receiver': 'myid',
        'context': {'project_id': 10, 'api_key': 'myapikey'},
        'event': {},
        'extra': None,
        'message': {
            'model': [],
            'event': {}
        }
    }


def test_zmq_channel_client_init_client_should_return_client():
    context = {'project_id': 1,
               'api_key': 'mykey',
               'channel_endpoint': 'tcp://localhost:1010'}
    transport = DummyZmqTransport()
    client = ZmqChannelClient.init_client(context, transport=transport)
    assert client.api_key == 'mykey'
    assert client.project_id == 1


def test_zmq_channel_client_send_message_should_invoke_transport():
    context = {'project_id': 1,
               'channel': {'endpoint': 'tcp://localhost:1010',
                           'type': 'mychannel',
                           'channels': [{'type': 'mychannel'}]},
               'api_key': 'mykey',
               'channel_endpoint': 'tcp://localhost:1010'}
    event = {'chat_id': '1124',
             'channel': 'mychannel'}
    transport = DummyZmqTransport()
    client = ZmqChannelClient.init_client(context, transport=transport)
    client.send_message('1123', {'message': 'Hello'}, event=event)
    message = transport.sent.pop(0)
    message_str = message[0].decode('utf-8')
    message_json = json.loads(message_str)
    assert message_json == {'receiver': '1123',
                            'message': {'message': 'Hello'},
                            'event': {'chat_id': '1124',
                                      'channel': 'mychannel'},
                            'context': {'api_key': 'mykey',
                                        'project_id': 1},
                            'channel': {'type': 'mychannel'},
                            'extra': None}
