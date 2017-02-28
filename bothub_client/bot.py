# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class BaseBot(object):
    def __init__(self, channel_client=None, storage_client=None, event=None):
        self.channel_client = channel_client
        self.storage_client = storage_client
        self.event = event

    def handle_message(self, event, context):
        raise NotImplementedError()

    def send_message(self, message, user_id=None, channel=None):
        self.channel_client.send_message(user_id, message, channel)

    def set_project_data(self, data):
        self.storage_client.set_project_data(data)

    def get_project_data(self):
        return self.storage_client.get_project_data()

    def set_user_data(self, data, user_id=None, channel=None):
        self.storage_client.set_user_data(data, user_id=user_id, channel=channel)

    def get_user_data(self, user_id=None, channel=None):
        return self.storage_client.get_user_data(user_id=user_id, channel=channel)
