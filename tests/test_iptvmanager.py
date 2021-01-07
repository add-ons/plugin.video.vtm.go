# -*- coding: utf-8 -*-
""" Tests for IPTV Manager """

# pylint: disable=missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import socket
import unittest

from resources.lib import kodiutils

_LOGGER = logging.getLogger(__name__)


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestIptvManager(unittest.TestCase):

    def test_channels(self):
        # Prepare data (implementation from IPTV Manager)
        sock = self._prepare_for_data()

        # Make request trough routing
        from resources.lib.addon import routing
        routing.run(['plugin://plugin.video.vtm.go/iptv/channels', 0, 'port=' + str(sock.getsockname()[1])])

        # Wait for data (implementation from IPTV Manager)
        data = self._wait_for_data(sock)

        # Parse data
        result = json.loads(data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['version'], 1)
        self.assertIsInstance(result['streams'], list)

    def test_epg(self):
        # Prepare data (implementation from IPTV Manager)
        sock = self._prepare_for_data()

        # Make request trough routing
        from resources.lib.addon import routing
        routing.run(['plugin://plugin.video.vtm.go/iptv/epg', 0, 'port=' + str(sock.getsockname()[1])])

        # Wait for data (implementation from IPTV Manager)
        data = self._wait_for_data(sock)

        # Parse data
        result = json.loads(data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['version'], 1)
        self.assertIsInstance(result['epg'], dict)

    @staticmethod
    def _prepare_for_data():
        """Prepare ourselves so we can receive data"""
        # Bind on localhost on a free port above 1024
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))

        _LOGGER.debug('Bound on port %s...', sock.getsockname()[1])

        # Listen for one connection
        sock.listen(1)
        return sock

    def _wait_for_data(self, sock, timeout=10):
        """Wait for data to arrive on the socket"""
        # Set a connection timeout
        # The remote and should connect back as soon as possible so we know that the request is being processed
        sock.settimeout(timeout)

        try:
            _LOGGER.debug('Waiting for a connection on port %s...', sock.getsockname()[1])

            # Accept one client
            conn, addr = sock.accept()
            _LOGGER.debug('Connected to %s:%s! Waiting for result...', addr[0], addr[1])

            # We have no timeout when the connection is established
            conn.settimeout(None)

            # Read until the remote end closes the connection
            buf = ''
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk.decode()

            if not buf:
                # We got an empty reply, this means that something didn't go according to plan
                raise Exception('Something went wrong')

            return buf

        except socket.timeout:
            raise Exception('Timout waiting for reply on port %s' % sock.getsockname()[1])

        finally:
            # Close our socket
            _LOGGER.debug('Closing socket on port %s', sock.getsockname()[1])
            sock.close()


if __name__ == '__main__':
    unittest.main()
