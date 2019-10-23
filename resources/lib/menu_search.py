# -*- coding: utf-8 -*-
""" Menu code related to search """

from __future__ import absolute_import, division, unicode_literals

from resources.lib.menu import Menu


class MenuSearch(Menu):
    """ Menu code related to search """

    def show_search(self, query=None):
        """ Shows the search dialog """
        if not query:
            # Ask for query
            query = self._kodi.get_search_string(heading=self._kodi.localize(30009))
            if not query:
                self._kodi.end_of_directory()
                return

        # Do search
        try:
            items = self.vtm_go.do_search(query)
        except Exception as ex:  # pylint: disable=broad-except
            self._kodi.show_notification(message=str(ex))
            self._kodi.end_of_directory()
            return

        # Display results
        listing = []
        for item in items:
            listing.append(self._generate_titleitem(item))

        # Sort like we get our results back.
        self._kodi.show_listing(listing, 30009, content='tvshows')
