# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


from bothub_client.transports import HttpTransport


def handle_message(event, context, bot_class):
    channel = ChannelClient.init_client(context)
    storage = StorageClient.init_client(context, event=event)

    context['channel'] = channel
    context['storage'] = storage

    bot = bot_class(channel_client=channel, storage_client=storage, event=event)
    result = bot.handle_message(event, context)
    return {'result': result, 'proxy': channel.cmd_buff}


class Client(object):
    def __init__(self, project_id, api_key, base_url, transport=None):
        self.project_id = project_id
        self.base_url = base_url
        self.api_key = api_key
        self.transport = transport or HttpTransport(base_url)


class ChannelClient(Client):
    def __init__(self, project_id, api_key, base_url, transport=None):
        super(ChannelClient, self).__init__(project_id, api_key, base_url, transport)
        self.cmd_buff = []

    @staticmethod
    def init_client(context):
        project_id = context.get('project_id')
        api_key = context.get('api_key', '')
        channel_endpoint = context.get('channel', {}).get('endpoint')
        return ChannelClient(project_id, api_key, channel_endpoint)

    def respond_message(self, message):
        self.cmd_buff.append({'chat_id': None, 'message': message, 'channel': None})

    def send_message(self, chat_id, message, channel=None):
        self.cmd_buff.append({'chat_id': chat_id, 'message': message, 'channel': channel})


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


class LogClient(object):
    def __init__(self, project_id, api_key, base_url, transport=None):
        self.project_id = project_id
        self.base_url = base_url
        self.api_key = api_key
        self.transport = transport
