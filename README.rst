
py-amqp-client
==============

Purpose
-------

I need:

1. A generic AMQP consumer that receives messages that change the IP address
used to access the AMQP broker.
2. An clean way of implementing an AMQP client that can support #1.

py-amqp-client provides a base class that is easily overridden to create
custom AMQP clients that will automatically update their connection
settings once certain messages are received on a secondary channel.

Requirements
------------

* py-amqplib is used to interface with the AMQP broker.
* Developed for Python 2.6

