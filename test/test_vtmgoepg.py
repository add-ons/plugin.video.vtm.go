# -*- coding: utf-8 -*-
""" Tests for VTM GO EPG API """
# pylint: disable=missing-function-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import warnings

from urllib3.exceptions import InsecureRequestWarning

from resources.lib.kodiwrapper import KodiWrapper
from resources.lib.vtmgo import vtmgoepg

kodi = KodiWrapper()


class TestVtmGoEpg(unittest.TestCase):
    """ Tests for VTM GO EPG API """

    def __init__(self, *args, **kwargs):
        super(TestVtmGoEpg, self).__init__(*args, **kwargs)

        self._vtmgoepg = vtmgoepg.VtmGoEpg(kodi)

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)

        # Don't warn that we are not verifying the certificates of VTM GO API.
        warnings.simplefilter("ignore", InsecureRequestWarning)

    def test_get_epg(self):
        from datetime import date

        # Get list of EPG for today
        epg = self._vtmgoepg.get_epg(channel='vtm', date='today')
        self.assertTrue(epg)

        # Get list of EPG for tomorrow
        epg = self._vtmgoepg.get_epg(channel='vtm', date='tomorrow')
        self.assertTrue(epg)

        # Get list of EPG for yesterday
        epg = self._vtmgoepg.get_epg(channel='vtm', date='yesterday')
        self.assertTrue(epg)

        # Get list of EPG for yesterday
        today = date.today().strftime('%Y-%m-%d')
        epg = self._vtmgoepg.get_epg(channel='vtm', date=today)
        self.assertTrue(epg)

        # Take first broadcast of vtm channel
        first = epg.broadcasts[0]

        # Fetch details
        details = self._vtmgoepg.get_details(channel='vtm', program_type=first.playable_type, epg_id=first.uuid)
        self.assertTrue(details)


if __name__ == '__main__':
    unittest.main()
