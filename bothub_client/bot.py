# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

from bothub_client.intent import IntentState
from bothub_client.dispatcher import DefaultDispatcher


class BaseBot(object):
    '''A base Bot class'''

    def __init__(self, channel_client=None, storage_client=None, nlu_client_factory=None, event=None):
        '''Initialize an object

        :param channel_client: a ChannelClient object
        :type channel_client: bothub_client.clients.ChannelClient
        :param storage_client: a StorageClient object
        :type storage_client: bothub_client.clients.StorageClient
        :param nlu_client_factory: an NLU client factory object
        :type nlu_client_factory: bothub_client.clients.NluClientFactory
        :param event: an event which messenger platform sent
        :type event: dict'''
        self.channel_client = channel_client
        self.storage_client = storage_client
        self.nlu_client_factory = nlu_client_factory
        self.event = event

    def handle_message(self, event, context):
        '''Handle a message which messenger platform sent

        :param event: an event which messenger platform sent
        :type event: dict
        :param context: a context Bot runs
        :type context: dict'''
        content = event.get('content')

        bot_dir_path = os.path.dirname(os.path.realpath(__file__))
        yml_path = os.path.join(bot_dir_path, os.pardir, 'bothub.yml')
        if os.path.isfile(yml_path):
            intent_slots = IntentState.load_intent_slots_from_yml(yml_path)
        else:
            intent_slots = []

        state = IntentState(self, intent_slots)
        dispatcher = DefaultDispatcher(self, state)
        dispatcher.dispatch(event, context)

    def send_message(self, message, chat_id=None, channel=None, extra=None):
        '''Send a message to an user or chatroom.

        :param message: a message to send. it can be a str text or Message class object
        :type message: str, bothub_client.messages.Message
        :return: None'''
        self.channel_client.send_message(chat_id, message, channel, event=self.event, extra=extra)

    def set_project_data(self, data):
        '''Set project properties

        :param data: a dict to store
        :type data: dict
        :return: None'''
        self.storage_client.set_project_data(data)

    def get_project_data(self):
        '''Returns project properties

        :return: a properties dict
        :rtype: dict'''
        return self.storage_client.get_project_data()

    def set_user_data(self, data, user_id=None, channel=None):
        '''Set user properties

        :param data: a dict to store
        :type data: dict
        :param user_id: an user id to store data
        :type user_id: str, int
        :param channel: a name of messaging platform
        :type channel: str
        :return: None'''
        _user_id = user_id or self.event.get('sender', {}).get('id')
        _channel = channel or self.event.get('channel')
        self.storage_client.set_user_data(_channel, _user_id, data)

    def get_user_data(self, user_id=None, channel=None):
        '''Returns user properties

        :param user_id: an user id to store data
        :type user_id: str, int
        :param channel: a name of messaging platform
        :type channel: str
        :return: a properties dict
        :rtype: dict'''
        _user_id = user_id or self.event.get('sender', {}).get('id')
        _channel = channel or self.event.get('channel')
        return self.storage_client.get_user_data(_channel, user_id=_user_id)

    def nlu(self, vendor):
        '''Returns NLU client

        :param vendor: a NLU vendor name
        :type vendor: str
        :return: a NLU client
        :rtype: bothub_client.client.NluClient'''
        return self.nlu_client_factory.get(vendor)
