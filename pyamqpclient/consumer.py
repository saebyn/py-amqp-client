"""
  AMQP Consumer Behaviours
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


class Consumer:
    """AMQP Consumer callback wrapper.

    # Simple callback
    >>> def test(message): return "success"

    # Create a consumer instance
    >>> consumer = Consumer(None, test)
    # Execute the callback
    >>> consumer(None)
    "success"
    """
    def __init__(self, channel, callback):
        self.channel = channel
        self.callback = callback

    def __call__(self, message):
        return self.callback(message)

class NoAckConsumer(Consumer):
    """Delivers message to callback and does not return an ack to origin."""
    pass

class AckConsumer(Consumer):
    """Delivers message to callback and returns an ack to origin."""
    def __call__(self, message):
        ret = Consumer.__call__(self, message)
        self.channel.basic_ack(message.delivery_tag)
        return ret

class ReplyingConsumer(AckConsumer):
    """Delivers message to callback and publishes returned response message."""
    def __call__(self, message):
        response = AckConsumer.__call__(self, message)
        self.channel.basic_publish(response, routing_key=message.reply_to)
        return response
