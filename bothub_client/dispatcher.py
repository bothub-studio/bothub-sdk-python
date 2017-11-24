# -*- coding: utf-8 -*-

import logging
from bothub_client.utils import get_decorators
from bothub_client.messages import Message

logger = logging.getLogger('bothub.dispatcher')

class DefaultDispatcher(object):
    default_handler_name = 'on_default'
    command_handler_pattern = 'on_{command}'

    def __init__(self, bot, state):
        '''Initializer

        :param bot: a Bot object
        :type bot: BaseBot
        :param state: an IntentState object
        :type state: IntentState
        '''
        self.bot = bot
        self.state = state
        self.command_handlers = {}
        self.intent_handlers = {}
        self.channel_handlers = {}
        self._read_handlers()

    def _read_handlers(self):
        dec_type_to_handler_dict = {'command': self.command_handlers,
                                    'intent': self.intent_handlers,
                                    'channel': self.channel_handlers}
        method_to_decorators = get_decorators(self.bot)
        logger.debug('dispatch: method_to_decorators - %s', method_to_decorators)
        for method_name, decorators in method_to_decorators.items():
            for dec_type, args in decorators:
                handler_dict = dec_type_to_handler_dict.get(dec_type)
                if handler_dict is None:
                    continue
                handler_name = args[0] if args else 'default'
                handler_dict[handler_name] = method_name

    def dispatch(self, event, context):
        '''Dispatch incoming message event.

        :param event: an event object
        :type event: dict
        :param context: a context object
        :type content: dict
        '''
        logger.debug('dispatch: started')

        content = event.get('content')

        if self._is_intent_command(content):
            self.open_intent(event, content)
            return

        if self._is_command(content):
            self.execute_command(event, context, content)
            return

        if self.state.is_opened():
            self.proceed_intent(event, context)
            return

        current_channel = event.get('channel')
        if current_channel is None:
            return

        channel_handler = self.channel_handlers.get(current_channel)
        if channel_handler is None:
            channel_handler = self.channel_handlers.get('default', None)
        if channel_handler:
            handler_func = getattr(self.bot, channel_handler)
            handler_func(event, context)
        else:
            handler_func = getattr(self.bot, self.default_handler_name, None)
            if handler_func:
                handler_func(event, context)

    def open_intent(self, event, content):
        intent_id = self._get_intent_id(content)
        logger.debug('dispatch: intent %s started', intent_id)
        self.state.open(intent_id)
        result = self.state.next()
        message = Message(event)
        message.set_text(result.next_message)
        if result.options:
            for option in result.options:
                message.add_postback_button(option, option)
        self.bot.send_message(message)

    def execute_command(self, event, context, content):
        command, args = self._get_command_args(content)
        logger.debug('dispatch: start command %s', command)
        try:
            new_style_handler_name = self.command_handlers.get(command)
            old_style_handler_name = self.command_handler_pattern.format(command=command)

            if new_style_handler_name:
                handler_func = getattr(self.bot, new_style_handler_name)
                handler_func(event, context, args)
            elif old_style_handler_name:
                handler_func = getattr(self.bot, old_style_handler_name)
                handler_func(event, context, *args)

        except KeyError:
            self.bot.send_message('No such command: {}'.format(command))

    def proceed_intent(self, event, context):
        logger.debug('dispatch: continue to process intent')
        result = self.state.next(event)
        if result.completed:
            logger.debug('dispatch: intent completed')

            new_sytle_handler_name = self.intent_handlers.get(result.intent_id)
            old_style_handler_name = result.complete_handler_name or 'set_{}'.format(result.intent_id)

            if new_sytle_handler_name:
                handler_func = getattr(self.bot, new_sytle_handler_name)
                handler_func(event, context, result.answers)
            elif old_style_handler_name:
                handler_func = getattr(self.bot, old_style_handler_name)
                handler_func(event, context, **result.answers)
        else:
            message = Message(event)
            message.set_text(result.next_message)
            if result.options:
                for option in result.options:
                    message.add_postback_button(option, option)
            self.bot.send_message(message)

    def _is_command(self, content):
        return content is not None and content.startswith('/')

    def _is_intent_command(self, content):
        return content is not None and content.startswith('/intent ')

    def _get_intent_id(self, content):
        _, intent_id = content.split()
        return intent_id

    def _get_command_args(self, content):
        tokens = content.split()
        command = tokens[0][1:]
        args = tokens[1:]
        return command, args
