# -*- coding: utf-8 -*-
""" Background service code """

from __future__ import absolute_import, division, unicode_literals

import hashlib
import logging
from time import time

from xbmc import Monitor

from resources.lib import kodilogging, kodiutils
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth

kodilogging.config()
_LOGGER = logging.getLogger('service')


class BackgroundService(Monitor):
    """ Background service code """

    def __init__(self):
        Monitor.__init__(self)
        self.vtm_go_auth = VtmGoAuth()
        self.update_interval = 24 * 3600  # Every 24 hours
        self.cache_expiry = 30 * 24 * 3600  # One month

    def run(self):
        """ Background loop for maintenance tasks """
        _LOGGER.info('Service started')

        while not self.abortRequested():
            # Update every `update_interval` after the last update
            if kodiutils.get_setting_bool('metadata_update') and int(kodiutils.get_setting('metadata_last_updated', 0)) + self.update_interval < time():
                self._update_metadata()

            # Stop when abort requested
            if self.waitForAbort(10):
                break

        _LOGGER.info('Service stopped')

    def onSettingsChanged(self):  # pylint: disable=invalid-name
        """ Callback when a setting has changed """
        # Refresh our VtmGo instance
        if self._has_credentials_changed():
            _LOGGER.info('Clearing auth tokens due to changed credentials')
            VtmGoAuth.clear_tokens()

            # Refresh container
            kodiutils.container_refresh()

    @staticmethod
    def _has_credentials_changed():
        """ Check if credentials have changed """
        old_hash = kodiutils.get_setting('credentials_hash')
        new_hash = ''
        if VtmGoAuth.has_credentials():
            new_hash = hashlib.md5((kodiutils.get_setting('username') + kodiutils.get_setting('password')).encode('utf-8')).hexdigest()
        if new_hash != old_hash:
            kodiutils.set_setting('credentials_hash', new_hash)
            return True
        return False

    def _update_metadata(self):
        """ Update the metadata for the listings """
        from resources.lib.modules.metadata import Metadata

        # Clear outdated metadata
        kodiutils.invalidate_cache(self.cache_expiry)

        def update_status(_i, _total):
            """ Allow to cancel the background job """
            return self.abortRequested() or not kodiutils.get_setting_bool('metadata_update')

        success = Metadata().fetch_metadata(callback=update_status)

        # Update metadata_last_updated
        if success:
            kodiutils.set_setting('metadata_last_updated', str(int(time())))


def run():
    """ Run the BackgroundService """
    BackgroundService().run()
