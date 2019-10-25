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

    def update(self):
        """ Update the metadata with a foreground progress indicator """
        # Create progress indicator
        progress = self._kodi.show_progress(message=self._kodi.localize(30715))

        def update_status(i, total):
            """ Update the progress indicator """
            progress.update(int(((i + 1) / total) * 100), self._kodi.localize(30716, index=i + 1, total=total))
            return progress.iscanceled()

        self.fetch_metadata(callback=update_status)

        # Close progress indicator
        progress.close()

    def fetch_metadata(self, callback=None):
        """ Fetch the metadata for all the items in the catalog """
        # Fetch all items from the catalog
        items = self.vtm_go.get_items('all')
        count = len(items)

        # Loop over all of them and download the metadata
        for index, item in enumerate(items):
            if isinstance(item, Movie):
                if not self.vtm_go.get_movie(item.movie_id, only_cache=True):
                    self.vtm_go.get_movie(item.movie_id)
            elif isinstance(item, Program):
                if not self.vtm_go.get_program(item.program_id, only_cache=True):
                    self.vtm_go.get_program(item.program_id)

            # Update the progress indicator
            if callback and callback(index, count):
                # Stop when callback returns False
                return False

        return True

    def clean(self):
        """ Clear metadata (called from settings) """
        self._kodi.invalidate_cache()
        self._kodi.set_setting('metadata_last_updated', '0')
        self._kodi.show_ok_dialog(message=self._kodi.localize(30714))  # Local metadata is cleared.
