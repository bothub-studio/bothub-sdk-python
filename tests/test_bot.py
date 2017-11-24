# -*- coding: utf-8 -*-

from bothub_client.bot import BaseBot


class DummyDispatcher(object):
    executed = []
    def __init__(self, bot, state):
        pass

    def dispatch(self, event, context):
        self.executed.append(('dispatch', {'event': event, 'context': context}))


class DummyStorageClient(object):
    def __init__(self):
        self.executed = []

    def set_project_data(self, data):
        self.executed.append(('set_project_data', {'data': data}))

    def get_project_data(self):
        self.executed.append(('get_project_data', {}))
        return {}

    def set_user_data(self, channel, user_id, data):
        self.executed.append(('set_user_data',
                              {'data': data, 'channel': channel, 'user_id': user_id}))

    def get_user_data(self, channel, user_id):
        self.executed.append(('get_user_data',
                              {'channel': channel, 'user_id': user_id}))
        return {}


class DummyNluClientFactory(object):
    def __init__(self):
        self.executed = []

    def get(self, vendor):
        self.executed.append(('get', {'vendor': vendor}))


def test_handle_message_should_run_dispatch():
    storage_client = DummyStorageClient()
    dispatcher_class = DummyDispatcher
    bot = BaseBot(storage_client=storage_client, event={}, dispatcher_class=dispatcher_class)
    bot.handle_message({}, {})
    assert dispatcher_class.executed.pop(0) == ('dispatch', {'event': {}, 'context': {}})


def test_set_project_data_should_invoke_client():
    storage_client = DummyStorageClient()
    bot = BaseBot(storage_client=storage_client, event={})
    bot.set_project_data({})
    assert storage_client.executed.pop(0) == ('set_project_data', {'data': {}})


def test_get_project_data_should_invoke_client():
    storage_client = DummyStorageClient()
    bot = BaseBot(storage_client=storage_client, event={})
    bot.get_project_data()
    assert storage_client.executed.pop(0) == ('get_project_data', {})


def test_set_user_data_should_invoke_client():
    storage_client = DummyStorageClient()
    bot = BaseBot(storage_client=storage_client, event={})
    bot.set_user_data({})
    assert storage_client.executed.pop(0) == ('set_user_data',
                                              {'data': {}, 'user_id': None, 'channel': None})


def test_get_user_data_should_invoke_client():
    storage_client = DummyStorageClient()
    bot = BaseBot(storage_client=storage_client, event={})
    bot.get_user_data()
    assert storage_client.executed.pop(0) == ('get_user_data',
                                              {'user_id': None, 'channel': None})


def test_nlu_should_return_client():
    nlu_factory = DummyNluClientFactory()
    bot = BaseBot(nlu_client_factory=nlu_factory, event={})
    bot.nlu('test')
    assert nlu_factory.executed.pop(0) == ('get', {'vendor': 'test'})
