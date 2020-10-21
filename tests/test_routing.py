# -*- coding: utf-8 -*-
""" Tests for Routing """

# pylint: disable=invalid-name,missing-docstring,no-self-use

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import xbmc

from resources.lib import kodiutils
from resources.lib import addon

routing = addon.routing


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

    def test_main_menu(self):
        routing.run([routing.url_for(addon.show_main_menu), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_channels_menu(self):
        addon.run([routing.url_for(addon.show_channels), '0', ''])
        addon.run([routing.url_for(addon.show_channel_menu, channel='vtm'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog_menu(self):
        addon.run([routing.url_for(addon.show_catalog), '0', ''])
        addon.run([routing.url_for(addon.show_catalog_all), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog_category_menu(self):
        addon.run([routing.url_for(addon.show_catalog_category, category='films'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog_channel_menu(self):
        addon.run([routing.url_for(addon.show_catalog_channel, channel='vtm'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog_program_menu(self):
        addon.run([routing.url_for(addon.show_catalog_program, program='96a49148-59f6-420c-9b90-8b058760c467'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog_program_season_menu(self):
        addon.run([routing.url_for(addon.show_catalog_program_season, program='96a49148-59f6-420c-9b90-8b058760c467', season=-1), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog_recommendations_menu(self):
        addon.run([routing.url_for(addon.show_recommendations), '0', ''])
        addon.run([routing.url_for(addon.show_recommendations_category, category='775de6ef-003d-4571-8a6e-8433be0ef379'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog_mylist_menu(self):
        addon.run([routing.url_for(addon.show_mylist), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_catalog_continuewatching_menu(self):
        addon.run([routing.url_for(addon.show_continuewatching), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_search_menu(self):
        addon.run([routing.url_for(addon.show_search), '0', ''])
        addon.run([routing.url_for(addon.show_search, query='nieuws'), '0', ''])
        addon.run([routing.url_for(addon.show_search, query='Loïc'), '0', ''])

    def test_tvguide_menu(self):
        addon.run([routing.url_for(addon.show_tvguide_channel, channel='vtm'), '0', ''])
        addon.run([routing.url_for(addon.show_tvguide_detail, channel='vtm', date='today'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_play_livetv(self):
        addon.run([routing.url_for(addon.play, category='channels', item='ea826456-6b19-4612-8969-864d1c818347?.pvr'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_play_movie(self):
        addon.run([routing.url_for(addon.play, category='movies', item='d1850498-941d-48cc-a558-37aaf37f4525'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_play_episode(self):
        addon.run([routing.url_for(addon.play, category='episodes', item='03136212-d2f5-4c0f-abff-eac84ae8da42'), '0', ''])

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_play_epg(self):
        import datetime
        timestamp = datetime.datetime.now().replace(hour=6, minute=0, second=0)
        addon.run([routing.url_for(addon.play_epg_datetime, channel='vtm', timestamp=timestamp.isoformat()), '0', ''])


if __name__ == '__main__':
    unittest.main()
