# -*- coding: utf-8 -*-
""" Search module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib.kodiutils import KodiUtils
from resources.lib.modules.menu import Menu
from resources.lib.vtmgo.vtmgo import VtmGo

_LOGGER = logging.getLogger('search')


class Search:
    """ Menu code related to search """

    def __init__(self, router):
        """ Initialise object """
        self._router = router  # type: callable
        self._vtm_go = VtmGo()
        self._menu = Menu(router)

    def show_search(self, query=None):
        """ Shows the search dialog
        :type query: str
        """
        if not query:
            # Ask for query
            query = KodiUtils.get_search_string(heading=KodiUtils.localize(30009))  # Search VTM GO
            if not query:
                KodiUtils.end_of_directory()
                return

        # Do search
        try:
            items = self._vtm_go.do_search(query)
        except Exception as ex:  # pylint: disable=broad-except
            KodiUtils.notification(message=str(ex))
            KodiUtils.end_of_directory()
            return

        # Display results
        listing = []
        for item in items:
            listing.append(self._menu.generate_titleitem(item))

        # Sort like we get our results back.
        KodiUtils.show_listing(listing, 30009, content='tvshows')
