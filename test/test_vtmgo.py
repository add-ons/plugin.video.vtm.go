# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import warnings

from urllib3.exceptions import InsecureRequestWarning

from resources.lib.kodiwrapper import KodiWrapper
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

    def test_catalog(self):
        categories = self._vtmgo.get_categories()
        self.assertTrue(categories)
        # print(categories)

        items = self._vtmgo.get_items('all')
        self.assertTrue(items)
        # print(items)

        # Movies
        movie = next(a for a in items if isinstance(a, Movie))
        info = self._vtmgo.get_movie(movie.movie_id)
        self.assertTrue(info)

        stream = self._vtmgostream.get_stream('movies', info.movie_id)
        self.assertTrue(stream)

        # Programs
        program = next(a for a in items if isinstance(a, Program))
        info = self._vtmgo.get_program(program.program_id)
        self.assertTrue(info)

        season = list(info.seasons.values())[0]
        episode = list(season.episodes.values())[0]
        info = self._vtmgo.get_episode(episode.episode_id)
        self.assertTrue(info)

        stream = self._vtmgostream.get_stream('episodes', info.episode_id)
        self.assertTrue(stream)

    def test_recommendations(self):
        recommendations = self._vtmgo.get_recommendations()
        self.assertTrue(recommendations)
        # print(main)

    def test_mylist(self):
        mylist = self._vtmgo.get_swimlane('my-list')
        self.assertIsInstance(mylist, list)
        # print(mylist)

    def test_live(self):
        items = self._vtmgo.get_live_channel('vtm')
        self.assertTrue(items)
        # print(items)

        try:
            info = self._vtmgostream.get_stream('channels', items.channel_id)
            self.assertTrue(info)
            # print(info)
        except StreamGeoblockedException:
            pass


if __name__ == '__main__':
    unittest.main()
