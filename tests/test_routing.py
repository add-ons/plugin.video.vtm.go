# -*- coding: utf-8 -*-
""" Tests for Routing """

# pylint: disable=invalid-name,missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import plugin
from resources.lib.kodiwrapper import KodiWrapper

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')
xbmcplugin = __import__('xbmcplugin')
xbmcvfs = __import__('xbmcvfs')

routing = plugin.routing
kodi = KodiWrapper(globals())


class TestRouting(unittest.TestCase):
    """ Tests for Routing """

    def __init__(self, *args, **kwargs):
        super(TestRouting, self).__init__(*args, **kwargs)

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)
        pass

    def test_main_menu(self):
        routing.run([routing.url_for(plugin.show_main_menu), '0', ''])

    def test_channels_menu(self):
        plugin.run([routing.url_for(plugin.show_channels), '0', ''])
        plugin.run([routing.url_for(plugin.show_channel_menu, channel='vtm'), '0', ''])

    def test_catalog_menu(self):
        plugin.run([routing.url_for(plugin.show_catalog), '0', ''])
        plugin.run([routing.url_for(plugin.show_catalog_all), '0', ''])

    def test_catalog_category_menu(self):
        plugin.run([routing.url_for(plugin.show_catalog_category, category='films'), '0', ''])

    def test_catalog_channel_menu(self):
        plugin.run([routing.url_for(plugin.show_catalog_channel, channel='vtm'), '0', ''])

    def test_catalog_program_menu(self):
        plugin.run([routing.url_for(plugin.show_catalog_program, program='e892cf10-5100-42ce-8d59-6b5c03cc2b96'), '0', ''])

    def test_catalog_program_season_menu(self):
        plugin.run([routing.url_for(plugin.show_catalog_program_season, program='e892cf10-5100-42ce-8d59-6b5c03cc2b96', season=-1), '0', ''])

    def test_catalog_recommendations_menu(self):
        plugin.run([routing.url_for(plugin.show_recommendations), '0', ''])
        plugin.run([routing.url_for(plugin.show_recommendations_category, category='775de6ef-003d-4571-8a6e-8433be0ef379'), '0', ''])

    def test_catalog_mylist_menu(self):
        plugin.run([routing.url_for(plugin.show_mylist), '0', ''])

    def test_catalog_continuewatching_menu(self):
        plugin.run([routing.url_for(plugin.show_continuewatching), '0', ''])

    def test_search_menu(self):
        plugin.run([routing.url_for(plugin.show_search), '0', ''])
        plugin.run([routing.url_for(plugin.show_search, query='nieuws'), '0', ''])

    def test_tvguide_menu(self):
        plugin.run([routing.url_for(plugin.show_tvguide_channel, channel='vtm'), '0', ''])
        plugin.run([routing.url_for(plugin.show_tvguide_detail, channel='vtm', date='today'), '0', ''])

    def test_play_livetv(self):
        plugin.run([routing.url_for(plugin.play, category='channels', item='ea826456-6b19-4612-8969-864d1c818347?.pvr'), '0', ''])

    def test_play_movie(self):
        plugin.run([routing.url_for(plugin.play, category='movies', item='d1850498-941d-48cc-a558-37aaf37f4525'), '0', ''])

    def test_play_episode(self):
        plugin.run([routing.url_for(plugin.play, category='episodes', item='ae0fa98d-6ed5-4f4a-8581-a051ed3bb755'), '0', ''])

    def test_play_epg(self):
        import dateutil
        import datetime
        timestamp = datetime.datetime.now(dateutil.tz.tzlocal()).replace(hour=6, minute=0, second=0)
        plugin.run([routing.url_for(plugin.play_epg_datetime, channel='vtm', timestamp=timestamp.isoformat()), '0', ''])

    def test_metadata_update(self):
        routing.run([routing.url_for(plugin.metadata_clean), '0', ''])
        routing.run([routing.url_for(plugin.metadata_update), '0', ''])


if __name__ == '__main__':
    unittest.main()
