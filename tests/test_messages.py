# -*- coding: utf-8 -*-

from bothub_client.messages import Message
from bothub_client.messages import Markdown
from bothub_client.messages import HTML


def test_set_text_should_append_entry():
    message = Message(None).set_text('hello')
    assert message.model == [{'command': 'set_text',
                              'args': {'text': 'hello', 'markup': None}}]


def test_set_text_with_markdown_should_append_entry():
    message = Message(None).set_text(Markdown('hello'))
    assert message.model == [{'command': 'set_text',
                              'args': {'text': 'hello', 'markup': 'markdown'}}]


def test_set_text_with_markdown_should_append_entry():
    message = Message(None).set_text(HTML('hello'))
    assert message.model == [{'command': 'set_text',
                              'args': {'text': 'hello', 'markup': 'html'}}]


def test_add_url_button_should_append_entry():
    message = Message(None).add_url_button('hello', 'myurl')
    assert message.model == [{'command': 'add_url_button',
                              'args': {'text': 'hello',
                                       'url': 'myurl'}}]


def test_add_postback_button_should_append_entry():
    message = Message(None).add_postback_button('hello', 'mypayload')
    assert message.model == [{'command': 'add_postback_button',
                              'args': {'text': 'hello',
                                       'payload': 'mypayload'}}]


def test_add_quick_reply_should_append_entry():
    message = Message(None).add_quick_reply('hello', 'mypayload', 'myurl')
    assert message.model == [{'command': 'add_quick_reply',
                              'args': {'text': 'hello',
                                       'payload': 'mypayload',
                                       'image_url': 'myurl'}}]


def test_add_location_request_should_append_entry():
    message = Message(None).add_location_request('hello')
    assert message.model == [{'command': 'add_location_request',
                              'args': {'text': 'hello'}}]


def test_add_keyboard_button_should_append_entry():
    message = Message(None).add_keyboard_button('hello')
    assert message.model == [{'command': 'add_keyboard_button',
                              'args': {'text': 'hello'}}]
