# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import random
import string
import unittest

from resources.lib import kodiutils
from resources.lib.vtmgo import Profile
from resources.lib.vtmgo.exceptions import NoLoginException, InvalidLoginException
from resources.lib.vtmgo.vtmgoauth import AccountStorage, VtmGoAuth


@unittest.skipUnless(kodiutils.get_setting('username') and kodiutils.get_setting('password'), 'Skipping since we have no credentials.')
class TestAuth(unittest.TestCase):
    """ Tests for VTM GO Auth """

    def test_login(self):
        auth = VtmGoAuth(kodiutils.get_setting('username'),
                         kodiutils.get_setting('password'),
                         'VTM',
                         kodiutils.get_setting('profile'),
                         kodiutils.get_tokens_path())

        account = auth.get_tokens()
        self.assertIsInstance(account, AccountStorage)
        self.assertIsNotNone(account.jwt_token)

        profiles = auth.get_profiles()
        self.assertIsInstance(profiles[0], Profile)

    def test_errors(self):
        with self.assertRaises(NoLoginException):
            VtmGoAuth(None, None, None, None, token_path=kodiutils.get_tokens_path())

        with self.assertRaises(InvalidLoginException):
            VtmGoAuth(self._random_email(), 'test', 'VTM', None, token_path=kodiutils.get_tokens_path())

    @staticmethod
    def _random_email(domain='gmail.com'):
        """ Generate a random e-mail address. """
        return '%s@%s' % (''.join(random.choice(string.ascii_letters) for i in range(12)), domain)


if __name__ == '__main__':
    unittest.main()
