# -*- coding: utf-8 -*-


class Message(object):
    def __init__(self, event):
        self.model = []
        self.event = event

    def set_text(self, text):
        self.model.append({
            'command': 'set_text',
            'args': {
                'text': text
            }
        })
        return self

    def add_url_button(self, text, url):
        self.model.append({
            'command': 'add_url_button',
            'args': {
                'text': text,
                'url': url
            }
        })
        return self

    def add_postback_button(self, text, payload):
        self.model.append({
            'command': 'add_postback_button',
            'args': {
                'text': text,
                'payload': payload
            }
        })
        return self

    def add_quick_reply(self, text, payload=None, image_url=None):
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
        self.model.append({
            'command': 'add_location_request',
            'args': {
                'text': text
            }
        })
        return self

    def add_keyboard_button(self, text):
        self.model.append({
            'command': 'add_keyboard_button',
            'args': {
                'text': text
            }
        })
        return self

    def __repr__(self):
        s = []
        for m in self.model:
            s.append('{} {}'.format(m['command'], m['args']))
        return '\n'.join(s)
