# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import xbmc

from resources.lib import kodiutils
from resources.lib.modules.player import Player
from resources.lib.vtmgo import Movie, Program, Category
from resources.lib.vtmgo import STOREFRONT_MAIN, STOREFRONT_MOVIES, STOREFRONT_SERIES
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestApi(unittest.TestCase):
    """ Tests for VTM GO API """

    @classmethod
    def setUpClass(cls):
        cls.auth = VtmGoAuth(kodiutils.get_setting('username'),
                             kodiutils.get_setting('password'),
                             'VTM',
                             kodiutils.get_setting('profile'),
                             kodiutils.get_tokens_path())
        cls.api = VtmGo(cls.auth)
        cls.player = Player()

    def tearDown(self):
        xbmc.Player().stop()

    def test_get_config(self):
        config = self.api.get_config()
        self.assertTrue(config)

    def test_catalog(self):
        items = self.api.get_items()
        self.assertTrue(items)

        # Movies
        movie = next(a for a in items if isinstance(a, Movie) and not a.geoblocked)
        info = self.api.get_movie(movie.movie_id)
        self.assertTrue(info)
        self.player.play('movies', info.movie_id)

        # Programs
        program = next(a for a in items if isinstance(a, Program) and not a.geoblocked)
        info = self.api.get_program(program.program_id)
        self.assertTrue(info)

        season = list(info.seasons.values())[0]
        episode = list(season.episodes.values())[0]
        info = self.api.get_episode(episode.episode_id)
        self.assertTrue(info)
        self.player.play('episodes', info.episode_id)

    def test_recommendations(self):
        results = self.api.get_storefront(STOREFRONT_MAIN)
        self.assertIsInstance(results, list)

        results = self.api.get_storefront_category(STOREFRONT_MOVIES, '9ab6cd7b-ee12-4177-b205-6e8cefea9833')  # Drama
        self.assertIsInstance(results, Category)
        self.assertIsInstance(results.content, list)

        results = self.api.get_storefront(STOREFRONT_MOVIES)
        self.assertIsInstance(results, list)

        results = self.api.get_storefront(STOREFRONT_SERIES)
        self.assertIsInstance(results, list)

    def test_mylist(self):
        mylist = self.api.get_swimlane('my-list')
        self.assertIsInstance(mylist, list)

    def test_continuewatching(self):
        mylist = self.api.get_swimlane('continue-watching')
        self.assertIsInstance(mylist, list)

    def test_search(self):
        results = self.api.do_search('telefacts')
        self.assertIsInstance(results, list)

    def test_live(self):
        channel = self.api.get_live_channel('vtm')
        self.assertTrue(channel)
        self.player.play('channels', channel.channel_id)

    def test_mylist_ids(self):
        mylist = self.api.get_mylist_ids()
        self.assertIsInstance(mylist, list)

    def test_catalog_ids(self):
        mylist = self.api.get_catalog_ids()
        self.assertIsInstance(mylist, list)


if __name__ == '__main__':
    unittest.main()
