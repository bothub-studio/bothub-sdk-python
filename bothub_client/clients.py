# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json

from bothub_client.transports import HttpTransport
from bothub_client.transports import ZmqTransport


def get_channel_client(context):
    scheme_to_channel_client = {
        'http': ChannelClient,
        'https': ChannelClient,
        'tcp': ZmqChannelClient,
    }

    endpoint = context.get('channel', {}).get('endpoint', 'http:')
    scheme = endpoint.split(':')[0]
    client_class = scheme_to_channel_client.get(scheme, ZmqChannelClient)
    return client_class.init_client(context)


def handle_message(event, context, bot_class):
    channel = get_channel_client(context)
    storage = StorageClient.init_client(context, event=event)
    nlu_client_factory = NluClientFactory(context)

    bot = bot_class(channel_client=channel, storage_client=storage, nlu_client_factory=nlu_client_factory, event=event)
    response = bot.handle_message(event, context)
    return {'response': response}


class Client(object):
    def __init__(self, project_id, api_key, base_url, transport=None):
        self.project_id = project_id
        self.base_url = base_url
        self.api_key = api_key
        self.transport = transport or HttpTransport(base_url)


class ChannelClient(Client):
    def __init__(self, project_id, api_key, base_url, transport=None):
        _transport = transport or HttpTransport
        super(ChannelClient, self).__init__(project_id, api_key, base_url, transport)

    @staticmethod
    def init_client(context):
        project_id = context.get('project_id')
        api_key = context.get('api_key', '')
        channel_endpoint = context.get('channel', {}).get('endpoint')
        return ChannelClient(project_id, api_key, channel_endpoint)

    def send_message(self, chat_id, message, channel=None, event=None, extra=None):
        sender_id = event.get('sender', {}).get('id', None)
        origin_channel = event.get('channel')
        _chat_id = chat_id or sender_id
        _channel = channel or origin_channel
        self.transport.post('/messages', {
            'channel': _channel,
            'receiver': _chat_id,
            'message': message,
            'event': event,
            'context': {
                'project_id': self.project_id,
                'api_key': self.api_key
            },
            'extra': extra
        })


class ZmqChannelClient(Client):
    def __init__(self, project_id, api_key, base_url, transport=None, context=None):
        _transport = transport or ZmqTransport(base_url)
        self.context = context
        super(ZmqChannelClient, self).__init__(project_id, api_key, base_url, _transport)

    @staticmethod
    def init_client(context):
        project_id = context.get('project_id')
        api_key = context.get('api_key', '')
        channel_endpoint = context.get('channel', {}).get('endpoint')
        return ZmqChannelClient(project_id, api_key, channel_endpoint, context=context)

    def get_channel_obj(self, channel_type):
        channels = self.context['channel']['channels']
        for c in channels:
            if c['type'] == channel_type:
                return c

    def send_message(self, chat_id, message, channel=None, event=None, extra=None):
        sender_id = event.get('sender', {}).get('id', None)
        origin_channel = event.get('channel')
        _chat_id = chat_id or sender_id
        channel_type = channel or origin_channel
        _channel = self.get_channel_obj(channel_type)
        data = {
            'channel': _channel,
            'receiver': _chat_id,
            'message': message,
            'event': event,
            'context': {
                'project_id': self.project_id,
                'api_key': self.api_key
            },
            'extra': extra
        }
        self.transport.send_multipart([json.dumps(data).encode('utf8')])


class ConsoleChannelClient(Client):
    def __init__(self):
        super(ConsoleChannelClient, self).__init__(None, None, None)

    def send_message(self, chat_id, message, channel=None, event=None):
        _channel = '[{}] '.format(chat_id) if channel else ''
        _channel = '[{}:{}] '.format(channel, chat_id) if channel is not None else _channel
        print('{}{}'.format(_channel, message))


class StorageClient(Client):
    def __init__(self, project_id, api_key, base_url, transport=None, user=None):
        super(StorageClient, self).__init__(project_id, api_key, base_url, transport)
        self.current_user = user

    @staticmethod
    def init_client(context, event=None, transport=None):
        project_id = context.get('project_id')
        api_key = context.get('api_key', '')
        storage_endpoint = context.get('storage', {}).get('endpoint')
        user = None if not event else (event['channel'], event['sender']['id'])
        return StorageClient(project_id, api_key, storage_endpoint, transport=transport, user=user)

    def set_project_data(self, data):
        self.transport.put(
            '/projects/{}'.format(self.project_id),
            {'data': data},
        )

    def get_project_data(self):
        return self.transport.get(
            '/projects/{}'.format(self.project_id),
        ).get('data') or {}

    def set_user_data(self, channel, user_id, data):
        self.transport.put(
            '/projects/{}/channels/{}/users/{}'.format(self.project_id, channel, user_id),
            {'data': data},
        )

    def get_user_data(self, channel, user_id):
        return self.transport.get(
            '/projects/{}/channels/{}/users/{}'.format(self.project_id, channel, user_id)
        ).get('data') or {}

    def set_current_user_data(self, data):
        channel, user_id = self.current_user
        self.set_user_data(channel, user_id, data)

    def get_current_user_data(self):
        channel, user_id = self.current_user
        return self.get_user_data(channel, user_id)


class LocMemStorageClient(Client):
    def __init__(self, user=None):
        super(LocMemStorageClient, self).__init__(None, None, None)
        self.current_user = user
        self.project_storage = {}
        self.user_storage = {}

    def set_project_data(self, data):
        self.project_storage.update(**data)

    def get_project_data(self):
        return self.project_storage

    def set_user_data(self, channel, user_id, data):
        self.user_storage.update(**data)

    def get_user_data(self, channel, user_id):
        return self.user_storage

    def set_current_user_data(self, data):
        channel, user_id = self.current_user
        self.set_user_data(channel, user_id, data)

    def get_current_user_data(self):
        channel, user_id = self.current_user
        return self.get_user_data(channel, user_id)


class NluClient(object):
    def get_response(self, message):
        raise NotImplementedError()


class ApiAiNluClient(NluClient):
    def __init__(self, api_key):
        self.api_key = api_key
        apiai_module = __import__('apiai')
        self.apiai = apiai_module.ApiAI(api_key)

    def parse_response(self, response):
        action = NluAction(
            response.get('result').get('action'),
            response.get('result').get('parameters'),
            response.get('result').get('actionIncomplete')
        )
        next_message = response.get('result').get('fulfillment', {}).get('speech')
        return NluResponse(response, next_message, action)

    def ask(self, message):
        request = self.apiai.text_request()
        request.query = message
        content = request.getresponse().read().decode('utf-8')
        response = json.loads(content)
        return self.parse_response(response)


class NluClientFactory(object):
    NAME_TO_CLIENT = {
        'apiai': ApiAiNluClient
    }

    def __init__(self, context):
        self.integrations_params = context.get('nlu')

    def get(self, vendor):
        return self.NAME_TO_CLIENT.get(vendor)(**self.integrations_params.get(vendor))


class NluAction(object):
    def __init__(self, intent=None, parameters=None, action_incomplete=True):
        self.intent = intent
        self.parameters = parameters or {}
        self.completed = not action_incomplete

    def __repr__(self):
        return "<NluAction '{}', completed: {}, args: {}>".format(
            self.intent,
            self.completed,
            self.parameters
        )


class NluResponse(object):
    def __init__(self, response, next_message=None, action=None):
        self.raw_response = response
        self.action = action
        self.next_message = next_message
