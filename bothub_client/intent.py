# -*- coding: utf-8 -*-

import logging
import yaml
from collections import namedtuple

logger = logging.getLogger('bothub.intent')

Intent = namedtuple('Intent', ['id', 'on_complete', 'slots'])
IntentResult = namedtuple('IntentResult', ['intent_id', 'completed', 'answers', 'next_message', 'complete_handler_name', 'options'])
Slot = namedtuple('Slot', ['id', 'question', 'options', 'datatype'])


class NoSlotRemainsException(Exception):
    pass


class IntentState(object):
    '''I manage intent state.

    Store and manage intent state in Bot user data storage.
    '''
    intent_id_field = '_intent_id'
    intent_answers_field = '_intent_answers'
    remaining_slots_field = '_remaining_slots'
    slot_id_field = '_slot_id'
    slot_datatype_field = '_slot_datatype'

    def __init__(self, bot, intent_slots):
        self.bot = bot
        self.intent_id_to_intent_definition = dict([(i.id, i) for i in intent_slots])

    @staticmethod
    def load_yml(path):
        with open(path, encoding='utf8') as fin:
            content = fin.read()
        return yaml.load(content)

    @staticmethod
    def load_intent_slots_from_yml(path):
        config = IntentState.load_yml(path)
        intents = config.get('intents', {})
        intent_slots = []
        for intent_id in intents.keys():
            intent_yaml = intents[intent_id]
            slots_yaml = intent_yaml.get('slots', [])
            handler_name = intent_yaml.get('on_complete')
            slot_objs = []
            for slot in slots_yaml:
                _id = slot['id']
                question = slot['question']
                try:
                    options = slot['options']
                except KeyError:
                    options = []
                datatype = slot.get('datatype', 'string')
                slot_obj = Slot(_id, question, options, datatype)
                slot_objs.append(slot_obj)
            intent = Intent(intent_id, handler_name, slot_objs)
            intent_slots.append(intent)
        return intent_slots

    def open(self, intent_id):
        '''Open and start an intent.
        Should execute a `next()` method after open an intent.

        :param intent_id: an intent ID
        :type intent_id: str
        '''
        logger.debug('IntentState: init %s', intent_id)
        data = self.bot.get_user_data()
        data[self.intent_id_field] = intent_id
        data[self.intent_answers_field] = {}
        data[self.remaining_slots_field] = [
            d._asdict()
            for d in self.intent_id_to_intent_definition[intent_id].slots
        ]
        self.bot.set_user_data(data)

    def is_opened(self):
        '''Returns whether an intent is opened or not.

        :rtype: bool
        '''
        data = self.bot.get_user_data()
        return self.intent_id_field in data and data[self.intent_id_field] is not None

    def next(self, event=None):
        '''Proceed a current opened intent.
        If a user answer is given, store the answer and return an IntentResult object.

        :param event: an event dict
        :type event: dict
        :return: an intent result object
        :rtype: IntentResult
        '''
        logger.debug('IntentState: next with event %s', event)
        data = self.bot.get_user_data()
        if event:
            self._store_answer(event, data)
        result = self._make_result_obj(data)
        if result.completed:
            self._clear_state(data)
        self.bot.set_user_data(data)
        return result

    def close(self):
        '''Close an opened intent.

        Clear intent state variables in user data storage.
        '''
        data = self.bot.get_user_data()
        self._clear_state(data)
        self.bot.set_user_data(data)

    def _make_result_obj(self, data):
        next_message, options = self._next_slot_message(data)
        completed = next_message is None
        intent_id = data[self.intent_id_field]
        intent = self.intent_id_to_intent_definition[intent_id]
        result = IntentResult(intent_id,
                              completed,
                              dict(data[self.intent_answers_field].items()),
                              next_message,
                              intent.on_complete,
                              options)
        return result

    def _clear_state(self, data):
        logger.debug('IntentState: clear state')
        data[self.intent_id_field] = None
        data[self.slot_id_field] = None
        data[self.slot_datatype_field] = None
        data[self.remaining_slots_field] = None
        data[self.intent_answers_field] = None

    def _store_answer(self, event, data):
        slot_id = data[self.slot_id_field]
        data.setdefault(self.intent_answers_field, {})[slot_id] = event['content']

    def _has_remainig_slots(self, data):
        return self.remaining_slots_field in data and data[self.remaining_slots_field] is not None

    def _next_slot_message(self, data):
        try:
            if not self._has_remainig_slots(data):
                self.bot.set_user_data(data)
                raise NoSlotRemainsException()
            slot = data[self.remaining_slots_field].pop(0)
            data[self.slot_id_field] = slot['id']
            data[self.slot_datatype_field] = slot['datatype']
            return slot['question'], slot['options']
        except IndexError:
            return None, None
