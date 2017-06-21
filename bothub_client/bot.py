# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class BaseBot(object):
    def __init__(self, channel_client=None, storage_client=None, nlu_client_factory=None, event=None):
        self.channel_client = channel_client
        self.storage_client = storage_client
        self.nlu_client_factory = nlu_client_factory
        self.event = event

    def handle_message(self, event, context):
        raise NotImplementedError()

    def send_message(self, message, user_id=None, channel=None, extra=None):
        self.channel_client.send_message(user_id, message, channel, event=self.event, extra=extra)

    def set_project_data(self, data):
        self.storage_client.set_project_data(data)

    def get_project_data(self):
        return self.storage_client.get_project_data()

    def set_user_data(self, data, user_id=None, channel=None):
        _user_id = user_id or self.event.get('sender', {}).get('id')
        _channel = channel or self.event.get('channel')
        self.storage_client.set_user_data(_channel, _user_id, data)

    def get_user_data(self, user_id=None, channel=None):
        _user_id = user_id or self.event.get('sender', {}).get('id')
        _channel = channel or self.event.get('channel')
        return self.storage_client.get_user_data(_channel, user_id=_user_id)

    def nlu(self, vendor):
        return self.nlu_client_factory.get(vendor)
