# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


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

    context['channel'] = channel
    context['storage'] = storage

    bot = bot_class(channel_client=channel, storage_client=storage, event=event)
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

    def send_message(self, chat_id, message, channel=None, event=None):
        sender_id = event.get('sender', {}).get('id', None)
        origin_channel = event.get('channel')
        _chat_id = chat_id or sender_id
        _channel = channel or origin_channel
        self.transport.post('/messages', {'channel': _channel, 'receiver': _chat_id, 'message': message, 'event': event})


class ZmqChannelClient(Client):
    def __init__(self, project_id, api_key, base_url, transport=None):
        _transport = transport or ZmqTransport(base_url)
        super(ZmqChannelClient, self).__init__(project_id, api_key, base_url, _transport)

    @staticmethod
    def init_client(context):
        project_id = context.get('project_id')
        api_key = context.get('api_key', '')
        channel_endpoint = context.get('channel', {}).get('endpoint')
        return ZmqChannelClient(project_id, api_key, channel_endpoint)

    def send_message(self, chat_id, message, channel=None, event=None):
        sender_id = event.get('sender', {}).get('id', None)
        origin_channel = event.get('channel')
        _chat_id = chat_id or sender_id
        _channel = channel or origin_channel
        self.transport.send_json({'channel': _channel, 'receiver': _chat_id, 'message': message, 'event': event})


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


class LogClient(object):
    def __init__(self, project_id, api_key, base_url, transport=None):
        self.project_id = project_id
        self.base_url = base_url
        self.api_key = api_key
        self.transport = transport
