# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import json
import logging
import unittest

import xbmcaddon

from resources.lib import kodilogging, vtmgo, vtmgoauth, vtmgostream

ADDON = xbmcaddon.Addon()
kodilogging.config()
logger = logging.getLogger(ADDON.getAddonInfo('id'))


class TestVtmGo(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestVtmGo, self).__init__(*args, **kwargs)

        try:
            with open('test/credentials.json') as f:
                self._SETTINGS = json.load(f)
        except Exception as e:
            print("Error using 'test/credentials.json' : %s" % e, file=sys.stderr)

        self._vtmgo = vtmgo.VtmGo()
        self._vtmgoauth = vtmgoauth.VtmGoAuth(self._SETTINGS['username'], self._SETTINGS['password'])
        self._vtmgostream = vtmgostream.VtmGoStream()

        # Enable debug logging for urllib
        try:
            import http.client as http_client
        except ImportError:
            # Python 2
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1

        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def test_login(self):
        jwt = self._vtmgoauth.login()
        self.assertTrue(jwt)
        self._token = jwt

    def test_get_config(self):
        config = self._vtmgo.get_config()
        self.assertTrue(config)
        print(config)

    def test_get_main(self):
        main = self._vtmgo.get_main()
        self.assertTrue(main)
        print(main)

    def test_get_categories(self):
        categories = self._vtmgo.get_categories()
        self.assertTrue(categories)
        print(categories)

        items = self._vtmgo.get_items('films')
        self.assertTrue(items)
        print(items)

    def test_get_live(self):
        items = self._vtmgo.get_live()
        self.assertTrue(items)
        print(items)

    def test_get_program(self):
        info = self._vtmgo.get_program('e892cf10-5100-42ce-8d59-6b5c03cc2b96')
        self.assertTrue(info)
        print(info)

    # def test_get_episodes(self):
    #     info = self._vtmgo.get_episodes('ae0fa98d-6ed5-4f4a-8581-a051ed3bb755')
    #     self.assertTrue(info)
    #     print(info)

    def test_get_stream(self):
        info = self._vtmgostream.get_stream('episodes', 'ae0fa98d-6ed5-4f4a-8581-a051ed3bb755')
        self.assertTrue(info)
        print(info)

        info = self._vtmgostream.get_stream('channels', 'd8659669-b964-414c-aa9c-e31d8d15696b')
        self.assertTrue(info)
        print(info)


if __name__ == '__main__':
    unittest.main()
