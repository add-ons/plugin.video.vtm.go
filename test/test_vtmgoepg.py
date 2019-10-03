# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import warnings

from urllib3.exceptions import InsecureRequestWarning

from resources.lib import vtmgoepg, kodilogging

logger = kodilogging.get_logger('TestVtmGoEpg')


class TestVtmGoEpg(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestVtmGoEpg, self).__init__(*args, **kwargs)
        self._vtmgoepg = vtmgoepg.VtmGoEpg()

        # Enable debug logging for urllib
        # try:
        #     import http.client as http_client
        # except ImportError:
        #     # Python 2
        #     import httplib as http_client
        # http_client.HTTPConnection.debuglevel = 1
        #
        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        warnings.simplefilter("ignore", ResourceWarning)

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
