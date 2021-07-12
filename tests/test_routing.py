# -*- coding: utf-8 -*-
""" Tests for Routing """

# pylint: disable=invalid-name,missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

import xbmc

from resources.lib import addon
from resources.lib import kodiutils
from resources.lib.vtmgo import STOREFRONT_MAIN

routing = addon.routing

_LOGGER = logging.getLogger(__name__)

EXAMPLE_CHANNEL = 'ea826456-6b19-4612-8969-864d1c818347'  # VTM2
EXAMPLE_MOVIE = '1c758fe2-fa19-4dc1-a9f6-fcd5eeb0a284'  # Belgica
EXAMPLE_PROGRAM = '96a49148-59f6-420c-9b90-8b058760c467'  # Familie
EXAMPLE_EPISODE = '03136212-d2f5-4c0f-abff-eac84ae8da42'  # Instafamous S01E01


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestRouting(unittest.TestCase):
    """ Tests for Routing """

    def __init__(self, *args, **kwargs):
        super(TestRouting, self).__init__(*args, **kwargs)

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)
        pass

    def tearDown(self):
        xbmc.Player().stop()

    def test_index(self):
        routing.run([routing.url_for(addon.index), '0', ''])

    def test_main_menu(self):
        routing.run([routing.url_for(addon.show_main_menu), '0', ''])

    def test_channels_menu(self):
        routing.run([routing.url_for(addon.show_channels), '0', ''])
        routing.run([routing.url_for(addon.show_channel_menu, channel='vtm'), '0', ''])

    def test_catalog_menu(self):
        routing.run([routing.url_for(addon.show_catalog), '0', ''])
        routing.run([routing.url_for(addon.show_catalog_all), '0', ''])

    def test_catalog_category_menu(self):
        routing.run([routing.url_for(addon.show_catalog_category, category='films'), '0', ''])

    def test_catalog_channel_menu(self):
        routing.run([routing.url_for(addon.show_catalog_channel, channel='vtm'), '0', ''])

    def test_catalog_program_menu(self):
        routing.run([routing.url_for(addon.show_catalog_program, program=EXAMPLE_PROGRAM), '0', ''])

    def test_catalog_program_season_menu(self):
        routing.run([routing.url_for(addon.show_catalog_program_season, program=EXAMPLE_PROGRAM, season=-1), '0', ''])

    def test_catalog_recommendations_menu(self):
        routing.run([routing.url_for(addon.show_recommendations, storefront=STOREFRONT_MAIN), '0', ''])
        routing.run([routing.url_for(addon.show_recommendations_category, storefront=STOREFRONT_MAIN, category='21'), '0', ''])  # Populair op VTM GO

    def test_catalog_mylist_menu(self):
        routing.run([routing.url_for(addon.show_mylist), '0', ''])

    def test_catalog_continuewatching_menu(self):
        routing.run([routing.url_for(addon.show_continuewatching), '0', ''])

    def test_search_menu(self):
        routing.run([routing.url_for(addon.show_search), '0', ''])
        routing.run([routing.url_for(addon.show_search, query='nieuws'), '0', ''])
        routing.run([routing.url_for(addon.show_search, query='Loïc'), '0', ''])

    def test_tvguide_menu(self):
        routing.run([routing.url_for(addon.show_tvguide_channel, channel='vtm'), '0', ''])
        routing.run([routing.url_for(addon.show_tvguide_detail, channel='vtm', date='today'), '0', ''])

    def test_play_livetv(self):
        routing.run([routing.url_for(addon.play, category='channels', item=EXAMPLE_CHANNEL + '?.pvr'), '0', ''])

    def test_play_movie(self):
        old_setting = kodiutils.get_setting('manifest_proxy')

        kodiutils.set_setting('manifest_proxy', 'true')
        routing.run([routing.url_for(addon.play, category='movies', item=EXAMPLE_MOVIE), '0', ''])

        kodiutils.set_setting('manifest_proxy', 'false')
        routing.run([routing.url_for(addon.play, category='movies', item=EXAMPLE_MOVIE), '0', ''])

        kodiutils.set_setting('manifest_proxy', old_setting)

    def test_play_episode(self):
        routing.run([routing.url_for(addon.play, category='episodes', item=EXAMPLE_EPISODE), '0', ''])

    def test_play_epg(self):
        import datetime
        # Play yesterdays news of 13:00
        timestamp = (datetime.datetime.now() - datetime.timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0)
        routing.run([routing.url_for(addon.play_epg_datetime, channel='vtm', timestamp=timestamp.isoformat()), '0', ''])

    def test_library(self):
        routing.run([routing.url_for(addon.library_movies), '0', ''])
        routing.run([routing.url_for(addon.library_movies), '0', 'movie=' + EXAMPLE_MOVIE + '&kodi_action=check_exists'])
        routing.run([routing.url_for(addon.library_movies), '0', 'movie=' + EXAMPLE_MOVIE + '&kodi_action=refresh_info'])
        routing.run([routing.url_for(addon.library_movies), '0', 'movie=' + EXAMPLE_MOVIE])
        routing.run([routing.url_for(addon.library_tvshows), '0', ''])
        routing.run([routing.url_for(addon.library_tvshows), '0', 'program=' + EXAMPLE_PROGRAM])
        routing.run([routing.url_for(addon.library_tvshows), '0', 'program=' + EXAMPLE_PROGRAM + '&kodi_action=check_exists'])
        routing.run([routing.url_for(addon.library_tvshows), '0', 'program=' + EXAMPLE_PROGRAM + '&kodi_action=refresh_info'])
        routing.run([routing.url_for(addon.library_tvshows), '0', 'episode=' + EXAMPLE_EPISODE])
        routing.run([routing.url_for(addon.library_configure), '0', ''])
        routing.run([routing.url_for(addon.library_clean), '0', ''])
        routing.run([routing.url_for(addon.library_update), '0', ''])


if __name__ == '__main__':
    unittest.main()
