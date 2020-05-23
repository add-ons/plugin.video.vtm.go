# -*- coding: utf-8 -*-
""" Background service code """

from __future__ import absolute_import, division, unicode_literals

import logging
from time import time

from xbmc import Monitor

from resources.lib import kodilogging
from resources.lib.kodiwrapper import KodiWrapper
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth

kodilogging.config()
_LOGGER = logging.getLogger('service')


class BackgroundService(Monitor):
    """ Background service code """

    def __init__(self):
        Monitor.__init__(self)
        self._kodi = KodiWrapper()
        self.vtm_go = VtmGo(self._kodi)
        self.vtm_go_auth = VtmGoAuth(self._kodi)
        self.update_interval = 24 * 3600  # Every 24 hours
        self.cache_expiry = 30 * 24 * 3600  # One month

    def run(self):
        """ Background loop for maintenance tasks """
        _LOGGER.debug('Service started')

        while not self.abortRequested():
            # Update every `update_interval` after the last update
            if self._kodi.get_setting_as_bool('metadata_update') and int(self._kodi.get_setting('metadata_last_updated', 0)) + self.update_interval < time():
                self._update_metadata()

            # Stop when abort requested
            if self.waitForAbort(10):
                break

        _LOGGER.debug('Service stopped')

    def onSettingsChanged(self):  # pylint: disable=invalid-name
        """ Callback when a setting has changed """
        # Refresh our VtmGo instance
        self.vtm_go = VtmGo(self._kodi)

        if self.vtm_go_auth.has_credentials_changed():
            _LOGGER.debug('Clearing auth tokens due to changed credentials')
            self.vtm_go_auth.clear_token()

            # Refresh container
            self._kodi.container_refresh()

    def _update_metadata(self):
        """ Update the metadata for the listings """
        from resources.lib.modules.metadata import Metadata

        # Clear outdated metadata
        self._kodi.invalidate_cache(self.cache_expiry)

        def update_status(_i, _total):
            """ Allow to cancel the background job """
            return self.abortRequested() or not self._kodi.get_setting_as_bool('metadata_update')

        success = Metadata(self._kodi).fetch_metadata(callback=update_status)

        # Update metadata_last_updated
        if success:
            self._kodi.set_setting('metadata_last_updated', str(int(time())))


def run():
    """ Run the BackgroundService """
    BackgroundService().run()
