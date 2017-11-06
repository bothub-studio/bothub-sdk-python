# -*- coding: utf-8 -*-

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
