# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import requests_mock

from bothub_client.clients import StorageClient
from .testutils import MockTransport


def fixture_client(transport=None):
    context = {
        'project_id': 1,
        'api_key': 'testkey',
        'storage': {
            'endpoint': 'http://192.168.0.1:9000'
        }
    }

    client = StorageClient.init_client(context, transport=transport)
    return client


def record_project_data(transport):
    transport.record({'score': 11})


def test_init_client_should_returns_client_obj():
    client = fixture_client()
    assert client.project_id == 1
    assert client.api_key == 'testkey'
    assert client.base_url == 'http://192.168.0.1:9000'


def test_set_project_data():
    transport = MockTransport()

    client = fixture_client(transport)
    client.set_project_data({'score': 11})

    assert transport.executed.pop(0) == ('put',
                                         {'url': '/projects/1',
                                          'data': {'data': {'score': 11}}})


def test_get_project_data():
    transport = MockTransport()
    transport.record({})

    client = fixture_client(transport)
    client.get_project_data()

    assert transport.executed.pop(0) == ('get', {'url': '/projects/1'})


def test_set_user_data():
    transport = MockTransport()

    client = fixture_client(transport)
    client.set_user_data('mychannel', 'yourid', {'score': 11})

    assert transport.executed.pop(0) == ('put',
                                         {'url': '/projects/1/channels/mychannel/users/yourid',
                                          'data': {'data': {'score': 11}}})


def test_get_user_data():
    transport = MockTransport()
    transport.record({})

    client = fixture_client(transport)
    client.get_user_data('mychannel', 'yourid')

    assert transport.executed.pop(0) == ('get',
                                         {'url': '/projects/1/channels/mychannel/users/yourid'})
