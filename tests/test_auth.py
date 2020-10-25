# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import kodiutils
from resources.lib.vtmgo import vtmgoauth


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestAuth(unittest.TestCase):
    """ Tests for VTM GO Auth """

    @classmethod
    def setUpClass(cls):
        cls._vtmgoauth = vtmgoauth.VtmGoAuth(kodiutils.get_setting('username'),
                                             kodiutils.get_setting('password'),
                                             'VTM',
                                             kodiutils.get_setting('profile'),
                                             kodiutils.get_tokens_path())

    def test_login(self):
        token = self._vtmgoauth.login()
        self.assertTrue(token)

    def test_get_profiles(self):
        profiles = self._vtmgoauth.get_profiles()
        self.assertTrue(profiles)


if __name__ == '__main__':
    unittest.main()
