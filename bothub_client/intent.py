# -*- coding: utf-8 -*-

import logging
import json
import yaml
from collections import namedtuple

from bothub_client.dispatcher import DefaultDispatcher

logger = logging.getLogger('bothub.intent')

Intent = namedtuple('Intent', ['id', 'on_complete', 'slots'])
IntentResult = namedtuple('IntentResult', ['intent_id', 'completed', 'answers', 'next_message'])
Slot = namedtuple('Slot', ['id', 'question', 'datatype'])


class NoSlotRemainsException(Exception):
    pass


class IntentState(object):
    '''Manage intent state'''
    intent_id_field = '_intent_id'
    intent_answers_field = '_intent_answers'
    remaining_slots_field = '_remaining_slots'
    slot_id_field = '_slot_id'
    slot_datatype_field = '_slot_datatype'

    def __init__(self, bot, intent_slots):
        self.bot = bot
        self.intent_id_to_intent_definition = dict([(i.id, i) for i in intent_slots])

    @staticmethod
    def load_intent_slots_from_yml(path):
        with open(path) as fin:
            content = fin.read()
        config = yaml.load(content)

        intents = config.get('intents', {})
        intent_slots = []
        for intent_id in intents.keys():
            intent_yaml = intents[intent_id]
            on_complete = intent_yaml.get('on_complete', 'set_{}'.format(intent_id))
            slots_yaml = intent_yaml.get('slots', [])
            slot_objs = []
            for slot in slots_yaml:
                _id = slot['id']
                question = slot['question']
                datatype = slot.get('datatype', 'string')
                slot_obj = Slot(_id, question, datatype)
                slot_objs.append(slot_obj)
            intent = Intent(intent_id, on_complete, slot_objs)
            intent_slots.append(intent)
        return intent_slots

    def init(self, intent_id):
        logger.debug('IntentState: init %s', intent_id)
        data = self.bot.get_user_data()
        data[self.intent_id_field] = intent_id
        data[self.intent_answers_field] = {}
        data[self.remaining_slots_field] = [
            d._asdict()
            for d in self.intent_id_to_intent_definition[intent_id].slots
        ]
        self.bot.set_user_data(data)

    def is_processing(self, data):
        return self.intent_id_field in data and data[self.intent_id_field] is not None

    def next(self, event=None):
        logger.debug('IntentState: next with event %s', event)
        data = self.bot.get_user_data()
        if event:
            self._store_answer(event, data)
        result = self._make_result_obj(data)
        if result.completed: self._clear_state(data)
        self.bot.set_user_data(data)
        return result

    def on_complete(self, intent_id, event, context, **kwargs):
        data = self.bot.get_user_data()
        logger.debug('IntentState: on_complete intent %s', intent_id)
        intent = self.intent_id_to_intent_definition[intent_id]
        func_name = intent.on_complete
        func = getattr(self.bot, func_name)
        func(event, context, **kwargs)

    def _make_result_obj(self, data):
        next_message = self._next_slot_message(data)
        completed = next_message is None
        result = IntentResult(
            data[self.intent_id_field],
            completed,
            dict(data[self.intent_answers_field].items()),
            next_message
        )
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

    def _load_slot(self, data):
        slot = data[self.remaining_slots_field].pop(0)

    def _has_remainig_slots(self, data):
        return self.remaining_slots_field not in data or data[self.remaining_slots_field] is not None
        
    def _next_slot_message(self, data):
        try:
            if not self._has_remainig_slots(data):
                self._clear_state(data)
                self.bot.set_user_data(data)
                raise NoSlotRemainsException()
            slot = data[self.remaining_slots_field].pop(0)
            data[self.slot_id_field] = slot['id']
            data[self.slot_datatype_field] = slot['datatype']
            return slot['question']
        except IndexError:
            return None
