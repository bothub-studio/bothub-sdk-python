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


class MockOldStyleBot(object):
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

    def on_default(self, *args):
        self.executed.append(Executed('on_default', args))

    def send_message(self, message):
        self.sent.append(message)

    def set_credentials(self, event, context, answers):
        self.executed.append(Executed('set_credentials', (answers['app_id'], answers['app_secret'])))

    def on_hello(self, event, context, *args):
        self.executed.append(Executed('hello', [event, context]))


class MockNewStyleBot(object):
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
    def default(self, *args):
        self.executed.append(Executed('default', args))

    def send_message(self, message):
        self.sent.append(message)

    @intent('credentials')
    def set_credentials(self, event, context, answers):
        self.executed.append(Executed('set_credentials', (event, context, answers)))

    @command('hello')
    def hello(self, event, context, args):
        self.executed.append(Executed('hello', [event, context]))


def fixture_intent_slots():
    return [
        Intent('credentials', None, [
            Slot('app_id', 'Please tell me your app ID', None, 'string'),
            Slot('app_secret', 'Please tell me your app secret', None, 'string'),
        ]),
        Intent('address', None, [
            Slot('country', 'Please tell me your country', None, 'string'),
            Slot('city', 'Please tell me your city', None, 'string'),
            Slot('road', 'Please tell me your road address', None, 'string'),
        ])
    ]


def test_simple_message_dispatch_should_call_default_channel_handler():
    bot = MockNewStyleBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)

    event = {'content': 'hello', 'channel': 'fakechannel'}
    dispatcher.dispatch(event, None)

    executed = bot.executed.pop(0) # type: Executed
    assert executed.command == 'default'
    assert executed.args == (event, None)


def test_simple_message_dispatch_should_call_execute_command():
    bot = MockNewStyleBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)

    event = {'content': '/hello', 'channel': 'fakechannel'}
    dispatcher.dispatch(event, None)

    executed = bot.executed.pop(0) # type: Executed
    assert executed.command == 'hello'
    assert executed.args == [event, None]


def test_simple_message_dispatch_should_call_intent_complete_handler():
    bot = MockNewStyleBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)

    event1 = {'content': '/intent credentials', 'channel': 'fakechannel'}
    dispatcher.dispatch(event1, None)

    event2 = {'content': 'myid', 'channel': 'fakechannel'}
    dispatcher.dispatch(event2, None)
    event3 = {'content': 'mysecret', 'channel': 'fakechannel'}
    dispatcher.dispatch(event3, None)

    executed = bot.executed.pop(0) # type: Executed
    assert executed.command == 'set_credentials'
    assert executed.args == (event3, None, {'app_id': 'myid', 'app_secret': 'mysecret'})


def test_simple_message_old_style_dispatch_should_call_default_channel_handler():
    bot = MockOldStyleBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)

    event = {'content': 'hello', 'channel': 'fakechannel'}
    dispatcher.dispatch(event, None)

    executed = bot.executed.pop(0) # type: Executed
    assert executed.command == 'on_default'
    assert executed.args == (event, None)


def test_simple_message_old_style_dispatch_should_call_execute_command():
    bot = MockOldStyleBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)

    event = {'content': '/hello', 'channel': 'fakechannel'}
    dispatcher.dispatch(event, None)

    executed = bot.executed.pop(0) # type: Executed
    assert executed.command == 'hello'
    assert executed.args == [event, None]
