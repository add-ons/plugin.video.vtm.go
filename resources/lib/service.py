# -*- coding: utf-8 -*-
""" Background service code """

from __future__ import absolute_import, division, unicode_literals

from time import time

from resources.lib.kodiwrapper import KodiWrapper, LOG_INFO, LOG_DEBUG
from resources.lib.vtmgo.vtmgo import VtmGo
from xbmc import Monitor


class BackgroundService(Monitor):
    """ Background service code """

    def __init__(self):
        Monitor.__init__(self)
        self.kodi = KodiWrapper()
        self.vtm_go = VtmGo(self.kodi)
        self.update_interval = 24 * 3600  # Every 24 hours
        self.cache_expiry = 30 * 24 * 3600  # One month

    def run(self):
        """ Background loop for maintenance tasks """
        self.kodi.log('Service started', LOG_INFO)

        while not self.abortRequested():
            # Update every `update_interval` after the last update
            if self.kodi.get_setting_as_bool('metadata_update') and int(self.kodi.get_setting('metadata_last_updated', 0)) + self.update_interval < time():
                self._update_metadata()

            # Stop when abort requested
            if self.waitForAbort(10):
                break

        self.kodi.log('Service stopped', LOG_INFO)

    def onSettingsChanged(self):
        """ Callback when a setting has changed """
        self.kodi.log('IN VTM GO: Settings changed', LOG_DEBUG)

        # Refresh our VtmGo instance
        self.vtm_go = VtmGo(self.kodi)

    def _update_metadata(self):
        """ Update the metadata for the listings. """
        from resources.lib.modules.metadata import Metadata

        # Clear outdated metadata
        self.kodi.invalidate_cache(self.cache_expiry)

        # Create progress indicator
        progress = self.kodi.show_progress_background(message=self.kodi.localize(30715))
        self.kodi.log('Updating metadata in the background')

        def update_status(i, total):
            progress.update(int(((i + 1) / total) * 100))
            return self.abortRequested() or not self.kodi.get_setting_as_bool('metadata_update')

        success = Metadata(self.kodi).fetch_metadata(callback=update_status)

        # Close progress indicator
        progress.close()

        # Update metadata_last_updated
        if success:
            self.kodi.set_setting('metadata_last_updated', str(int(time())))


def run():
    """ Run the BackgroundService """
    BackgroundService().run()
