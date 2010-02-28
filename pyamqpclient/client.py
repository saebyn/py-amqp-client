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

from __future__ import with_statement # for Python 2.5 compatiblity
from amqplib import client_0_8 as amqp
from time import sleep
import threading

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
        self.routing_keys = {}

    def serve_forever(self):
        """Handle requests until an unhandled exception is raised.
        
        Use this method rather than start() and stop().
        """
        try:
            self.start()
            while threading.activeCount() > 1:
                sleep(0.1) # do nothing, just let the threads do their thing
        finally:
            return self.stop()

    def start(self):
        """Begin waiting for activity on each channel."""
        def channel_wait(channel):
            while channel.is_open():
                channel.wait()

        def thread_factory(channel):
            thread = threading.Thread(target=channel_wait,
                                      args=(channel,))
            thread.daemon = True
            return thread

        # start one thread per consumer/channel
        map(lambda ch: thread_factory(ch).start(), self.channels.values())

    def stop(self):
        """Stop all channels and close the connection.
        
        Calling this will not stop the serve_forever() loop.
        """
        for channel in self.channels.values():
            channel.stop()

        self.connection.close()

    def restart(self, connection_settings):
        """Restart the client with new connection settings.
        
        This is intended to be called from within a consumer callback, in
        a spawned thread.
        """

        # Lock this method, so that only one thread
        # can call it at a time (not that, in general, it's a good
        # idea to have more than one thread want to access this thread).
        lock = threading.Lock()
        with lock:
            self.stop()
            self.connection = amqp.Connection(**connection_settings)
            for prop, routing_key in self.routing_keys.iteritems():
                self.__getattr__(prop).set_routing_key(routing_key)
            self.start()

    def __getattr__(self, key):
        client = self

        class ConsumerCtl:
            def set_routing_key(self, routing_key):
                """Set the routing key for this consumer and start channel."""
                # save the routing key, in case we need to restart the
                # connection.
                client.routing_keys[key] = routing_key
                # start the channel
                client.channels[key].start(client, key, routing_key)

        if key in self.channels:
            return ConsumerCtl()
