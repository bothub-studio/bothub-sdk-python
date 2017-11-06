# -*- coding: utf-8 -*-

from bothub_client.bot import BaseBot


class DummyStorageClient(object):
    def get_user_data(self, channel, user_id=None):
        return {}


def test_handle_message_should_run_dispatch():
    storage_client = DummyStorageClient()

    bot = BaseBot(storage_client=storage_client,
                  event={})
    bot.handle_message({}, {})
