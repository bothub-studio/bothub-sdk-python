# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

import json

from bothub_client.messages import Message
from bothub_client.transports import HttpTransport
from bothub_client.transports import ZmqTransport


def get_channel_client(context):
    '''Returns proper channel client according to channel URL scheme

    :param context: a context Bot runs
    :type context: dict
    :return: a ChannelClient instance'''
    scheme_to_channel_client = {
        'http': ChannelClient,
        'https': ChannelClient,
        'tcp': ZmqChannelClient,
    }

    endpoint = context.get('channel', {}).get('endpoint', 'http:')
    scheme = endpoint.split(':')[0]
    client_class = scheme_to_channel_client.get(scheme, ZmqChannelClient)
    return client_class.init_client(context)


def handle_message(event, context, bot_class):
    '''Handle a message which messenger platform sent

    :param event: an event which messenger platform sent
    :type event: dict
    :param context: a context Bot runs
    :type context: dict
    :param bot_class: a Bot class user wrote
    :type bot_class: bothub_client.bot.BaseBot
    :return: a dict contains response'''
    channel = get_channel_client(context)
    storage = StorageClient.init_client(context, event=event)
    nlu_client_factory = NluClientFactory(context)

    bot = bot_class(channel_client=channel, storage_client=storage,
                    nlu_client_factory=nlu_client_factory, event=event)
    response = bot.handle_message(event, context)
    bot.close()
    channel.close()
    return {'response': response}


class Client(object):
    '''A base client class'''
    def __init__(self, project_id, api_key, base_url, transport=None):
        self.project_id = project_id
        self.base_url = base_url
        self.api_key = api_key
        self.transport = transport or HttpTransport(base_url)


class BaseChannelClient(Client):
    '''A ChannelClient class

    Send a message to  a messenger platform'''
    def __init__(self, project_id, api_key, base_url, transport=None, context=None):
        self.context = context
        super(BaseChannelClient, self).__init__(project_id, api_key, base_url, transport)

    def _get_channel_obj(self, channel_type):
        channels = self.context['channel'].get('channels', [])
        for channel in channels:
            if channel['type'] == channel_type:
                return channel

    def _default_prepare_payload(self, chat_id, channel, event):
        from_chat_id = event.get('chat_id')
        origin_channel = event.get('channel')
        _chat_id = chat_id or from_chat_id
        channel_type = channel or origin_channel
        _channel = self._get_channel_obj(channel_type)

        data = {
            'channel': _channel,
            'receiver': _chat_id,
            'event': event,
            'context': {
                'project_id': self.project_id,
                'api_key': self.api_key,
                'request_id': self.context.get('request_id'),
                'rabbitmq': self.context.get('rabbitmq', {}).get('endpoint', 'localhost')
            }
        }
        return data

    def _prepare_payload(self, chat_id, message, channel=None, event=None, extra=None):
        data = self._default_prepare_payload(chat_id, channel, event)
        data['extra'] = extra

        if isinstance(message, Message):
            data['message'] = {
                'model': message.model,
                'event': message.event
            }
        else:
            data['message'] = message
        return data

    def _prepare_payload_to_photo(self, chat_id, photo_url, channel=None, event=None):
        data = self._default_prepare_payload(chat_id, channel, event)
        data['photo'] = photo_url
        return data


class ChannelClient(BaseChannelClient):
    '''A ChannelClient class using HTTP transport

    Send a message to  a messenger platform'''
    @staticmethod
    def init_client(context):
        project_id = context.get('project_id')
        api_key = context.get('api_key', '')
        channel_endpoint = context.get('channel', {}).get('endpoint')
        return ChannelClient(project_id, api_key, channel_endpoint,
                             transport=HttpTransport(channel_endpoint), context=context)

    def send_message(self, chat_id, message, channel=None, event=None, extra=None):
        data = self._prepare_payload(chat_id, message, channel, event, extra)
        self.transport.post('/messages', data)

    def send_photo(self, chat_id, photo_url, channel=None, event=None):
        pass

    def close(self):
        pass


class ZmqChannelClient(BaseChannelClient):
    '''A ChannelClient class using ZeroMQ

    Send a message to  a messenger platform'''
    @staticmethod
    def init_client(context, transport=None):
        project_id = context.get('project_id')
        api_key = context.get('api_key', '')
        channel_endpoint = context.get('channel', {}).get('endpoint')
        _transport = transport or ZmqTransport(channel_endpoint)
        return ZmqChannelClient(project_id, api_key, channel_endpoint,
                                transport=_transport, context=context)

    def send_message(self, chat_id, message, channel=None, event=None, extra=None):
        data = self._prepare_payload(chat_id, message, channel, event, extra)
        self.transport.send_multipart([json.dumps(data).encode('utf8')])

    def send_photo(self, chat_id, photo_url, channel=None, event=None):
        data = self._prepare_payload_to_photo(chat_id, photo_url, channel, event)
        self.transport.send_multipart([json.dumps(data).encode('utf8')])

    def close(self):
        self.transport.close()


class StorageClient(Client):
    def __init__(self, project_id, api_key, base_url, transport=None, user=None):
        super(StorageClient, self).__init__(project_id, api_key, base_url, transport)
        self.current_user = user

    @staticmethod
    def init_client(context, event=None, transport=None):
        project_id = context.get('project_id')
        api_key = context.get('api_key', '')
        storage_endpoint = context.get('storage', {}).get('endpoint')
        user = None if not event else (event['channel'], event.get('sender', {}).get('id'))
        return StorageClient(project_id, api_key, storage_endpoint, transport=transport, user=user)

    def set_project_data(self, data):
        self.transport.put(
            '/projects/{}'.format(self.project_id),
            {'data': data},
        )

    def get_project_data(self, key=None):
        url = '/projects/{}'.format(self.project_id)
        if key:
            url += '/{}'.format(key)
        return self.transport.get(url).get('data') or {}

    def set_user_data(self, channel, user_id, data):
        self.transport.put(
            '/projects/{}/channels/{}/users/{}'.format(self.project_id, channel, user_id),
            {'data': data},
        )

    def get_user_data(self, channel, user_id, key=None):
        url = '/projects/{}/channels/{}/users/{}'.format(self.project_id, channel, user_id)
        if key:
            url += '/{}'.format(key)
        return self.transport.get(url).get('data') or {}

    def set_current_user_data(self, data):
        channel, user_id = self.current_user
        self.set_user_data(channel, user_id, data)

    def get_current_user_data(self, key=None):
        channel, user_id = self.current_user
        return self.get_user_data(channel, user_id, key)


class NluClient(object):
    ''''''
    def ask(self, event=None, message=None, session_id=None):
        '''Request a query to NLU service.

        There are two styles to request to NLU service::

        * client.ask(event=event)
        * client.ask(message=message, session_id=session_id)
        '''
        raise NotImplementedError()

class DialogflowNluClient(NluClient):
    '''An NLU client for Dialogflow'''
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.dialogflow = __import__('dialogflow')
        self.lang = self._get_lang()

    def _get_lang(self):
        client = self.dialogflow.AgentsClient()
        parent = client.project_path(self.agent_id)
        response = client.get_agent(parent)
        lang = response.default_language_code
        return lang

    @staticmethod
    def parse_response(query_result):
        '''Parse a response API.ai returns

        :param response: a response which apiai client returns
        :type response: http.client.HTTPResponse
        :return: an NluResponse object
        :rtype: bothub_client.clients.NluResponse'''
        action = NluAction(
            query_result.action or query_result.intent.display_name,
            query_result.parameters,
            not query_result.all_required_params_present
        )
        next_message = query_result.fulfillment_text
        return NluResponse(query_result, next_message, action)

    def ask(self, event=None, message=None, session_id=None, lang=None):
        '''Query a message to Dialogflow

        use ``ask(event=event)``
        form either ``ask(message='a text', session_id=<session_id>)``

        :param event: an event dict messenger platform sent.
        :param lang: optional, default value equal 'en' '''
        if event:
            return self._ask_with_event(event, lang)
        if message:
            return self._ask_with_message(message, session_id, lang)

    def _ask_with_event(self, event, lang=None):
        lang = lang or self.lang
        text = event.get('content')
        session_id = '{}-{}'.format(event.get('channel'), event.get('sender').get('id'))
        session_client = self.dialogflow.SessionsClient()
        session = session_client.session_path(self.agent_id, session_id)
        text_input = self.dialogflow.types.TextInput(text=text, language_code=lang)
        query_input = self.dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(session, query_input=query_input)

        return DialogflowNluClient.parse_response(response.query_result)

    def _ask_with_message(self, message, session_id, lang=None):
        lang = lang or self.lang
        session_client = self.dialogflow.SessionsClient()
        session = session_client.session_path(self.agent_id, session_id)
        text_input = self.dialogflow.types.TextInput(text=message, language_code=lang)
        query_input = self.dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(session, query_input=query_input)

        return DialogflowNluClient.parse_response(response.query_result)

class ApiAiNluClient(NluClient):
    '''An NLU client for API.ai'''
    def __init__(self, api_key):
        self.api_key = api_key
        apiai_module = __import__('apiai')
        self.apiai = apiai_module.ApiAI(api_key)

    @staticmethod
    def parse_response(response):
        '''Parse a response API.ai returns

        :param response: a response which apiai client returns
        :type response: http.client.HTTPResponse
        :return: an NluResponse object
        :rtype: bothub_client.clients.NluResponse'''
        content = response.read().decode('utf-8')
        json_response = json.loads(content)
        action = NluAction(
            json_response.get('result').get('action'),
            json_response.get('result').get('parameters'),
            json_response.get('result').get('actionIncomplete')
        )
        next_message = json_response.get('result').get('fulfillment', {}).get('speech')
        return NluResponse(json_response, next_message, action)

    def ask(self, event=None, message=None, session_id=None, lang='en'):
        '''Query a message to API.ai

        use ``ask(event=event)``
        form either ``ask(message='a text', session_id=<session_id>)``

        :param event: an event dict messenger platform sent.
        :param lang: optional, default value equal 'en' '''
        if event:
            return self._ask_with_event(event, lang)
        if message and session_id:
            return self._ask_with_message(message, session_id, lang)

    def _ask_with_event(self, event, lang='en'):
        request = self.apiai.text_request()
        request.lang = lang
        request.query = event.get('content')
        request.session_id = '{}-{}'.format(event.get('channel'), event.get('sender').get('id'))
        response = request.getresponse()
        return ApiAiNluClient.parse_response(response)

    def _ask_with_message(self, message, session_id, lang='en'):
        request = self.apiai.text_request()
        request.lang = lang
        request.query = message
        request.session_id = session_id
        response = request.getresponse()
        return ApiAiNluClient.parse_response(response)


class NluClientFactory(object):
    '''An NluClientFactory which returns NluClient according to vendor name'''
    NAME_TO_CLIENT = {
        'apiai': ApiAiNluClient,
        'dialogflow': DialogflowNluClient
    }

    def __init__(self, context):
        self.integrations_params = context.get('nlu')

    def get(self, vendor):
        '''Returns a proper NluClient object'''
        return self.NAME_TO_CLIENT.get(vendor)(**self.integrations_params.get(vendor))


class NluAction(object):
    '''A NluAction class represents an intent identified action.'''

    def __init__(self, intent=None, parameters=None, action_incomplete=True):
        self.intent = intent
        self.parameters = parameters or {}
        self.completed = not action_incomplete

    def __repr__(self):
        return "<NluAction '{}', completed: {}, args: {}>".format(
            self.intent,
            self.completed,
            self.parameters
        )


class NluResponse(object):
    '''A NluResponse class containing a response from a NLU service.'''
    def __init__(self, response, next_message=None, action=None):
        self.raw_response = response
        self.action = action
        self.next_message = next_message
