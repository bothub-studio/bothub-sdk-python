================================================
BotHub.Studio: Chatbot Framework for easy deploy
================================================

This package provide components to works with `BotHub.Studio`_, which is a chatbot hosting service.

With `bothub-cli`_, you can deploy a new chatbot with just four lines of commands.


Installation
============

To install bothub::

  $ pip install bothub

The bothub package works on python2 and 3 both.


Getting Started
===============

You can build an echo chatbot simply by subclassing ``BaseBot`` class and overriding ``handle_message`` method.

.. code:: python

   # -*- coding: utf-8 -*-
   
   from bothub_client.bot import BaseBot
   
   class Bot(BaseBot):
       """Represent a Bot logic which interacts with a user.
   
       BaseBot superclass have methods belows:
   
       * Send message
         * self.send_message(message, chat_id=None, channel=None, extra=None)
       * Data Storage
         * self.set_project_data(data)
         * self.get_project_data()
         * self.set_user_data(data, user_id=None, channel=None)
         * self.get_user_data(user_id=None, channel=None)
         * self.nlu(vendor) -> NluClient

       When you omit user_id and channel argument, it regarded as a user
       who triggered a bot.
       """
   
       def handle_message(self, event, context):
           self.send_message(event['content'])


When a bot receives a message from an user, it triggers ``handle_message`` method with ``event`` and ``context`` object.

An ``event`` is a dict which contains following items:

* ``content``: A message text received.
* ``channel``: Which channel (messenger platform) sent a message.
* ``sender``: Who sent a message. ``{"id": <user-id>, "name": "<username>}``
* ``chat_id``: Chatroom ID where message is sent. It can be a 1:1 chatroom or group chatroom.
* ``location``: Location information if possible ``{"longitude": <float>, "latitude": <float>}``
* ``postback``: A postback data.
* ``new_joined``: A boolean which indicates this bot was invited to some chatroom or not.
* ``raw_data``: A raw data itself messenger platforms sent.

You can respond to this message with various tools we provides.


Messaging
---------

To send a message, use a ``self.send_message`` method with a message you want to send.

.. code:: python

          self.send_message('hello')

In most cases, you may omit ``user_id`` and ``channel`` arguments. Then it replies to whom sent a message to your bot. Put values to those arguments when you want to specify a receiver.

You can send a message with rich controls like 'quick replies' or 'buttons' using ``Message`` object.

.. code:: python

          from bothub_client.messages import Message

          message = Message(event).add_quick_reply('Go ahead')\
                                  .add_quick_reply('Never mind')\
                                  .set_text('May I reserve the seat?')
          self.send_message(message)


``Message`` class provides these methods:

* ``set_text(text)``
* ``add_url_button(text, url)``: 
* ``add_postback_button(text, payload)``
* ``add_quick_reply(text, payload=None, image_url=None)``
* ``add_location_request(text)``
* ``add_keyboard_button(text)``


Storage
-------

To store/retreive some property data, we provides following methods:

* Project level

  * ``self.set_project_data(data)``: set data to a project
  * ``self.get_project_data()``: get data from a project

* User level

  * ``self.set_user_data(data, user_id=None, channel=None)``: set user data
  * ``self.get_user_data(user_id=None, channel=None)``: get user data

``data`` should be a dict. An existing properties not included in ``data`` will be ignored, not be deleted.

If ``user_id`` and ``channel`` is ``None``, it regarded as a message sender.


NLU Integeration
----------------

You can use ``nlu`` method to perform NLU after setup NLU integration at BotHub.Studio.

There are two styles to request to NLU service. (eg. to use API.ai)

First, use event object to construct message and session_id.

.. code:: python

          def handle_message(self, event, context):
              response = self.nlu('apiai').ask(event=event)
              self.send_message(response.next_message)

Or, put explicit message and session_id by yourself.

.. code:: python

          def handle_message(self, event, context):
              response = self.nlu('apiai').ask(message='hello', session_id='customer1')
              self.send_message(response.next_message)

``ask`` method returns a ``NluResponse`` object which contains attributes like:

* ``raw_response``: A raw response which NLU service returns.
* ``action``: A ``NluAction`` class object to identify intent and required parameters.
* ``next_message``: Next message text to respond NLU service recommend.

A ``NluAction`` object contains attributes like:

* ``intent``: Intent name
* ``parameters``: parameter dict
* ``completed``: A boolean indicates whether action completed

For incompleted action, you need to reply to user with ``next_message`` attribute of a NluResponse instance to complete action.


License
=======

This package is licensed under AGPLv3 for non-commercial personal use. If you want to use this package for commercial use, please contact to ``bothub@bothub.studio``.
	   
.. _Bothub.studio: https://bothub.studio?utm_source=pypi&utm_medium=display&utm_campaign=bothub
.. _bothub-cli: https://pypi.python.org/pypi/bothub-cli
