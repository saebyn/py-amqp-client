"""
  AMQP Client
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

from pyamqpclient.channel import Channel


class ClientMetaclass(type):
    def __new__(cls, name, bases, attrs):
        channels = dict([(name, attr) for name, attr in attrs.iteritems()
                         if isinstance(attr, Channel)])
        for attr in channels:
            attrs.pop(attr)

        new_cls = super(ClientMetaclass, cls).__new__(cls, name, bases, attrs)
        new_cls.channels = channels
        return new_cls


class Client(object):
    __metaclass__ = ClientMetaclass

    def __init__(self, connection_settings):
        """Start AMQP connection.

        `connection_settings` are passed as keyword arguments to
        amqp.Connection.__init__().
        """
        self.connection = amqp.Connection(**connection_settings)

    def serve_forever(self):
        """Handle requests until an unhandled exception is raised"""
        try:
            self.start()
        finally:
            return self.stop()

    def start(self):
        """Begin waiting for activity on each channel."""
        while True:
            for channel in self.channels.values():
                channel.wait()

    def stop(self):
        """Stop all channels and close the connection."""
        pass

    def __getattr__(self, key):
        client = self

        class ConsumerCtl:
            def set_routing_key(self, routing_key):
                """Set the routing key for this consumer and start channel."""
                client.channels[key].start(client, key, routing_key)
                return self

        if key in self.channels:
            return ConsumerCtl()
