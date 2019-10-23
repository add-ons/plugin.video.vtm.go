# -*- coding: utf-8 -*-
""" Menu code related to main menu """

from __future__ import absolute_import, division, unicode_literals

from resources.lib.kodiwrapper import TitleItem
from resources.lib.menu import Menu


class MenuMain(Menu):
    """ Menu code related to main menu """

    def show_mainmenu(self):
        """ Show the main menu """
        kids = self._kodi.kids_mode()

        listing = []
        listing.extend([
            TitleItem(title=self._kodi.localize(30001),  # A-Z
                      path=self._kodi.url_for('show_catalog_category', kids=kids, category='all'),
                      art_dict=dict(
                          icon='DefaultMovieTitle.png'
                      ),
                      info_dict=dict(
                          plot=self._kodi.localize(30002),
                      )),
            TitleItem(title=self._kodi.localize(30003),  # Catalogue
                      path=self._kodi.url_for('show_catalog', kids=kids),
                      art_dict=dict(
                          icon='DefaultGenre.png'
                      ),
                      info_dict=dict(
                          plot=self._kodi.localize(30004),
                      )),
            TitleItem(title=self._kodi.localize(30005),  # Live TV
                      path=self._kodi.url_for('show_livetv', kids=kids),
                      art_dict=dict(
                          icon='DefaultAddonPVRClient.png'
                      ),
                      info_dict=dict(
                          plot=self._kodi.localize(30006),
                      )),
            TitleItem(title=self._kodi.localize(30013),  # TV Guide
                      path=self._kodi.url_for('show_tvguide', kids=kids),
                      art_dict={
                          'icon': 'DefaultAddonTvInfo.png'
                      },
                      info_dict={
                          'plot': self._kodi.localize(30014),
                      }),
            TitleItem(title=self._kodi.localize(30015),  # Recommendations
                      path=self._kodi.url_for('show_recommendations', kids=kids),
                      art_dict={
                          'icon': 'DefaultFavourites.png'
                      },
                      info_dict={
                          'plot': self._kodi.localize(30016),
                      }),
            TitleItem(title=self._kodi.localize(30017),  # My List
                      path=self._kodi.url_for('show_mylist', kids=kids),
                      art_dict={
                          'icon': 'DefaultPlaylist.png'
                      },
                      info_dict={
                          'plot': self._kodi.localize(30018),
                      }),
            # TitleItem(title=self._kodi.localize(30019),  # Continue watching
            #           path=routing.url_for(show_continuewatching, kids=kids),
            #           art_dict={
            #               'icon': 'DefaultInProgressShows.png'
            #           },
            #           info_dict={
            #               'plot': self._kodi.localize(30020),
            #           }),
        ])

        # Only provide YouTube option when plugin.video.youtube is available
        if self._kodi.get_cond_visibility('System.HasAddon(plugin.video.youtube)') != 0:
            listing.append(
                TitleItem(title=self._kodi.localize(30007),  # YouTube
                          path=self._kodi.url_for('show_youtube', kids=kids),
                          art_dict=dict(
                              icon='DefaultTags.png'
                          ),
                          info_dict=dict(
                              plot=self._kodi.localize(30008),
                          ))
            )

        listing.extend([
            TitleItem(title=self._kodi.localize(30009),  # Search
                      path=self._kodi.url_for('show_search', kids=kids),
                      art_dict=dict(
                          icon='DefaultAddonsSearch.png'
                      ),
                      info_dict=dict(
                          plot=self._kodi.localize(30010),
                      )),
        ])

        if not kids:
            listing.append(
                TitleItem(title=self._kodi.localize(30011),  # Kids Zone
                          path=self._kodi.url_for('show_index', kids=True),
                          art_dict=dict(
                              icon='DefaultUser.png'
                          ),
                          info_dict=dict(
                              plot=self._kodi.localize(30012),
                          ))
            )

        self._kodi.show_listing(listing)
