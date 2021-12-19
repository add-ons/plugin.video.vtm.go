# -*- coding: utf-8 -*-
""" Tests for VTM GO EPG API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import xbmc

from resources.lib import addon
from resources.lib.modules import CHANNELS
from resources.lib.vtmgo import vtmgoepg

routing = addon.routing


class TestEpg(unittest.TestCase):
    """ Tests for VTM GO EPG API """

    @classmethod
    def setUpClass(cls):
        cls.epg = vtmgoepg.VtmGoEpg()

    def tearDown(self):
        xbmc.Player().stop()

    def test_get_broadcast(self):
        import datetime

        import dateutil

        timestamp = datetime.datetime.now(dateutil.tz.tzlocal()).replace(hour=12, minute=0, second=0)
        broadcast = self.epg.get_broadcast('vtm', timestamp.isoformat())
        self.assertTrue(broadcast)

    def test_get_epg(self):
        from datetime import date

        # Test EPG for all channels
        for _, channel in CHANNELS.items():
            if not channel.get('epg'):
                continue

            epg = self.epg.get_epg(channel=channel.get('epg'))
            self.assertTrue(epg)

        # This channel doesn't exist
        with self.assertRaises(Exception):
            self.epg.get_epg(channel='caz')

        # Get list of EPG by date
        epg = self.epg.get_epg(channel='vtm', date=date.today().strftime('%Y-%m-%d'))
        self.assertTrue(epg)

        # Get list of EPG for tomorrow
        epg_tomorrow = self.epg.get_epg(channel='vtm', date='tomorrow')
        self.assertTrue(epg_tomorrow)

        # Get list of EPG for yesterday
        epg_yesterday = self.epg.get_epg(channel='vtm', date='yesterday')
        self.assertTrue(epg_yesterday)

        broadcast = next(b for b in epg_yesterday.broadcasts if b.playable_type == 'episodes' and b.title == 'VTM NIEUWS')
        routing.run([routing.url_for(addon.show_catalog_program, program=broadcast.program_uuid), '0', ''])
        routing.run([routing.url_for(addon.play, category=broadcast.playable_type, item=broadcast.playable_uuid), '0', ''])


if __name__ == '__main__':
    unittest.main()
