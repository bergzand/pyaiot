# Copyright 2017 IoT-Lab Team
# Contributor(s) : see AUTHORS file
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""MQTT gateway application module."""

import sys
import logging
import tornado.platform.asyncio
from tornado.options import define, options

from pyaiot import global_settings
from pyaiot.common.auth import check_key_file, DEFAULT_KEY_FILENAME
from pyaiot.common.helpers import start_application, define_options

from .application import MQTTGatewayApplication
from .mqtt import MAX_TIME, MQTT_PORT, MQTT_HOST

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)14s - '
                           '%(levelname)5s - %(message)s')
logger = logging.getLogger("pyaiot.gw.mqtt")


def parse_command_line():
    """Parse command line arguments for CoAP gateway application."""
    define_options(MQTTGatewayApplication.settings + global_settings)
    options.parse_command_line()
    if options.config:
        options.parse_config_file(options.config)
    # Parse the command line a second time to override config file options
    options.parse_command_line()


def run(arguments=[]):
    """Start the CoAP gateway instance."""
    if arguments != []:
        sys.argv[1:] = arguments

    parse_command_line()

    if options.debug:
        logger.setLevel(logging.DEBUG)

    try:
        keys = check_key_file(options.key_file)
    except SyntaxError as e:
        logger.error("Invalid config file: {}".format(e))
        return
    except FileNotFoundError as e:
        logger.error("Config file not found: {}".format(e))
        return

    # Application ioloop initialization
    if not tornado.platform.asyncio.AsyncIOMainLoop().initialized():
        tornado.platform.asyncio.AsyncIOMainLoop().install()

    start_application(MQTTGatewayApplication(keys, options=options),
                      close_client=True)


if __name__ == '__main__':
    run()
