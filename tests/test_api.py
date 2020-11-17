# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import xbmc

from resources.lib import kodiutils
from resources.lib.modules.player import Player
from resources.lib.vtmgo import Movie, Program
from resources.lib.vtmgo import vtmgo, vtmgostream, vtmgoauth, STOREFRONT_MAIN, STOREFRONT_MOVIES, STOREFRONT_SERIES
from resources.lib.vtmgo.vtmgostream import StreamGeoblockedException


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestApi(unittest.TestCase):
    """ Tests for VTM GO API """

    @classmethod
    def setUpClass(cls):
        cls._vtmgoauth = vtmgoauth.VtmGoAuth(kodiutils.get_setting('username'),
                                             kodiutils.get_setting('password'),
                                             'VTM',
                                             kodiutils.get_setting('profile'),
                                             kodiutils.get_tokens_path())
        cls._vtmgo = vtmgo.VtmGo(cls._vtmgoauth)
        cls._vtmgostream = vtmgostream.VtmGoStream()
        cls._player = Player()

    def tearDown(self):
        xbmc.Player().stop()

    def test_get_config(self):
        config = self._vtmgo.get_config()
        self.assertTrue(config)

    def test_catalog(self):
        categories = self._vtmgo.get_categories()
        self.assertTrue(categories)

        items = self._vtmgo.get_items()
        self.assertTrue(items)

        # Movies
        movie = next(a for a in items if isinstance(a, Movie) and not a.geoblocked)
        info = self._vtmgo.get_movie(movie.movie_id)
        self.assertTrue(info)
        try:
            self._player.play('movies', info.movie_id)
        except StreamGeoblockedException:
            pass

        # Programs
        program = next(a for a in items if isinstance(a, Program) and not a.geoblocked)
        info = self._vtmgo.get_program(program.program_id)
        self.assertTrue(info)

        season = list(info.seasons.values())[0]
        episode = list(season.episodes.values())[0]
        info = self._vtmgo.get_episode(episode.episode_id)
        self.assertTrue(info)
        try:
            self._player.play('episodes', info.episode_id)
        except StreamGeoblockedException:
            pass

    def test_recommendations(self):
        main_recommendations = self._vtmgo.get_recommendations(STOREFRONT_MAIN)
        self.assertIsInstance(main_recommendations, list)

        movie_recommendations = self._vtmgo.get_recommendations(STOREFRONT_MOVIES)
        self.assertIsInstance(movie_recommendations, list)

        serie_recommendations = self._vtmgo.get_recommendations(STOREFRONT_SERIES)
        self.assertIsInstance(serie_recommendations, list)

    def test_mylist(self):
        mylist = self._vtmgo.get_swimlane('my-list')
        self.assertIsInstance(mylist, list)

    def test_continuewatching(self):
        mylist = self._vtmgo.get_swimlane('continue-watching')
        self.assertIsInstance(mylist, list)

    def test_search(self):
        results = self._vtmgo.do_search('telefacts')
        self.assertIsInstance(results, list)

    def test_live(self):
        channel = self._vtmgo.get_live_channel('vtm')
        self.assertTrue(channel)

        try:
            self._player.play('channels', channel.channel_id)
        except (StreamGeoblockedException, Exception):  # pylint: disable=broad-except
            # TODO: fix this
            pass

    def test_mylist_ids(self):
        mylist = self._vtmgo.get_mylist_ids()
        self.assertIsInstance(mylist, list)

    def test_catalog_ids(self):
        mylist = self._vtmgo.get_catalog_ids()
        self.assertIsInstance(mylist, list)


if __name__ == '__main__':
    unittest.main()
