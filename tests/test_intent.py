# -*- coding: utf-8 -*-

import json
import logging
from collections import namedtuple

import pytest
from bothub_client.intent import Intent
from bothub_client.intent import Slot
from bothub_client.intent import IntentState
from bothub_client.intent import NoSlotRemainsException
from bothub_client.dispatcher import DefaultDispatcher
from bothub_client.decorators import channel
from bothub_client.decorators import intent


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


def test_init_intent_should_set_init_entries():
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    state.open('credentials')
    assert bot.data['_intent_id'] == 'credentials'
    assert bot.data['_remaining_slots'] == [
        {'id': 'app_id', 'question': 'Please tell me your app ID', 'datatype': 'string', 'options': None},
        {'id': 'app_secret', 'question': 'Please tell me your app secret', 'datatype': 'string', 'options': None},
    ]


def test_get_result_should_return_result_with_next_message():
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    state.open('credentials')
    assert bot.data['_remaining_slots'] == [
        {'id': 'app_id', 'question': 'Please tell me your app ID', 'datatype': 'string', 'options': None},
        {'id': 'app_secret', 'question': 'Please tell me your app secret', 'datatype': 'string', 'options': None},
    ]

    result = state.next()
    assert result.completed is False
    assert result.next_message == 'Please tell me your app ID'
    assert bot.data['_remaining_slots'] == [
        {'id': 'app_secret', 'question': 'Please tell me your app secret', 'datatype': 'string', 'options': None},
    ]

    result = state.next({'content': '<my app ID>'})
    assert result.completed is False
    assert result.next_message == 'Please tell me your app secret'
    assert bot.data['_remaining_slots'] == []
    assert result.answers == {
        'app_id': '<my app ID>'
    }

    result = state.next({'content': '<my app secret>'})
    assert result.completed is True
    assert result.next_message is None
    assert result.answers == {
        'app_id': '<my app ID>',
        'app_secret': '<my app secret>'
    }


def test_get_result_should_raise_exception_when_exceeded_slots():
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    state.open('credentials')
    state.next() # Returns IntentResult: q=Please tell me your app ID
    state.next() # Returns IntentResult: q=Please tell me your app secret
    result = state.next() # Returns IntentResult: complete=True
    assert result.completed is True

    with pytest.raises(NoSlotRemainsException):
        state.next()


def test_dispatch_should_execute_default():
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)
    dispatcher.dispatch({'content': 'hello', 'channel': 'fakechannel'}, None)
    assert len(bot.executed) == 1
    executed = bot.executed.pop(0)
    assert executed == Executed(
        'on_default',
        ({'content': 'hello', 'channel': 'fakechannel'}, None)
    )


def test_dispatch_should_execute_credentials():
    logging.basicConfig(level=logging.DEBUG)
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)
    dispatcher.dispatch({'content': '/intent credentials'}, None)
    dispatcher.dispatch({'content': 'my token'}, None)
    dispatcher.dispatch({'content': 'my secret token'}, None)
    assert len(bot.executed) == 1
    executed = bot.executed.pop(0)
    assert executed == Executed('set_credentials', ('my token', 'my secret token'))


def test_dispatch_should_trigger_intent_and_default():
    logging.basicConfig(level=logging.DEBUG)
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)
    dispatcher.dispatch({'content': '/intent credentials', 'channel': 'fakechannel'}, None)
    dispatcher.dispatch({'content': 'my token', 'channel': 'fakechannel'}, None)
    dispatcher.dispatch({'content': 'my secret token', 'channel': 'fakechannel'}, None)
    dispatcher.dispatch({'content': 'hello', 'channel': 'fakechannel'}, None)
    assert len(bot.executed) == 2
    executed = bot.executed.pop(0)
    assert executed == Executed('set_credentials', ('my token', 'my secret token'))
    executed = bot.executed.pop(0)
    assert executed == Executed('on_default', ({'content': 'hello', 'channel': 'fakechannel'},
                                               None))


def test_intent_state_load_intent_slots_should_return_intent_slots():
    intent_slots = IntentState.load_intent_slots_from_yml('tests/fixtures/test_bothub.yml')
    assert intent_slots == [Intent('age', None, [Slot('age', 'How old are you?', [], 'string'),
                                                 Slot('name', 'What is your name?', [], 'string')])]
