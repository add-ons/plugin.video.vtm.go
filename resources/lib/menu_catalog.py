# -*- coding: utf-8 -*-
""" Menu code related to the catalog """

from __future__ import absolute_import, division, unicode_literals

from resources.lib import UnavailableException
from resources.lib.kodiwrapper import TitleItem
from resources.lib.menu import Menu


class MenuCatalog(Menu):
    """ Menu code related to the catalog """

    def show_catalog(self):
        """ Show the catalog """
        try:
            categories = self.vtm_go.get_categories()
        except Exception as ex:
            self._kodi.show_notification(message=str(ex))
            raise

        listing = []
        for cat in categories:
            listing.append(
                TitleItem(title=cat.title,
                          path=self._kodi.url_for('show_catalog_category', kids=self._kodi.kids_mode(), category=cat.category_id),
                          info_dict={
                              'plot': '[B]{category}[/B]'.format(category=cat.title),
                          })
            )

        # Sort categories by default like in VTM GO.
        self._kodi.show_listing(listing, 30003, content='files')

    def show_catalog_category(self, category):
        """ Show a category in the catalog """
        try:
            items = self.vtm_go.get_items(category)
        except Exception as ex:
            self._kodi.show_notification(message=str(ex))
            raise

        listing = []
        for item in items:
            listing.append(self._generate_titleitem(item))

        # Sort items by label, but don't put folders at the top.
        # Used for A-Z listing or when movies and episodes are mixed.
        self._kodi.show_listing(listing, 30003, content='movies' if category == 'films' else 'tvshows', sort='label')

    def show_program(self, program):
        """ Show a program from the catalog """
        try:
            program_obj = self.vtm_go.get_program(program)
        except UnavailableException:
            self._kodi.show_notification(message=self._kodi.localize(30717))  # This program is not available in the VTM GO catalogue.
            self._kodi.end_of_directory()
            return

        listing = []

        # Add an '* All seasons' entry when configured in Kodi
        if self._kodi.get_global_setting('videolibrary.showallitems') is True:
            listing.append(
                TitleItem(title='* %s' % self._kodi.localize(30204),  # * All seasons
                          path=self._kodi.url_for('show_program_season', program=program, season='all'),
                          art_dict={
                              'thumb': program_obj.cover,
                              'fanart': program_obj.cover,
                          },
                          info_dict={
                              'tvshowtitle': program_obj.name,
                              'title': self._kodi.localize(30204),  # All seasons
                              'tagline': program_obj.description,
                              'set': program_obj.name,
                              'mpaa': ', '.join(program_obj.legal) if hasattr(program_obj, 'legal') and program_obj.legal else self._kodi.localize(30216),
                          })
            )

        # Add the seasons
        for s in program_obj.seasons.values():
            listing.append(
                TitleItem(title=self._kodi.localize(30205, season=s.number),  # Season X
                          path=self._kodi.url_for('show_program_season', program=program, season=s.number),
                          art_dict={
                              'thumb': s.cover,
                              'fanart': program_obj.cover,
                          },
                          info_dict={
                              'tvshowtitle': program_obj.name,
                              'title': self._kodi.localize(30205, season=s.number),
                              'tagline': program_obj.description,
                              'set': program_obj.name,
                              'mpaa': ', '.join(program_obj.legal) if hasattr(program_obj, 'legal') and program_obj.legal else self._kodi.localize(30216),
                          })
            )

        # Sort by label. Some programs return seasons unordered.
        self._kodi.show_listing(listing, 30003, content='tvshows', sort='label')

    def show_program_season(self, program, season):
        """ Show a program from the catalog """
        try:
            program_obj = self.vtm_go.get_program(program)
        except UnavailableException:
            self._kodi.show_notification(message=self._kodi.localize(30717))  # This program is not available in the VTM GO catalogue.
            self._kodi.end_of_directory()
            return

        if season == 'all':
            # Show all seasons
            seasons = program_obj.seasons.values()
        else:
            # Show the season that was selected
            seasons = [program_obj.seasons[int(season)]]

        listing = []
        for s in seasons:
            for episode in s.episodes.values():
                listing.append(self._generate_titleitem(episode))

        # Sort by episode number by default. Takes seasons into account.
        self._kodi.show_listing(listing, 30003, content='episodes', sort='episode')

    def show_recommendations(self):
        """ Show the recommendations """
        try:
            recommendations = self.vtm_go.get_recommendations()
        except Exception as ex:
            self._kodi.show_notification(message=str(ex))
            raise

        listing = []
        for cat in recommendations:
            listing.append(
                TitleItem(title=cat.title,
                          path=self._kodi.url_for('show_recommendations_category', kids=self._kodi.kids_mode(), category=cat.category_id),
                          info_dict={
                              'plot': '[B]{category}[/B]'.format(category=cat.title),
                          })
            )

        # Sort categories by default like in VTM GO.
        self._kodi.show_listing(listing, 30015, content='files')

    def show_recommendations_category(self, category):
        """ Show the items in a recommendations category """
        try:
            recommendations = self.vtm_go.get_recommendations()
        except Exception as ex:
            self._kodi.show_notification(message=str(ex))
            raise

        listing = []
        for cat in recommendations:
            # Only show the requested category
            if cat.category_id != category:
                continue

            for item in cat.content:
                listing.append(self._generate_titleitem(item))

        # Sort categories by default like in VTM GO.
        self._kodi.show_listing(listing, 30015, content='tvshows')

    def show_mylist(self):
        """ Show the items in "My List" """
        try:
            mylist = self.vtm_go.get_swimlane('my-list')
        except Exception as ex:
            self._kodi.show_notification(message=str(ex))
            raise

        listing = []
        for item in mylist:
            item.my_list = True
            listing.append(self._generate_titleitem(item))

        # Sort categories by default like in VTM GO.
        self._kodi.show_listing(listing, 30017, content='tvshows')

    def show_continuewatching(self):
        """ Show the items in "Continue Watching" """
        try:
            mylist = self.vtm_go.get_swimlane('continue-watching')
        except Exception as ex:
            self._kodi.show_notification(message=str(ex))
            raise

        listing = []
        for item in mylist:
            titleitem = self._generate_titleitem(item, progress=True)

            # Add Program Name to title since this list contains episodes from multiple programs
            title = '%s - %s' % (titleitem.info_dict.get('tvshowtitle'), titleitem.info_dict.get('title'))
            titleitem.title = title
            titleitem.info_dict['title'] = title

            listing.append(titleitem)

        # Sort categories by default like in VTM GO.
        self._kodi.show_listing(listing, 30019, content='episodes', sort='label')
