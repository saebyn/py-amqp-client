"""
  AMQP Channel
"""
#
# Copyright (c) 2010 John Weaver
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from amqplib import client_0_8 as amqp

assert(__name__ == 'pyamqpclient.channel')


class Channel(object):
    def __init__(self, consumer, handler, exchange, options={}):
        """Save declarative options for later `start` method.

        Options are the same as those for amqp.Channel.queue_declare().
        """
        self.consumer = consumer
        self.handler = handler
        self.exchange = exchange
        self.queue_options = options
        self.is_stopped = True

    def start(self, client, queue_name, routing_key):
        """Initialize the channel , create the queue `queue_name`,
        use `routing_key` to bind the queue to the exchange, and
        register the consumer callback.
        """
        self.channel = client.connection.channel()
        self.is_stopped = False

        # Create queue
        self.channel.queue_declare(queue=queue_name, **self.queue_options)

        # Bind queue to exchange, with routing_key
        self.channel.queue_bind(queue=queue_name, exchange=self.exchange,
                                routing_key=routing_key)

        # Initialize consumer class with channel and provided handler

        # If handler is a string, assume it's the name of a method of
        # the client.
        if isinstance(self.handler, str):
            self.handler = getattr(client, self.handler)

        callback = self.consumer(self.channel, self.handler)

        # Bind consumer to queue
        no_ack = not self.consumer.ack
        self.consumer_tag = self.channel.basic_consume(queue=queue_name,
                                                       callback=callback,
                                                       no_ack=no_ack)

    def wait(self):
        """Wait for activity"""
        try:
            self.channel.wait()
        except:
            self.stop()

    def is_open(self):
        """Returns a boolean indicating if the channel is open."""
        return self.channel.is_open and not self.is_stopped

    def stop(self):
        """Cancel the consumer callback and close the channel.
        """
        try:
            self.channel.basic_cancel(self.consumer_tag)
            self.channel.close()
        finally:
            self.is_stopped = True # stop the thread whether the channel
                                   # successful tells the server that
                                   # we've closed it or not.
