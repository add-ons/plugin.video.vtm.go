# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os
import unittest
import warnings

from urllib3.exceptions import InsecureRequestWarning

from resources.lib.kodiwrapper import KodiWrapper, LOG_WARNING
from resources.lib.vtmgo import vtmgo, vtmgostream, vtmgoauth

kodi = KodiWrapper()


class TestVtmGo(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestVtmGo, self).__init__(*args, **kwargs)

        # Read credentials from credentials.json
        settings = {}
        if 'VTMGO_USERNAME' in os.environ and 'VTMGO_PASSWORD' in os.environ:
            kodi.log('Using credentials from the environment variables VTMGO_USERNAME and VTMGO_PASSWORD', log_level=LOG_WARNING)
            settings['username'] = os.environ.get('VTMGO_USERNAME')
            settings['password'] = os.environ.get('VTMGO_PASSWORD')
        else:
            with open('test/userdata/credentials.json') as f:
                settings = json.load(f)

        if settings['username'] and settings['password']:
            kodi.set_setting('username', settings['username'])
            kodi.set_setting('password', settings['password'])

        self._vtmgoauth = vtmgoauth.VtmGoAuth(kodi)
        self._vtmgo = vtmgo.VtmGo(kodi)
        self._vtmgostream = vtmgostream.VtmGoStream(kodi)

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)

        # Don't warn that we are not verifying the certificates of VTM GO API.
        warnings.simplefilter("ignore", InsecureRequestWarning)

    def test_login(self):
        token = self._vtmgoauth.get_token()
        self.assertTrue(token)

    def test_get_config(self):
        config = self._vtmgo.get_config()
        self.assertTrue(config)
        # print(config)

    def test_get_recommendations(self):
        recommendations = self._vtmgo.get_recommendations()
        self.assertTrue(recommendations)
        # print(main)

    def test_get_mylist(self):
        mylist = self._vtmgo.get_mylist()
        self.assertIsInstance(mylist, list)
        # print(mylist)

    def test_get_categories(self):
        categories = self._vtmgo.get_categories()
        self.assertTrue(categories)
        # print(categories)

        items = self._vtmgo.get_items('films')
        self.assertTrue(items)
        # print(items)

    def test_get_live(self):
        items = self._vtmgo.get_live_channels()
        self.assertTrue(items)
        # print(items)

    def test_get_program(self):
        info = self._vtmgo.get_program('e892cf10-5100-42ce-8d59-6b5c03cc2b96')
        self.assertTrue(info)
        # print(info)

    def test_get_episode(self):
        info = self._vtmgo.get_episode('ae0fa98d-6ed5-4f4a-8581-a051ed3bb755')
        self.assertTrue(info)
        # print(info)

    def test_get_stream(self):
        info = self._vtmgostream.get_stream('episodes', 'ae0fa98d-6ed5-4f4a-8581-a051ed3bb755')
        self.assertTrue(info)
        # print(info)

        info = self._vtmgostream.get_stream('channels', 'd8659669-b964-414c-aa9c-e31d8d15696b')
        self.assertTrue(info)
        # print(info)

    def test_get_stream_with_subtitles(self):
        # 13 Geboden - Episode 2
        info = self._vtmgostream.get_stream('episodes', '2fafb247-0368-46d4-bdcf-fb209420e715')
        self.assertTrue(info)
        # print(info)


if __name__ == '__main__':
    unittest.main()
