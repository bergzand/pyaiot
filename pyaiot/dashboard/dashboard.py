#!/usr/bin/env python

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

"""Web dashboard tornado application module."""

import os
import os.path
import sys
import logging
import tornado
from tornado import web
from tornado.options import define, options

from pyaiot import global_settings
from pyaiot.common.auth import DEFAULT_KEY_FILENAME
from pyaiot.common.helpers import start_application, define_options

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)14s - '
                           '%(levelname)5s - %(message)s')
logger = logging.getLogger("pyaiot.dashboard")


class DashboardHandler(web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, path=None):
        self.render("dashboard.html",
                    wsproto="wss" if options.broker_ssl else "ws",
                    wsserver="{}:{}".format(options.broker_host,
                                            options.broker_port),
                    camera_url=options.camera_url,
                    favicon=options.favicon,
                    logo_url=options.logo,
                    title=options.title)


class IoTDashboardApplication(web.Application):
    """Tornado based web application providing an IoT Dashboard."""

    settings = [
        {'name': 'static_path', 'default': os.path.join(os.path.dirname(__file__), "static"),
         'help': 'Static files path (containing npm package.json file)'},
        {'name': 'web_port', 'default': 8080, 'help': 'Web application HTTP port'},
        {'name': 'broker_port', 'default': 8000, 'help': 'Broker websocket port'},
        {'name': 'broker_host', 'default': 'localhost', 'help': 'Broker hostname'},
        {'name': 'broker_ssl', 'type': bool, 'default': False, 'help': 'Supply the broker websocket with ssl'},
        {'name': 'key_file', 'default': DEFAULT_KEY_FILENAME, 'help': "Secret and private keys filename."},
        {'name': 'camera_url', 'default': None, 'help': "Default camera url"},
        {'name': 'title', 'default': "IoT Dashboard", 'help': "Dashboard title"},
        {'name': 'logo', 'default': None, 'help': "URL for a logo in the dashboard navbar"},
        {'name': "favicon", 'default': None, 'help': "Favicon url for your dashboard site"}
    ]

    def __init__(self):
        self._nodes = {}
        if options.debug:
            logger.setLevel(logging.DEBUG)

        handlers = [
            (r'/', DashboardHandler),
        ]
        settings = {'debug': True,
                    "cookie_secret": "MY_COOKIE_ID",
                    "xsrf_cookies": False,
                    'static_path': options.static_path,
                    'template_path': options.static_path
                    }
        super().__init__(handlers, **settings)
        logger.info('Application started, listening on port {0}'
                    .format(options.web_port))


def parse_command_line():
    """Parse command line arguments for IoT broker application."""
    define_options(IoTDashboardApplication.settings + global_settings)
    options.parse_command_line()
    if options.config:
        options.parse_config_file(options.config)
    # Parse the command line a second time to override config file options
    options.parse_command_line()

def run(arguments=[]):
    """Start an instance of a dashboard."""
    if arguments != []:
        sys.argv[1:] = arguments
    try:
        parse_command_line()
    except SyntaxError as e:
        logger.error("Invalid config file: {}".format(e))
        return
    except FileNotFoundError as e:
        logger.error("Config file not found: {}".format(e))
        return

    if options.debug:
        logger.setLevel(logging.DEBUG)

    start_application(IoTDashboardApplication(), port=options.web_port)


if __name__ == '__main__':
    run()
