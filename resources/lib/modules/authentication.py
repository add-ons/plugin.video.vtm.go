# -*- coding: utf-8 -*-
""" Profile module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib import kodiutils
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth

_LOGGER = logging.getLogger(__name__)


class Authentication:
    """ Code responsible for the Authentication """

    def __init__(self):
        """ Initialise object """
        self._auth = VtmGoAuth(kodiutils.get_tokens_path())

    def login(self):
        """ Start the authorisation flow. """
        # Start the authorization
        auth_info = self._auth.authorize()

        # Check the authorization until it succeeds or the user cancels.
        while True:
            result = kodiutils.yesno_dialog(
                message="Go to {url} and enter [B]{code}[/B] to login on this device.".format(
                    url=auth_info.get('verification_uri'),
                    code=auth_info.get('user_code')),
                yeslabel="Yes Refresh",
                nolabel="No Cancel"
            )

            if not result:
                # User has cancelled
                return

            # Check if we are authorized now
            check = self._auth.authorize_check()
            if check:
                kodiutils.redirect(kodiutils.url_for('show_main_menu'))

    def clear_tokens(self):
        """ Clear the authentication tokens """
        self._auth.logout()
        kodiutils.notification(message=kodiutils.localize(30706))
