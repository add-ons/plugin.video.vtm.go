# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from resources.lib import kodiutils
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth


class TestAuth(unittest.TestCase):
    """ Tests for VTM GO Auth """

    def test_authorization(self):
        auth = VtmGoAuth(kodiutils.get_tokens_path())
        auth_info = auth.authorize()
        self.assertIsInstance(auth_info, dict)
        self.assertIsNotNone(auth_info.get('user_code'))
        self.assertIsNotNone(auth_info.get('device_code'))
        self.assertIsNotNone(auth_info.get('interval'))
        self.assertIsNotNone(auth_info.get('verification_uri'))
        self.assertIsNotNone(auth_info.get('expires_in'))

    def test_login(self):
        auth = VtmGoAuth(kodiutils.get_tokens_path())
        tokens = auth.get_tokens()
        self.assertTrue(tokens.is_valid_token())


if __name__ == '__main__':
    unittest.main()
