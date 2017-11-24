# -*- coding: utf-8 -*-

import json
import pytest
from io import BytesIO
from bothub_client.clients import NluClient
from bothub_client.clients import NluAction
from bothub_client.clients import ApiAiNluClient


class MockApiAiRequest(object):
    def __init__(self):
        self.query = None
        self.session_id = None

    def getresponse(self):
        response = {'request': {'query': self.query,
                                'session_id': self.session_id},
                    'result': {'action': 'myaction',
                               'parameters': [],
                               'actionIncomplete': True,
                               'fulfillment': {'speech': 'next question'}}}
        return BytesIO(json.dumps(response).encode('utf8'))


class MockApiai(object):
    def text_request(self):
        return MockApiAiRequest()


def fixture_apiai_response():
    response_dict = {'result': {'action': 'myaction',
                                'parameters': [],
                                'actionIncomplete': True,
                                'fulfillment': {'speech': 'Next question?'}}}
    return response_dict


def test_nlu_client_ask_raises_exception():
    with pytest.raises(NotImplementedError):
        NluClient().ask()


def test_apiai_nlu_client_parse_should_return_response():
    response_dict = fixture_apiai_response()
    response = BytesIO(json.dumps(response_dict).encode('utf8'))
    result = ApiAiNluClient.parse_response(response)
    assert isinstance(result.action, NluAction)
    assert result.next_message == 'Next question?'


def test_apiai_nlu_client_ask_with_event_should_return_response():
    client = ApiAiNluClient('myapikey')
    client.apiai = MockApiai()
    response = client._ask_with_event({'content': 'hello',
                                       'channel': 'mychannel',
                                       'sender': {'id': 'myid'}})
    _assert_apiai_response(response)


def test_apiai_nlu_client_ask_with_message_should_return_response():
    client = ApiAiNluClient('myapikey')
    client.apiai = MockApiai()
    response = client._ask_with_message('hello', 'mychannel-myid')
    _assert_apiai_response(response)


def test_apiai_nlu_client_ask_event_should_return_response():
    client = ApiAiNluClient('myapikey')
    client.apiai = MockApiai()
    response = client.ask(event={'content': 'hello',
                                 'channel': 'mychannel',
                                 'sender': {'id': 'myid'}})
    _assert_apiai_response(response)


def test_apiai_nlu_client_ask_message_should_return_response():
    client = ApiAiNluClient('myapikey')
    client.apiai = MockApiai()
    response = client.ask(message='hello', session_id='mychannel-myid')
    _assert_apiai_response(response)


def _assert_apiai_response(response):
    assert response.raw_response['result'] == {'action': 'myaction',
                                               'parameters': [],
                                               'actionIncomplete': True,
                                               'fulfillment': {'speech': 'next question'}}
    assert response.raw_response['request']['query'] == 'hello'
    assert response.raw_response['request']['session_id'] == 'mychannel-myid'
