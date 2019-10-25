# -*- coding: utf-8 -*-
""" Menu code related to channels """

from __future__ import absolute_import, division, unicode_literals

from resources.lib import UnavailableException
from resources.lib.kodiwrapper import TitleItem
from resources.lib.modules.menu import Menu
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoepg import VtmGoEpg


class Channels:
    """ Menu code related to channels """

    def __init__(self, kodi):
        """ Initialise object """
        self._kodi = kodi
        self._vtm_go = VtmGo(self._kodi)
        self._vtm_go_epg = VtmGoEpg(self._kodi)
        self._menu = Menu(self._kodi)

    def show_livetv(self):
        """ Shows Live TV channels """
        try:
            channels = self._vtm_go.get_live_channels()
        except Exception as ex:
            self._kodi.show_notification(message=str(ex))
            raise

        from resources.lib import CHANNEL_MAPPING

        listing = []
        for channel in channels:
            if CHANNEL_MAPPING.get(channel.name):
                # Lookup the high resolution logo based on the channel name
                icon = '{path}/resources/logos/{logo}-white.png'.format(path=self._kodi.get_addon_path(), logo=CHANNEL_MAPPING.get(channel.name))
                fanart = '{path}/resources/logos/{logo}.png'.format(path=self._kodi.get_addon_path(), logo=CHANNEL_MAPPING.get(channel.name))
            else:
                # Fallback to the default (lower resolution) logo
                icon = channel.logo
                fanart = channel.logo

            title = channel.name
            if channel.epg:
                title += '[COLOR gray] | {title}[/COLOR]'.format(title=channel.epg[0].title)

            listing.append(
                TitleItem(title=title,
                          path=self._kodi.url_for('play', category='channels', item=channel.channel_id) + '?.pvr',
                          art_dict={
                              'icon': icon,
                              'thumb': icon,
                              'fanart': fanart,
                          },
                          info_dict={
                              'plot': self._menu.format_plot(channel),
                              'playcount': 0,
                              'mediatype': 'video',
                          },
                          stream_dict={
                              'codec': 'h264',
                              'height': 1080,
                              'width': 1920,
                          },
                          is_playable=True),
            )

        self._kodi.show_listing(listing, 30005)

    def show_tvguide(self):
        """ Shows the TV guide """
        kids = self._kodi.kids_mode()

        from resources.lib import CHANNELS

        listing = []
        for entry in CHANNELS:
            # Skip non-kids channels when we are in kids mode.
            if kids and entry.get('kids') is False:
                continue

            # Lookup the high resolution logo based on the channel name
            icon = '{path}/resources/logos/{logo}-white.png'.format(path=self._kodi.get_addon_path(), logo=entry.get('logo'))
            fanart = '{path}/resources/logos/{logo}.png'.format(path=self._kodi.get_addon_path(), logo=entry.get('logo'))

            listing.append(
                TitleItem(title=entry.get('label'),
                          path=self._kodi.url_for('show_tvguide_channel', channel=entry.get('key')),
                          art_dict={
                              'icon': icon,
                              'thumb': icon,
                              'fanart': fanart,
                          },
                          info_dict={
                              'plot': self._kodi.localize(30215, channel=entry.get('label')),
                          })
            )

        self._kodi.show_listing(listing, 30013)

    def show_tvguide_channel(self, channel):
        """ Shows the dates in the tv guide """
        listing = []
        for day in self._vtm_go_epg.get_dates('%A %d %B %Y'):
            if day.get('highlight'):
                title = '[B]{title}[/B]'.format(title=day.get('title'))
            else:
                title = day.get('title')

            listing.append(
                TitleItem(title=title,
                          path=self._kodi.url_for('show_tvguide_detail', channel=channel, date=day.get('date')),
                          art_dict={
                              'icon': 'DefaultYear.png',
                              'thumb': 'DefaultYear.png',
                          },
                          info_dict={
                              'plot': None,
                          })
            )

        self._kodi.show_listing(listing, 30013, content='files')

    def show_tvguide_detail(self, channel=None, date=None):
        """ Shows the programs of a specific date in the tv guide """
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
                    self._kodi.localize(30052),  # Go to Program
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

            if broadcast.title != 'Geen Uitzending':
                path = self._kodi.url_for('play_epg', channel=channel, program_type=broadcast.playable_type, epg_id=broadcast.uuid)
                is_playable = True
            else:
                path = None
                is_playable = False
                title = '[COLOR gray]' + title + '[/COLOR]'

            listing.append(
                TitleItem(title=title,
                          path=path,
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
                          is_playable=is_playable)
            )

        self._kodi.show_listing(listing, 30013, content='episodes')

    def show_program_from_epg(self, channel, program):
        """ Show a program based on the channel and information from the EPG. """
        details = self._vtm_go_epg.get_details(channel=channel, program_type='episodes', epg_id=program)
        if not details:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30713))  # The requested video was not found in the guide.
            return

        # Show the program with our freshly obtained program_uuid
        self._kodi.routing.redirect(
            self._kodi.url_for('show_catalog_program', program=details.program_uuid).replace('plugin://plugin.video.vtm.go', ''))

    def play_datetime(self, channel, timestamp):
        """ Play a program based on the channel and the timestamp when it was aired. """
        broadcast = self._vtm_go_epg.get_broadcast(channel, timestamp)
        if not broadcast:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30713))  # The requested video was not found in the guide.
            return

        self.play_epg(channel, broadcast.playable_type, broadcast.uuid)

    def play_epg(self, channel, program_type, epg_id):
        """ Play a program based on the channel and information from the EPG. """
        details = self._vtm_go_epg.get_details(channel=channel, program_type=program_type, epg_id=epg_id)
        if not details:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30713))  # The requested video was not found in the guide.
            return

        # Play this program
        self._kodi.routing.redirect(
            self._kodi.url_for('play', category=details.playable_type, item=details.playable_uuid).replace('plugin://plugin.video.vtm.go', ''))
