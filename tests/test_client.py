# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bothub_client.bot import BaseBot
from bothub_client.clients import handle_message


class Bot(BaseBot):
    def handle_message(self, event, context):
        content = event.get('content')
        self.send_message('hello, you said: {}'.format(content))


def test_handle_message_should_add_channel_cmd_buff():
    event = {
        'content': 'hi!',
        'channel': 'mychannel',
        'sender': {
            'id': 'abcd1234',
            'name': 'myname'
        }
    }

    context = {}

    result = handle_message(event, context, Bot)
    assert result['result'] is None
    assert result['proxy'] == [{'channel': None, 'chat_id': None, 'message': 'hello, you said: hi!'}]
