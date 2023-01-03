# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import xbmc

from resources.lib import kodiutils
from resources.lib.modules.player import Player
from resources.lib.vtmgo import STOREFRONT_MAIN, STOREFRONT_MOVIES, STOREFRONT_SHORTIES, Category
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth


class TestApi(unittest.TestCase):
    """ Tests for VTM GO API """

    @classmethod
    def setUpClass(cls):
        auth = VtmGoAuth(kodiutils.get_tokens_path())
        cls.api = VtmGo(auth.get_tokens())
        cls.player = Player()

    def tearDown(self):
        xbmc.Player().stop()

    def test_get_config(self):
        config = self.api.get_config()
        self.assertTrue(config)

    def test_recommendations(self):
        results = self.api.get_storefront(STOREFRONT_MAIN)
        self.assertIsInstance(results, list)

        results = self.api.get_storefront_category(STOREFRONT_MOVIES, '9ab6cd7b-ee12-4177-b205-6e8cefea9833')  # Drama
        self.assertIsInstance(results, Category)
        self.assertIsInstance(results.content, list)

        results = self.api.get_storefront(STOREFRONT_MOVIES)
        self.assertIsInstance(results, list)

        results = self.api.get_storefront(STOREFRONT_SHORTIES)
        self.assertIsInstance(results, list)

    def test_mylist(self):
        mylist = self.api.get_mylist()
        self.assertIsInstance(mylist, list)

    def test_search(self):
        results = self.api.do_search('telefacts')
        self.assertIsInstance(results, list)

    def test_live(self):
        channel = self.api.get_live_channel('vtm')
        self.assertTrue(channel)
        self.player.play('channels', channel.channel_id)


if __name__ == '__main__':
    unittest.main()
