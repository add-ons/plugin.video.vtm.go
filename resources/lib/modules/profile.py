# -*- coding: utf-8 -*-
""" Profile module """

from __future__ import absolute_import, division, unicode_literals

from resources.lib.vtmgo.vtmgo import VtmGo


class Profile:
    """ Code responsible for the refreshing of the metadata """

    def __init__(self, kodi):
        """ Initialise object """
        self._kodi = kodi
        self._vtm_go = VtmGo(self._kodi)

    def select_profile(self):
        """ Show your profiles """
        profiles = self._vtm_go.get_profiles()

        index = self._kodi.show_context_menu([x.name for x in profiles])
        if index == -1:  # user has cancelled
            return
        profile = profiles[index]

        self._kodi.log('Setting profile to %s' % profile)
        self._kodi.set_setting('profile', profile.key)
        self._kodi.set_setting('profile_name', profile.name)
        self._kodi.set_setting('product', profile.product)

        # Return to the main menu
        self._kodi.redirect('')
