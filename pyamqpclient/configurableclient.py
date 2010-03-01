"""
  Configurable AMQP Client
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

from __future__ import with_statement  # for Python 2.5 compatiblity
from ConfigParser import SafeConfigParser

from pyamqpclient.client import Client
from pyamqpclient.channel import Channel
from pyamqpclient.consumer import AckConsumer


class ClientWithFileConfig(Client):
    """Read the default AMQP connection information from a configuration file.
    Hook onto restart to grab new config information and save it back to the
    file.
    """

    CONNECTION_SETTINGS_SECTION = 'connection'

    def __init__(self, config_filename):
        self.config = SafeConfigParser()
        self.config.read(config_filename)
        self.config_fn = config_filename
        connection_settings = self.config.options(CONNECTION_SETTINGS_SECTION)
        Client.__init__(self, connection_settings)

    def restart(self, connection_settings):
        # save configuration
        for key, value in connection_settings.iteritems():
            self.config.set(CONNECTION_SETTINGS_SECTION, key, value)

        with open(self.config_fn, 'w') as fp:
            self.config.write(fp)

        Client.restart(self, connection_settings)


class ClientWithNetConfig(Client):
    """Create a secondary connection and bind a new queue to
    an exchange (amqp-config).
    """
    config_queue = Channel(AckConsumer, 'update_config', 'amqp-config',
                           {'durable': False, 'exclusive': False,
                            'auto_delete': False})

    def __init__(self, connection_settings):
        Client.__init__(self, connection_settings)
        self.setup_routing_key()

    def setup_routing_key(self):
        # Set the config_queue to accept messages regarding the
        # host we are connecting to.
        self.config_queue.set_routing_key(self.connection_settings['host'])

    def update_config(self, message):
        new_config = SafeConfigParser()
        new_config.read(message.body)
        connection_settings = new_config.options('default')
        self.restart(connection_settings)


class ClientWithNetAndFileConfig(ClientWithFileConfig, ClientWithNetConfig):
    def __init__(self, config_filename):
        ClientWithConfigFile.__init__(self, config_filename)
        self.setup_routing_key()
