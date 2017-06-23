0.1.19
------

* refactor and add docstrings

0.1.18
------

* use chat_id as an argument name instead of user_id

0.1.17
------

* fix invalid method signature usage

0.1.16
------

* use chat_id as a default for ZmqChannelClient

0.1.15
------

* use chat_id as a default

0.1.14
------

* give higher priority to payload argument

0.1.13
------

* add a repr method to Message class
* fix: Message.set_text returns nothing
* fix: add payload argument which Facebook Messenger requires


0.1.12
------

* fix a bug which ``Message.set_text`` returns nothing

0.1.11
------

* add rich widget message

0.1.10
------

* change ask method to use also with an event object
* set an user who sent a message as a default user for storage client

0.1.9
-----

* fix NLU response

0.1.8
-----

* add NLU integration support

0.1.7
-----

* add ``extra`` argument

0.1.6
-----

* remove unnessary overrides

0.1.5
-----

* fix unmatched zmq protocol

0.1.4
-----

* fix ``ZmqChannelClient`` invalid default transport object

0.1.3
-----

* fix ``ZmqTransport`` send_json method signature mismatch

0.1.2
-----

* add a ``ZmqChannelClient`` class
* pass event object to channel client

0.1.1
-----

* add a ``ConsoleChannelClient`` and ``LocMemStorageClient`` classes


0.1.0
-----

* initial release
