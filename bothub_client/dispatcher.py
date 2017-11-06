# -*- coding: utf-8 -*-

import logging
from bothub_client.utils import get_decorators

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
                handler_name = args[0] if len(args) > 0 else 'default'
                handler_dict[handler_name] = method_name

    def dispatch(self, event, context):
        '''Dispatch incoming message event.

        :param event: an event object
        :type event: dict
        :param context: a context object
        :type content: dict
        '''
        logger.debug('dispatch: started')
        if self.state.is_opened():
            logger.debug('dispatch: continue to process intent')
            result = self.state.next(event)
            if result.completed:
                logger.debug('dispatch: intent completed')
                handler_func = getattr(self.bot, self.intent_handlers[result.intent_id])
                handler_func(event, context, result.answers)
            else:
                self.bot.send_message(result.next_message)
            return

        content = event['content']

        if self._is_intent_command(content):
            intent_id = self._get_intent_id(content)
            logger.debug('dispatch: intent %s started', intent_id)
            self.state.open(intent_id)
            result = self.state.next()
            self.bot.send_message(result.next_message)
            return

        if self._is_command(content):
            command, args = self._get_command_args(content)
            logger.debug('dispatch: start command %s', command)
            try:
                handler_func = getattr(self.bot, self.command_handlers[command])
                handler_func(event, context, *args)
                return
            except KeyError:
                self.bot.send_message('No such command: {}'.format(command))
                return

        current_channel = event.get('channel')
        if current_channel is None:
            return

        channel_handler = None
        if current_channel not in self.channel_handlers:
            channel_handler = self.channel_handlers.get('default', None)
        else:
            channel_handler = self.channel_handlers[event['channel']]

        if not channel_handler:
            return

        handler_func = getattr(self.bot, channel_handler)
        handler_func(event, context)

    def _is_command(self, content):
        return content.startswith('/')

    def _is_intent_command(self, content):
        return content.startswith('/intent ')

    def _get_intent_id(self, content):
        _, intent_id = content.split()
        return intent_id

    def _get_command_args(self, content):
        tokens = content.split()
        command = tokens[0][1:]
        args = tokens[1:]
        return command, args
