# -*- coding: utf-8 -*-
""" Menu code related to channels """

from __future__ import absolute_import, division, unicode_literals

from resources.lib.kodiwrapper import TitleItem
from resources.lib.modules.menu import Menu
from resources.lib.vtmgo.vtmgo import VtmGo


class Channels:
    """ Menu code related to channels """

    def __init__(self, kodi):
        """ Initialise object """
        self._kodi = kodi
        self._vtm_go = VtmGo(self._kodi)
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
