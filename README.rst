=========================================
BotHub: Chatbot Framework for easy deploy
=========================================

This package provide components to works with `BotHub.Studio`_, which is a chatbot hosting service.

With `bothub-cli`_, you can deploy a new chatbot with just four lines of commands.


Installation
============

To install bothub::

  $ pip install bothub

The bothub package works on python2 and 3 both.


Getting Started
===============

You can build a echo chatbot simply by subclassing ``BaseBot`` class and overriding ``handle_message`` method.

.. code:: python

   # -*- coding: utf-8 -*-
   
   from bothub_client.bot import BaseBot
   
   class Bot(BaseBot):
       """Represent a Bot logic which interacts with a user.
   
       BaseBot superclass have methods belows:
   
       * Send message
         * self.send_message(message, user_id=None, channel=None)
       * Data Storage
         * self.set_project_data(data)
         * self.get_project_data()
         * self.set_user_data(data, user_id=None, channel=None)
         * self.get_user_data(user_id=None, channel=None)
   
       When you omit user_id and channel argument, it regarded as a user
       who triggered a bot.
       """
   
       def handle_message(self, event, context):
           self.send_message(event['content'])



License
=======

This package is licensed under AGPLv3 for non-commercial personal use. If you want to use this package for commercial use, please contact to ``bothub@bothub.studio``.
	   
.. _Bothub.studio: https://bothub.studio?utm_source=pypi&utm_medium=display&utm_campaign=bothub
.. _bothub-cli: https://pypi.python.org/pypi/bothub-cli
