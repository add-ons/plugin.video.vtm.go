# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib.kodiwrapper import KodiWrapper
from resources.lib.modules.player import Player
from resources.lib.vtmgo import vtmgo, vtmgostream, vtmgoauth
from resources.lib.vtmgo.vtmgo import Movie, Program
from resources.lib.vtmgo.vtmgostream import StreamGeoblockedException

kodi = KodiWrapper()


class TestVtmGo(unittest.TestCase):
    """ Tests for VTM GO API """

    def __init__(self, *args, **kwargs):
        super(TestVtmGo, self).__init__(*args, **kwargs)

        self._vtmgoauth = vtmgoauth.VtmGoAuth(kodi)
        self._vtmgo = vtmgo.VtmGo(kodi)
        self._vtmgostream = vtmgostream.VtmGoStream(kodi)
        self._player = Player(kodi)

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)
        pass

    @unittest.skipUnless(kodi.has_credentials(), 'Skipping since we have no credentials.')
    def test_login(self):
        token = self._vtmgoauth.get_token()
        self.assertTrue(token)

    def test_get_config(self):
        config = self._vtmgo.get_config()
        self.assertTrue(config)

    @unittest.skipUnless(kodi.has_credentials(), 'Skipping since we have no credentials.')
    def test_get_profiles(self):
        profiles = self._vtmgo.get_profiles()
        self.assertTrue(profiles)

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
        recommendations = self._vtmgo.get_recommendations()
        self.assertTrue(recommendations)

    def test_mylist(self):
        mylist = self._vtmgo.get_swimlane('my-list')
        self.assertIsInstance(mylist, list)

    def test_continuewatching(self):
        mylist = self._vtmgo.get_swimlane('continue-watching')
        self.assertIsInstance(mylist, list)

    def test_live(self):
        channel = self._vtmgo.get_live_channel('vtm')
        self.assertTrue(channel)

        try:
            self._player.play('channels', channel.channel_id)
        except StreamGeoblockedException:
            pass


if __name__ == '__main__':
    unittest.main()
