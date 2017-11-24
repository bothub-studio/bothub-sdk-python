# -*- coding: utf-8 -*-

import sys
from bothub_client.utils import traceback_to_string
from bothub_client.utils import get_decorators
from bothub_client.decorators import command, intent


class TestDecorator(object):
    @command('start')
    def iamcommand(self):
        pass

    @command('reply')
    def iamcommand_too(self):
        pass

    @intent('credentials')
    def iamintent(self):
        pass


def test_get_decorators_should_returns_decorators():
    assert get_decorators(TestDecorator) == {'iamcommand': [('command', ['start'])],
                                             'iamcommand_too': [('command', ['reply'])],
                                             'iamintent': [('intent', ['credentials'])]}


def test_get_decorators_with_obj_should_returns_decorators():
    assert get_decorators(TestDecorator()) == {'iamcommand': [('command', ['start'])],
                                               'iamcommand_too': [('command', ['reply'])],
                                               'iamintent': [('intent', ['credentials'])]}


def test_traceback_to_string_should_return_string():
    try:
        raise KeyError()
    except KeyError as e:
        tb = None
        if sys.version_info < (3, 0):
            _, _, tb = sys.exc_info()
        s = traceback_to_string(e, tb=tb)
        assert 'raise KeyError()' in s
