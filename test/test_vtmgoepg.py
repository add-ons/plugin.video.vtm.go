# -*- coding: utf-8 -*-

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import vtmgoepg
from resources.lib.kodilogging import getLogger

logger = getLogger('TestVtmGoEpg')


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

    def test_get_epg(self):
        # Get list of EPG for today
        epg = self._vtmgoepg.get_epg()
        self.assertTrue(epg)

        # Take first broadcast of vtm
        # TODO: extend test to keep trying next episodes until we have one with a playableUuid
        first = epg['vtm'].broadcasts[0]

        # Fetch details
        details = self._vtmgoepg.get_details(channel='vtm', program_type=first.playable_type, epg_id=first.uuid)
        self.assertTrue(details)
        print(details)


if __name__ == '__main__':
    unittest.main()
