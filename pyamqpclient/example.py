"""
  py-amqp-client example.
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

from client import Client
from channel import Channel
from consumer import AckConsumer

class OurClient(Client):
    consumer = Channel(AckConsumer, 'callback1', 'exchange',
                           {'durable': False, 'exclusive': False,
                            'auto_delete': False})

    def callback1(self, message):
        print message.body
        return None

client = OurClient(connection_settings)
client.consumer.set_routing_key('')
try:
    client.start()
finally:
    client.stop()


