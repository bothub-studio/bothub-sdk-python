# -*- coding: utf-8 -*-

import json
from collections import namedtuple
from bothub_client.dispatcher import DefaultDispatcher
from bothub_client.intent import Intent
from bothub_client.intent import Slot
from bothub_client.intent import IntentState
from bothub_client.decorators import command
from bothub_client.decorators import intent
from bothub_client.decorators import channel

Executed = namedtuple('Executed', ['command', 'args'])


class MockBot(object):
    def __init__(self):
        self.data = {}
        self.executed = []
        self.sent = []

    def get_user_data(self):
        return self.data

    def set_user_data(self, data):
        data_json_str = json.dumps(data)
        json_data = json.loads(data_json_str)
        self.data.update(**json_data)

    @channel()
    def on_default(self, *args):
        self.executed.append(Executed('on_default', args))

    def send_message(self, message):
        self.sent.append(message)

    @intent('credentials')
    def set_credentials(self, event, context, answers):
        self.executed.append(Executed('set_credentials', (answers['app_id'], answers['app_secret'])))

    @command('hello')
    def hello(self, event, context, args):
        self.executed.append(Executed('hello', [event, context]))


def fixture_intent_slots():
    return [
        Intent('credentials', None, [
            Slot('app_id', None, 'Please tell me your app ID', 'string'),
            Slot('app_secret', None, 'Please tell me your app secret', 'string'),
        ]),
        Intent('address', None, [
            Slot('country', None, 'Please tell me your country', 'string'),
            Slot('city', None, 'Please tell me your city', 'string'),
            Slot('road', None, 'Please tell me your road address', 'string'),
        ])
    ]


def test_simple_message_dispatch_should_call_default_channel_handler():
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)

    event = {'content': 'hello', 'channel': 'fakechannel'}
    dispatcher.dispatch(event, None)

    executed = bot.executed.pop(0) # type: Executed
    assert executed.command == 'on_default'
    assert executed.args == (event, None)


def test_simple_message_dispatch_should_call_execute_command():
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)

    event = {'content': '/hello', 'channel': 'fakechannel'}
    dispatcher.dispatch(event, None)

    executed = bot.executed.pop(0) # type: Executed
    assert executed.command == 'hello'
    assert executed.args == [event, None]
