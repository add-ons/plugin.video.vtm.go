# -*- coding: utf-8 -*-
""" Tests for VTM GO EPG API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import xbmc

from resources.lib import addon
from resources.lib import kodiutils
from resources.lib.vtmgo import vtmgoepg

routing = addon.routing


class TestEpg(unittest.TestCase):
    """ Tests for VTM GO EPG API """

    @classmethod
    def setUpClass(cls):
        cls._vtmgoepg = vtmgoepg.VtmGoEpg()

    def tearDown(self):
        xbmc.Player().stop()

    def test_get_broadcast(self):
        import datetime
        import dateutil

        timestamp = datetime.datetime.now(dateutil.tz.tzlocal()).replace(hour=12, minute=0, second=0)
        broadcast = self._vtmgoepg.get_broadcast('vtm', timestamp.isoformat())
        self.assertTrue(broadcast)

    @unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
    def test_get_epg(self):
        from datetime import date

        # Get list of EPG for today
        epg = self._vtmgoepg.get_epg(channel='vtm3')
        self.assertTrue(epg)

        epg = self._vtmgoepg.get_epg(channel='vtm', date=date.today().strftime('%Y-%m-%d'))
        self.assertTrue(epg)

        # Get list of EPG for tomorrow
        epg_tomorrow = self._vtmgoepg.get_epg(channel='vtm', date='tomorrow')
        self.assertTrue(epg_tomorrow)

        # Get list of EPG for yesterday
        epg_yesterday = self._vtmgoepg.get_epg(channel='vtm', date='yesterday')
        self.assertTrue(epg_yesterday)

        # Get list of EPG for today
        epg_today = self._vtmgoepg.get_epg(channel='vtm4', date='today')
        self.assertTrue(epg_today)

        # combined_broadcasts = epg_today.broadcasts + epg_tomorrow.broadcasts + epg_yesterday.broadcasts

        # broadcast = next(b for b in combined_broadcasts if b.playable_type == 'episodes')
        # if broadcast:
        #     addon.run([routing.url_for(addon.show_catalog_program, program=broadcast.program_uuid), '0', ''])

        # broadcast = next(b for b in combined_broadcasts if b.playable_type == 'movies')
        # if broadcast:
        #     addon.run(
        #         [routing.url_for(addon.play, category=broadcast.playable_type, item=broadcast.playable_uuid), '0', ''])


if __name__ == '__main__':
    unittest.main()
