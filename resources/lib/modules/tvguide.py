# -*- coding: utf-8 -*-
""" Menu code related to channels """

from __future__ import absolute_import, division, unicode_literals

from resources.lib.kodiwrapper import TitleItem
from resources.lib.vtmgo.vtmgo import UnavailableException
from resources.lib.vtmgo.vtmgoepg import VtmGoEpg


class TvGuide:
    """ Menu code related to the TV Guide """

    EPG_NO_BROADCAST = 'Geen Uitzending'

    def __init__(self, kodi):
        """ Initialise object
        :type kodi: resources.lib.kodiwrapper.KodiWrapper
        """
        self._kodi = kodi
        self._vtm_go_epg = VtmGoEpg(self._kodi)

    def show_tvguide_channel(self, channel):
        """ Shows the dates in the tv guide
        :type channel: str
        """
        listing = []
        for day in self._vtm_go_epg.get_dates('%A %d %B %Y'):
            if day.get('highlight'):
                title = '[B]{title}[/B]'.format(title=day.get('title'))
            else:
                title = day.get('title')

            listing.append(
                TitleItem(title=title,
                          path=self._kodi.url_for('show_tvguide_detail', channel=channel, date=day.get('key')),
                          art_dict={
                              'icon': 'DefaultYear.png',
                              'thumb': 'DefaultYear.png',
                          },
                          info_dict={
                              'plot': None,
                              'date': day.get('date'),
                          })
            )

        self._kodi.show_listing(listing, 30013, content='files', sort=['date'])

    def show_tvguide_detail(self, channel=None, date=None):
        """ Shows the programs of a specific date in the tv guide
        :type channel: str
        :type date: str
        """
        try:
            epg = self._vtm_go_epg.get_epg(channel=channel, date=date)
        except UnavailableException as ex:
            self._kodi.show_notification(message=str(ex))
            self._kodi.end_of_directory()
            return

        listing = []
        for broadcast in epg.broadcasts:
            if broadcast.playable_type == 'episodes':
                context_menu = [(
                    self._kodi.localize(30102),  # Go to Program
                    'XBMC.Container.Update(%s)' %
                    self._kodi.url_for('show_program_from_epg', channel=channel, program=broadcast.uuid)
                )]
            else:
                context_menu = None

            title = '{time} - {title}{live}'.format(
                time=broadcast.time.strftime('%H:%M'),
                title=broadcast.title,
                live=' [I](LIVE)[/I]' if broadcast.live else ''
            )

            if broadcast.airing:
                title = '[B]{title}[/B]'.format(title=title)

            if broadcast.title == self.EPG_NO_BROADCAST:
                title = '[COLOR gray]' + title + '[/COLOR]'

            listing.append(
                TitleItem(title=title,
                          path=self._kodi.url_for('play_epg_program', channel=channel, program_type=broadcast.playable_type, epg_id=broadcast.uuid,
                                                  airing=epg.uuid if broadcast.airing else None),
                          art_dict={
                              'icon': broadcast.image,
                              'thumb': broadcast.image,
                          },
                          info_dict={
                              'title': title,
                              'plot': broadcast.description,
                              'duration': broadcast.duration,
                              'mediatype': 'video',
                          },
                          stream_dict={
                              'duration': broadcast.duration,
                              'codec': 'h264',
                              'height': 1080,
                              'width': 1920,
                          },
                          context_menu=context_menu,
                          is_playable=True)
            )

        self._kodi.show_listing(listing, 30013, content='episodes', sort=['unsorted'])

    def show_program_from_epg(self, channel, program):
        """ Show a program based on the channel and information from the EPG
        :type channel: str
        :type program: str
        """
        details = self._vtm_go_epg.get_details(channel=channel, program_type='episodes', epg_id=program)
        if not details:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30713))  # The requested video was not found in the guide.
            self._kodi.end_of_directory()
            return

        # Show the program with our freshly obtained program_uuid
        self._kodi.redirect(
            self._kodi.url_for('show_catalog_program', program=details.program_uuid).replace('plugin://plugin.video.vtm.go', ''))

    def play_epg_datetime(self, channel, timestamp):
        """ Play a program based on the channel and the timestamp when it was aired
        :type channel: str
        :type timestamp: str
        """
        broadcast = self._vtm_go_epg.get_broadcast(channel, timestamp)
        if not broadcast:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30713))  # The requested video was not found in the guide.
            self._kodi.end_of_directory()
            return

        self.play_epg_program(channel, broadcast.playable_type, broadcast.uuid)

    def play_epg_program(self, channel, program_type, epg_id, airing=None):
        """ Play a program based on the channel and information from the EPG
        :type channel: str
        :type program_type: str
        :type epg_id: str
        :type airing: str
        """
        if airing:
            res = self._kodi.show_context_menu([self._kodi.localize(30103), self._kodi.localize(30105)])  # Watch Live | Play from Catalog
            if res == -1:  # user has cancelled
                return
            if res == 0:  # user selected "Watch Live"
                self._kodi.redirect(
                    self._kodi.url_for('play', category='channels', item=airing))
                return

        details = self._vtm_go_epg.get_details(channel=channel, program_type=program_type, epg_id=epg_id)
        if not details:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30713))  # The requested video was not found in the guide.
            self._kodi.end_of_directory()
            return

        # Play this program
        self._kodi.redirect(
            self._kodi.url_for('play', category=details.playable_type, item=details.playable_uuid))
