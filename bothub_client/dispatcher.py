# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger('bothub.dispatcher')

class DefaultDispatcher(object):
    default_handler_name = 'on_default'
    command_handler_pattern = 'on_{command}'

    def __init__(self, bot, state):
        self.bot = bot
        self.state = state

    def dispatch(self, event, context):
        logger.debug('dispatch: started')
        data = self.bot.get_user_data()
        if self.state.is_processing(data):
            logger.debug('dispatch: continue to process intent')
            result = self.state.next(event)
            if result.completed:
                logger.debug('dispatch: intent completed')
                self.state.on_complete(result.intent_id, event, context, **result.answers)
            else:
                self.bot.send_message(result.next_message)
            return

        content = event['content']

        if content.startswith('/intent '):
            _, intent_id = content.split()
            logger.debug('dispatch: intent %s started', intent_id)
            self.state.init(intent_id)
            result = self.state.next()
            self.bot.send_message(result.next_message)
            return

        if content.startswith('/'):
            tokens = content.split()
            command = tokens[0][1:]
            logger.debug('dispatch: start command %s', command)
            args = tokens[1:]
            func = getattr(self.bot, self.command_handler_pattern.format(command=command))
            func(event, context, *args)
            return

        func = getattr(self.bot, self.default_handler_name)
        func(event, context)
