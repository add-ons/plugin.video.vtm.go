# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import plugin

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')
xbmcplugin = __import__('xbmcplugin')
xbmcvfs = __import__('xbmcvfs')

addon = plugin.plugin


class TestRouter(unittest.TestCase):

    def test_main_menu(self):
        addon.run(['plugin://plugin.video.vtm.go/', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_index), 'plugin://plugin.video.vtm.go/')

    def test_kids_zone(self):
        plugin.run(['plugin://plugin.video.vtm.go/kids', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_index), 'plugin://plugin.video.vtm.go/kids')

    # Check credentials: '/check-credentials'
    #    def test_check_credentials(self):
    #        plugin.run(['plugin://plugin.video.vtm.go/check-credentials', '0', ''])
    #        self.assertEqual(addon.url_for(plugin.check_credentials), 'plugin://plugin.video.vtm.go/check-credentials')

    # Live TV menu: '/livetv'
    def test_livetv_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/livetv', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_livetv), 'plugin://plugin.video.vtm.go/livetv')
        plugin.run(['plugin://plugin.video.vtm.go/kids/livetv', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_livetv), 'plugin://plugin.video.vtm.go/kids/livetv')

    # Episodes menu: '/program/<program>'
    def test_program_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96', '0', ''])
        self.assertEqual(
            addon.url_for(plugin.show_program, program='e892cf10-5100-42ce-8d59-6b5c03cc2b96'),
            'plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96')

    # Episodes menu: '/program/<program>/<season>'
    def test_program_season_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96/all', '0', ''])
        self.assertEqual(
            addon.url_for(plugin.show_program_season, program='e892cf10-5100-42ce-8d59-6b5c03cc2b96', season='all'),
            'plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96/all')

    # Catalogue menu: '/catalog'
    def test_catalog_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/catalog', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_catalog), 'plugin://plugin.video.vtm.go/catalog')
        plugin.run(['plugin://plugin.video.vtm.go/kids/catalog', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_catalog), 'plugin://plugin.video.vtm.go/kids/catalog')

    # Catalogue menu: '/catalog/<category>'
    def test_catalog_category_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/catalog/films', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_catalog_category, category='films'), 'plugin://plugin.video.vtm.go/catalog/films')
        plugin.run(['plugin://plugin.video.vtm.go/kids/catalog/films', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_catalog_category, category='films'), 'plugin://plugin.video.vtm.go/kids/catalog/films')
        plugin.run(['plugin://plugin.video.vtm.go/catalog/kids', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_catalog_category, category='kids'), 'plugin://plugin.video.vtm.go/catalog/kids')
        plugin.run(['plugin://plugin.video.vtm.go/catalog/nieuws-actua', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_catalog_category, category='nieuws-actua'), 'plugin://plugin.video.vtm.go/catalog/nieuws-actua')

    # YouTube menu: '/youtube'
    def test_youtube_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/youtube', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_youtube), 'plugin://plugin.video.vtm.go/youtube')
        plugin.run(['plugin://plugin.video.vtm.go/kids/youtube', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_youtube), 'plugin://plugin.video.vtm.go/kids/youtube')

    # Search menu: '/search'
    def test_search_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/search', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_search), 'plugin://plugin.video.vtm.go/search')
        plugin.run(['plugin://plugin.video.vtm.go/kids/search', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_search), 'plugin://plugin.video.vtm.go/kids/search')

    # TV Guide menu: '/tvguide'
    def test_tvguide_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/tvguide', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_tvguide), 'plugin://plugin.video.vtm.go/tvguide')
        plugin.run(['plugin://plugin.video.vtm.go/kids/tvguide', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_tvguide), 'plugin://plugin.video.vtm.go/kids/tvguide')
        plugin.run(['plugin://plugin.video.vtm.go/tvguide/vtm', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_tvguide_channel, channel='vtm'), 'plugin://plugin.video.vtm.go/tvguide/vtm')
        plugin.run(['plugin://plugin.video.vtm.go/tvguide/vtm/today', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_tvguide_detail, channel='vtm', date='today'), 'plugin://plugin.video.vtm.go/tvguide/vtm/today')

    # Play Live TV: '/play/livetv/<channel>'
    def test_play_livetv(self):
        plugin.run(['plugin://plugin.video.vtm.go/play/channels/ea826456-6b19-4612-8969-864d1c818347?.pvr', '0', ''])
        self.assertEqual(
            addon.url_for(plugin.play, category='channels', item='ea826456-6b19-4612-8969-864d1c818347?.pvr'),
            'plugin://plugin.video.vtm.go/play/channels/ea826456-6b19-4612-8969-864d1c818347?.pvr')

    # Play Movie: '/play/movie/<movie>'
    def test_play_movie(self):
        plugin.run(['plugin://plugin.video.vtm.go/play/movies/d1850498-941d-48cc-a558-37aaf37f4525', '0', ''])
        self.assertEqual(
            addon.url_for(plugin.play, category='movies', item='d1850498-941d-48cc-a558-37aaf37f4525'),
            'plugin://plugin.video.vtm.go/play/movies/d1850498-941d-48cc-a558-37aaf37f4525')

    # Play Episode: '/play/episode/<episode>'
    def test_play_episode(self):
        plugin.run(['plugin://plugin.video.vtm.go/play/episodes/ae0fa98d-6ed5-4f4a-8581-a051ed3bb755', '0', ''])
        self.assertEqual(
            addon.url_for(plugin.play, category='episodes', item='ae0fa98d-6ed5-4f4a-8581-a051ed3bb755'),
            'plugin://plugin.video.vtm.go/play/episodes/ae0fa98d-6ed5-4f4a-8581-a051ed3bb755')


if __name__ == '__main__':
    unittest.main()
