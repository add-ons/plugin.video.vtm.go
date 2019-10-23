# -*- coding: utf-8 -*-
""" Metadata """

from __future__ import absolute_import, division, unicode_literals

from resources.lib.vtmgo.vtmgo import VtmGo, Movie, Program


class Metadata:
    """ Code responsible for the refreshing of the metadata """

    def __init__(self, _kodi):
        """ Initialise object """
        self._kodi = _kodi
        self.vtm_go = VtmGo(self._kodi)

    def update(self, delay=10):
        """ Update the metadata for the listings (called from settings) """
        import xbmc

        progress = self._kodi.show_progress(message=self._kodi.localize(30715))

        # Fetch all items from the catalog
        items = self.vtm_go.get_items('all')
        count = len(items)

        # Loop over all of them and download the metadata
        for index, item in enumerate(items):
            # Update the items
            if isinstance(item, Movie):
                if not self.vtm_go.get_movie(item.movie_id, only_cache=True):
                    self.vtm_go.get_movie(item.movie_id)
                    xbmc.sleep(delay)
            elif isinstance(item, Program):
                if not self.vtm_go.get_program(item.program_id, only_cache=True):
                    self.vtm_go.get_program(item.program_id)
                    xbmc.sleep(delay)

            # Upgrade the progress bar
            progress.update(int(((index + 1) / count) * 100), self._kodi.localize(30716, index=index + 1, total=count))

            # Allow to cancel this operation
            if progress.iscanceled():
                break

        # Close the progress dialog
        progress.close()

        # Update last updated
        from time import time
        self._kodi.set_setting('metadata_last_updated', str(int(time())))

    def clean(self):
        """ Clear metadata (called from settings) """
        self._kodi.invalidate_cache()
        self._kodi.show_ok_dialog(message=self._kodi.localize(30714))  # Local metadata is cleared.
