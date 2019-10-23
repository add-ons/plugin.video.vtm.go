# -*- coding: utf-8 -*-
""" Background service code """

from __future__ import absolute_import, division, unicode_literals

from time import time

from resources.lib.kodiwrapper import KodiWrapper, LOG_INFO, LOG_DEBUG
from resources.lib.vtmgo.vtmgo import VtmGo, Program, Movie
from xbmc import Monitor


class BackgroundService(Monitor):
    """ Background service code """

    def __init__(self):
        Monitor.__init__(self)
        self.kodi = KodiWrapper()
        self.vtm_go = VtmGo(self.kodi)
        self.update_interval = 24 * 3600  # Every 24 hours

    def run(self):
        """ Background loop for maintenance tasks """
        self.kodi.log('Service started', LOG_INFO)

        while not self.abortRequested():
            # Update every `update_interval` after the last update
            if self.kodi.get_setting_as_bool('metadata_update') \
                    and int(self.kodi.get_setting('metadata_last_updated', 0)) + self.update_interval < time():
                self._update_metadata()
                self.kodi.set_setting('metadata_last_updated', str(int(time())))

            # Stop when abort requested
            if self.waitForAbort(10):
                break

        self.kodi.log('Service stopped', LOG_INFO)

    def onSettingsChanged(self):
        """ Callback when a setting has changed """
        self.kodi.log('IN VTM GO: Settings changed', LOG_DEBUG)

        # Refresh our VtmGo instance
        self.vtm_go = VtmGo(self.kodi)

    def _update_metadata(self, delay=10):
        """ Update the metadata for the listings. """
        self.kodi.log('Updating metadata in the background')

        # Clear outdated metadata
        self.kodi.invalidate_cache(30 * 24 * 3600)  # one month

        vtm_go = self.vtm_go

        progress = self.kodi.show_progress_background(message=self.kodi.localize(30715))

        # Fetch all items from the catalog
        items = vtm_go.get_items('all')
        count = len(items)

        # Loop over all of them and download the metadata
        for index, item in enumerate(items):
            # Update the items
            if isinstance(item, Movie):
                if not vtm_go.get_movie(item.movie_id, only_cache=True):
                    vtm_go.get_movie(item.movie_id)
                    self.waitForAbort(delay / 1000)
            elif isinstance(item, Program):
                if not vtm_go.get_program(item.program_id, only_cache=True):
                    vtm_go.get_program(item.program_id)
                    self.waitForAbort(delay / 1000)

            # Upgrade the progress bar
            progress.update(int(((index + 1) / count) * 100))

            # Abort when the setting is disabled or kodi is exiting
            if self.abortRequested() or not self.kodi.get_setting_as_bool('metadata_update'):
                break

        # Close the progress dialog
        progress.close()


def run():
    """ Run the BackgroundService """
    BackgroundService().run()
