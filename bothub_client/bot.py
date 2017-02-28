# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class BaseBot(object):
    def __init__(self, channel_client=None, storage_client=None, event=None):
        self.channel_client = channel_client
        self.storage_client = storage_client
        self.event = event
        self.current_user_id = event.get('sender') if event else None
        self.current_channel = event.get('channel') if event else None

    def handle_message(self, event, context):
        raise NotImplementedError()

    def send_message(self, message, user_id=None, channel=None):
        _user_id = user_id or self.current_user_id
        _channel = channel or self.current_channel
        self.channel_client.send_message(_user_id, message, _channel)

    def set_project_data(self, data):
        self.storage_client.set_project_data(data)

    def get_project_data(self):
        return self.storage_client.get_project_data()

    def set_user_data(self, data, user_id=None, channel=None):
        _user_id = user_id or self.current_user_id
        _channel = channel or self.current_channel
        self.storage_client.set_user_data(data, user_id=_user_id, channel=_channel)

    def get_user_data(self, user_id=None, channel=None):
        _user_id = user_id or self.current_user_id
        _channel = channel or self.current_channel
        return self.storage_client.get_user_data(user_id=_user_id, channel=_channel)
