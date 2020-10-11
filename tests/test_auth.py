# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib.kodiwrapper import KodiWrapper
from resources.lib.vtmgo import vtmgo, vtmgoauth

kodi = KodiWrapper()


class TestAuth(unittest.TestCase):
    """ Tests for VTM GO Auth """

    def __init__(self, *args, **kwargs):
        super(TestAuth, self).__init__(*args, **kwargs)

        self._vtmgoauth = vtmgoauth.VtmGoAuth(kodi)
        self._vtmgo = vtmgo.VtmGo(kodi)

    @unittest.skipUnless(kodi.has_credentials(), 'Skipping since we have no credentials.')
    def test_login(self):
        token = self._vtmgoauth.get_token()
        self.assertTrue(token)

    @unittest.skipUnless(kodi.has_credentials(), 'Skipping since we have no credentials.')
    def test_get_profiles(self):
        profiles = self._vtmgo.get_profiles()
        self.assertTrue(profiles)


if __name__ == '__main__':
    unittest.main()
