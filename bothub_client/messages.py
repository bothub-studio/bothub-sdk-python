# -*- coding: utf-8 -*-


class Message(object):
    '''A message class which renders rich messages like button, quick replies

    ex) Message(event).set_text('Hi there!')\\
                      .add_quick_reply('Say hello')'''
    def __init__(self, event):
        '''Initialize message class

        :param event: an event object
        :type event: dict'''
        self.model = []
        self.event = event

    def set_text(self, text):
        '''Set text message

        :param text: a text to send
        :type text: str'''
        self.model.append({
            'command': 'set_text',
            'args': {
                'text': text
            }
        })
        return self

    def add_url_button(self, text, url):
        '''Add an URL button

        :param text: button text
        :type text: str
        :param url: URL to link
        :type url: str'''
        self.model.append({
            'command': 'add_url_button',
            'args': {
                'text': text,
                'url': url
            }
        })
        return self

    def add_postback_button(self, text, payload):
        '''Add a postback button

        :param text: button text
        :type text: str
        :param payload: a payload to returns when button is clicked
        :type payload: str'''
        self.model.append({
            'command': 'add_postback_button',
            'args': {
                'text': text,
                'payload': payload
            }
        })
        return self

    def add_quick_reply(self, text, payload=None, image_url=None):
        '''Add a quick reply button

        :param text: button text
        :type text: str
        :param payload: a payload to returns when button is clicked
        :type payload: str
        :param image_url: an icon image URL. Only works with Facebook Messenger
        :type image_url: str'''
        self.model.append({
            'command': 'add_quick_reply',
            'args': {
                'text': text,
                'image_url': image_url,
                'payload': payload,
            }
        })
        return self

    def add_location_request(self, text):
        '''Add a location request

        :param text: button text. Will be ignored with Facebook Messenger
        :type text: str'''
        self.model.append({
            'command': 'add_location_request',
            'args': {
                'text': text
            }
        })
        return self

    def add_keyboard_button(self, text):
        '''Add a keyboard button

        :param text: Keyboard button text. Not supported for Facebook Messenger for now
        :type text: str'''
        self.model.append({
            'command': 'add_keyboard_button',
            'args': {
                'text': text
            }
        })
        return self

    def __repr__(self):
        result = []
        for model_entry in self.model:
            result.append('{} {}'.format(model_entry['command'], model_entry['args']))
        return '\n'.join(result)
