# -*- coding: utf-8 -*-

import json
from collections import namedtuple
from bothub_client.dispatcher import DefaultDispatcher
from bothub_client.intent import Intent
from bothub_client.intent import Slot
from bothub_client.intent import IntentState

Executed = namedtuple('Executed', ['command', 'args'])


class MockBot:
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

    def set_credentials(self, app_id, app_secret):
        self.executed.append(Executed('set_credentials', (app_id, app_secret)))


def fixture_intent_slots():
    return [
        Intent('credentials', 'set_credentials', [
            Slot('app_id', 'Please tell me your app ID', 'string'),
            Slot('app_secret', 'Please tell me your app secret', 'string'),
        ]),
        Intent('address', 'set_address', [
            Slot('country', 'Please tell me your country', 'string'),
            Slot('city', 'Please tell me your city', 'string'),
            Slot('road', 'Please tell me your road address', 'string'),
        ])
    ]


def test_simple_message_dispatch_should_call_on_default():
    bot = MockBot()
    intent_slots = fixture_intent_slots()
    state = IntentState(bot, intent_slots)
    dispatcher = DefaultDispatcher(bot, state)

    event = {'content': 'hello'}
    dispatcher.dispatch(event, None)

    executed = bot.executed.pop(0) # type: Executed
    assert executed.command == 'on_default'
    assert executed.args == (event, None)
