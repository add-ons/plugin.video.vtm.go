# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os
import unittest
import warnings

from urllib3.exceptions import InsecureRequestWarning

from resources.lib import plugin, kodilogging
from resources.lib.vtmgo import vtmgoauth

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')
xbmcplugin = __import__('xbmcplugin')
xbmcvfs = __import__('xbmcvfs')

addon = plugin.plugin

logger = kodilogging.get_logger('TestRouting')


class TestRouting(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRouting, self).__init__(*args, **kwargs)

        # Read credentials from credentials.json
        settings = {}
        if 'VTMGO_USERNAME' in os.environ and 'VTMGO_PASSWORD' in os.environ:
            logger.warning('Using credentials from the environment variables VTMGO_USERNAME and VTMGO_PASSWORD')
            settings['username'] = os.environ.get('VTMGO_USERNAME')
            settings['password'] = os.environ.get('VTMGO_PASSWORD')
        else:
            with open('test/userdata/credentials.json') as f:
                settings = json.load(f)

        if settings['username'] and settings['password']:
            vtmgoauth.VtmGoAuth.username = settings['username']
            vtmgoauth.VtmGoAuth.password = settings['password']

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)

        # Don't warn that we are not verifying the certificates of VTM GO API.
        warnings.simplefilter("ignore", InsecureRequestWarning)

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
        plugin.run(['plugin://plugin.video.vtm.go/search/nieuws', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_search, query='nieuws'), 'plugin://plugin.video.vtm.go/search/nieuws')
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

    # Recommendations menu: '/recommendations'
    def test_recommendations_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/recommendations', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_recommendations), 'plugin://plugin.video.vtm.go/recommendations')
        plugin.run(['plugin://plugin.video.vtm.go/kids/recommendations', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_recommendations), 'plugin://plugin.video.vtm.go/kids/recommendations')
        plugin.run(['plugin://plugin.video.vtm.go/recommendations/775de6ef-003d-4571-8a6e-8433be0ef379', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_recommendations_category, category='775de6ef-003d-4571-8a6e-8433be0ef379'),
                         'plugin://plugin.video.vtm.go/recommendations/775de6ef-003d-4571-8a6e-8433be0ef379')

    # My List menu: '/mylist'
    def test_mylist_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/mylist', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_mylist), 'plugin://plugin.video.vtm.go/mylist')
        plugin.run(['plugin://plugin.video.vtm.go/kids/mylist', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_kids_mylist), 'plugin://plugin.video.vtm.go/kids/mylist')

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

    # Play from EPG: '/play/epg/<channel>/<datetime>'
    def test_play_epg(self):
        import dateutil
        import datetime
        timestamp = datetime.datetime.now(dateutil.tz.tzlocal())
        plugin.run(['plugin://plugin.video.vtm.go/play/epg/vtm/' + timestamp.isoformat(), '0', ''])
        self.assertEqual(
            addon.url_for(plugin.play_epg_datetime, channel='vtm', timestamp=timestamp.isoformat()),
            'plugin://plugin.video.vtm.go/play/epg/vtm/' + timestamp.isoformat())


if __name__ == '__main__':
    unittest.main()
