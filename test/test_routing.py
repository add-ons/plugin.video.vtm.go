# -*- coding: utf-8 -*-
""" Tests for Routing """

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import warnings

from urllib3.exceptions import InsecureRequestWarning

from resources.lib import plugin
from resources.lib.kodiwrapper import KodiWrapper

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')
xbmcplugin = __import__('xbmcplugin')
xbmcvfs = __import__('xbmcvfs')

routing = plugin.routing
kodi = KodiWrapper(routing=routing)


class TestRouting(unittest.TestCase):
    """ Tests for Routing """

    def __init__(self, *args, **kwargs):
        super(TestRouting, self).__init__(*args, **kwargs)

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)

        # Don't warn that we are not verifying the certificates of VTM GO API.
        warnings.simplefilter("ignore", InsecureRequestWarning)

    def test_main_menu(self):
        routing.run(['plugin://plugin.video.vtm.go/', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_index), 'plugin://plugin.video.vtm.go/')

    def test_metadata_update(self):
        routing.run(['plugin://plugin.video.vtm.go/metadata/clean', '0', ''])
        self.assertEqual(routing.url_for(plugin.metadata_clean), 'plugin://plugin.video.vtm.go/metadata/clean')
        routing.run(['plugin://plugin.video.vtm.go/metadata/update', '0', ''])
        self.assertEqual(routing.url_for(plugin.metadata_update), 'plugin://plugin.video.vtm.go/metadata/update')

    def test_kids_zone(self):
        plugin.run(['plugin://plugin.video.vtm.go/?kids=True', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_index, kids=True), 'plugin://plugin.video.vtm.go/?kids=True')

    # Check credentials: '/check-credentials'
    def test_check_credentials(self):
        plugin.run(['plugin://plugin.video.vtm.go/check-credentials', '0', ''])
        self.assertEqual(routing.url_for(plugin.check_credentials), 'plugin://plugin.video.vtm.go/check-credentials')

    # Live TV menu: '/livetv'
    def test_livetv_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/livetv', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_livetv), 'plugin://plugin.video.vtm.go/livetv')

    # Episodes menu: '/program/<program>'
    def test_program_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96', '0', ''])
        self.assertEqual(
            routing.url_for(plugin.show_program, program='e892cf10-5100-42ce-8d59-6b5c03cc2b96'),
            'plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96')

    # Episodes menu: '/program/<program>/<season>'
    def test_program_season_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96/all', '0', ''])
        self.assertEqual(
            routing.url_for(plugin.show_program_season, program='e892cf10-5100-42ce-8d59-6b5c03cc2b96', season='all'),
            'plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96/all')

    # Catalogue menu: '/catalog'
    def test_catalog_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/catalog', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_catalog), 'plugin://plugin.video.vtm.go/catalog')

    # Catalogue menu: '/catalog/<category>'
    def test_catalog_category_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/catalog/films', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_catalog_category, category='films'), 'plugin://plugin.video.vtm.go/catalog/films')
        plugin.run(['plugin://plugin.video.vtm.go/catalog/kids', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_catalog_category, category='kids'), 'plugin://plugin.video.vtm.go/catalog/kids')
        plugin.run(['plugin://plugin.video.vtm.go/catalog/nieuws-actua', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_catalog_category, category='nieuws-actua'), 'plugin://plugin.video.vtm.go/catalog/nieuws-actua')

    # YouTube menu: '/youtube'
    def test_youtube_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/youtube', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_youtube), 'plugin://plugin.video.vtm.go/youtube')

    # Search menu: '/search'
    def test_search_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/search', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_search), 'plugin://plugin.video.vtm.go/search')
        plugin.run(['plugin://plugin.video.vtm.go/search/nieuws', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_search, query='nieuws'), 'plugin://plugin.video.vtm.go/search/nieuws')

    # TV Guide menu: '/tvguide'
    def test_tvguide_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/tvguide', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_tvguide), 'plugin://plugin.video.vtm.go/tvguide')
        plugin.run(['plugin://plugin.video.vtm.go/tvguide/vtm', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_tvguide_channel, channel='vtm'), 'plugin://plugin.video.vtm.go/tvguide/vtm')
        plugin.run(['plugin://plugin.video.vtm.go/tvguide/vtm/today', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_tvguide_detail, channel='vtm', date='today'), 'plugin://plugin.video.vtm.go/tvguide/vtm/today')

    # Recommendations menu: '/recommendations'
    def test_recommendations_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/recommendations', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_recommendations), 'plugin://plugin.video.vtm.go/recommendations')
        plugin.run(['plugin://plugin.video.vtm.go/recommendations/775de6ef-003d-4571-8a6e-8433be0ef379', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_recommendations_category, category='775de6ef-003d-4571-8a6e-8433be0ef379'),
                         'plugin://plugin.video.vtm.go/recommendations/775de6ef-003d-4571-8a6e-8433be0ef379')

    # My List menu: '/mylist'
    def test_mylist_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/mylist', '0', ''])
        self.assertEqual(routing.url_for(plugin.show_mylist), 'plugin://plugin.video.vtm.go/mylist')

    # Play Live TV: '/play/livetv/<channel>'
    def test_play_livetv(self):
        plugin.run(['plugin://plugin.video.vtm.go/play/channels/ea826456-6b19-4612-8969-864d1c818347?.pvr', '0', ''])
        self.assertEqual(
            routing.url_for(plugin.play, category='channels', item='ea826456-6b19-4612-8969-864d1c818347?.pvr'),
            'plugin://plugin.video.vtm.go/play/channels/ea826456-6b19-4612-8969-864d1c818347?.pvr')

    # Play Movie: '/play/movie/<movie>'
    def test_play_movie(self):
        plugin.run(['plugin://plugin.video.vtm.go/play/movies/d1850498-941d-48cc-a558-37aaf37f4525', '0', ''])
        self.assertEqual(
            routing.url_for(plugin.play, category='movies', item='d1850498-941d-48cc-a558-37aaf37f4525'),
            'plugin://plugin.video.vtm.go/play/movies/d1850498-941d-48cc-a558-37aaf37f4525')

    # Play Episode: '/play/episode/<episode>'
    def test_play_episode(self):
        plugin.run(['plugin://plugin.video.vtm.go/play/episodes/ae0fa98d-6ed5-4f4a-8581-a051ed3bb755', '0', ''])
        self.assertEqual(
            routing.url_for(plugin.play, category='episodes', item='ae0fa98d-6ed5-4f4a-8581-a051ed3bb755'),
            'plugin://plugin.video.vtm.go/play/episodes/ae0fa98d-6ed5-4f4a-8581-a051ed3bb755')

    # Play from EPG: '/play/epg/<channel>/<datetime>'
    def test_play_epg(self):
        import dateutil
        import datetime
        timestamp = datetime.datetime.now(dateutil.tz.tzlocal())
        timestamp = timestamp.replace(hour=6, minute=0, second=0)
        plugin.run(['plugin://plugin.video.vtm.go/play/epg/vtm/' + timestamp.isoformat(), '0', ''])
        self.assertEqual(
            routing.url_for(plugin.play_epg_datetime, channel='vtm', timestamp=timestamp.isoformat()),
            'plugin://plugin.video.vtm.go/play/epg/vtm/' + timestamp.isoformat())


if __name__ == '__main__':
    unittest.main()
