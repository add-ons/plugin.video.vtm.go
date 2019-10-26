# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import warnings

from urllib3.exceptions import InsecureRequestWarning

from resources.lib.kodiwrapper import KodiWrapper
from resources.lib.vtmgo import vtmgo, vtmgostream, vtmgoauth
from resources.lib.vtmgo.vtmgostream import StreamGeoblockedException

kodi = KodiWrapper()


class TestVtmGo(unittest.TestCase):
    """ Tests for VTM GO API """

    def __init__(self, *args, **kwargs):
        super(TestVtmGo, self).__init__(*args, **kwargs)

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
        mylist = self._vtmgo.get_swimlane('my-list')
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
        try:
            info = self._vtmgostream.get_stream('episodes', 'ae0fa98d-6ed5-4f4a-8581-a051ed3bb755')
            self.assertTrue(info)
            # print(info)
        except StreamGeoblockedException:
            pass

        try:
            info = self._vtmgostream.get_stream('channels', 'd8659669-b964-414c-aa9c-e31d8d15696b')
            self.assertTrue(info)
            # print(info)
        except StreamGeoblockedException:
            pass

    def test_get_stream_with_subtitles(self):
        try:
            # 13 Geboden - Episode 2
            info = self._vtmgostream.get_stream('episodes', '2fafb247-0368-46d4-bdcf-fb209420e715')
            self.assertTrue(info)
            # print(info)
        except StreamGeoblockedException:
            pass


if __name__ == '__main__':
    unittest.main()
