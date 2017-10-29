# -*- coding: utf-8 -*-

import logging

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
                handler_func = getattr(self.bot, result.complete_handler_name)
                handler_func(**result.answers)
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
            handler_func = getattr(self.bot, self.command_handler_pattern.format(command=command))
            handler_func(event, context, *args)
            return

        handler_func = getattr(self.bot, self.default_handler_name)
        handler_func(event, context)

    def _is_intent_command(self, content):
        return content.startswith('/intent ')

    def _get_intent_id(self, content):
        _, intent_id = content.split()
        return intent_id

    def _is_command(self, content):
        return content.startswith('/')

    def _get_command_args(self, content):
        tokens = content.split()
        command = tokens[0][1:]
        args = tokens[1:]
        return command, args
