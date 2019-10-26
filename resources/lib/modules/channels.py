# -*- coding: utf-8 -*-
""" Menu code related to channels """

from __future__ import absolute_import, division, unicode_literals

from collections import OrderedDict

from resources.lib.kodiwrapper import TitleItem
from resources.lib.modules.menu import Menu
from resources.lib.vtmgo.vtmgo import VtmGo

# key   = id used in the VTM GO API
# label = Label to show in the UI
# logo  = File in resources/logos/
# eog   = id used in the EPG API
CHANNELS = OrderedDict([
    ('vtm', dict(
        label='VTM',
        logo='vtm',
        epg='vtm',
        kids=False,
        youtube=[
            dict(
                # VTM: https://www.youtube.com/user/VTMvideo
                label='VTM',
                logo='vtm',
                path='plugin://plugin.video.youtube/user/VTMvideo/',
            ),
            dict(
                # VTM Nieuws: https://www.youtube.com/channel/UCm1v16r82bhI5jwur14dK9w
                label='VTM Nieuws',
                logo='vtm',
                path='plugin://plugin.video.youtube/channel/UCm1v16r82bhI5jwur14dK9w/',
            ),
            dict(
                # VTM Koken: https://www.youtube.com/user/VTMKOKENvideokanaal
                label='VTM Koken',
                logo='vtm',
                path='plugin://plugin.video.youtube/user/VTMKOKENvideokanaal/',
            ),
        ]
    )),
    ('q2', dict(
        label='Q2',
        logo='q2',
        epg='q2',
        kids=False,
        youtube=[
            dict(
                # Q2: https://www.youtube.com/user/2BEvideokanaal
                label='Q2',
                logo='q2',
                path='plugin://plugin.video.youtube/user/2BEvideokanaal/',
            ),
        ]
    )),
    ('vitaya', dict(
        label='Vitaya',
        logo='vitaya',
        epg='vitaya',
        kids=False,
        youtube=[
            dict(
                # Vitaya: https://www.youtube.com/user/VITAYAvideokanaal
                label='Vitaya',
                logo='vitaya',
                path='plugin://plugin.video.youtube/user/VITAYAvideokanaal/',
            ),
        ]
    )),
    ('caz', dict(
        label='CAZ',
        logo='caz',
        epg='caz',
        stream='caz',
        kids=False,
    )),
    ('vtmkids', dict(
        label='VTM KIDS',
        logo='vtmkids',
        epg='vtm-kids',
        kids=True,
        youtube=[
            dict(
                # VTM KIDS: https://www.youtube.com/channel/UCJgZKD2qpa7mY2BtIgpNR2Q
                label='VTM KIDS',
                logo='vtmkids',
                path='plugin://plugin.video.youtube/channel/UCJgZKD2qpa7mY2BtIgpNR2Q/',
            ),
        ]
    )),
    ('vtmkidsjr', dict(
        label='VTM KIDS Jr',
        logo='vtmkidsjr',
        epg='vtm-kids-jr',
        kids=True,
    )),
    ('qmusic', dict(
        label='QMusic',
        logo='qmusic',
        epg='qmusic',
        kids=False,
        youtube=[
            dict(
                # Q-Music: https://www.youtube.com/user/qmusic
                label='QMusic',
                logo='qmusic',
                path='plugin://plugin.video.youtube/user/qmusic/',
            ),
        ]
    )),
])


class Channels:
    """ Menu code related to channels """

    def __init__(self, kodi):
        """ Initialise object """
        self._kodi = kodi
        self._vtm_go = VtmGo(self._kodi)
        self._menu = Menu(self._kodi)

    def show_channels(self):
        """ Shows TV channels """
        kids = self._kodi.kids_mode()

        # Fetch EPG from API
        channel_infos = self._vtm_go.get_live_channels()

        listing = []
        for i, key in enumerate(CHANNELS):  # pylint: disable=unused-variable
            channel = CHANNELS[key]

            if kids and channel.get('kids') is False:
                continue

            channel_info = [cval for (ckey, cval) in enumerate(channel_infos) if cval.key == key][0]

            # Lookup the high resolution logo based on the channel name
            icon = '{path}/resources/logos/{logo}-white.png'.format(path=self._kodi.get_addon_path(), logo=channel.get('logo'))
            fanart = '{path}/resources/logos/{logo}.png'.format(path=self._kodi.get_addon_path(), logo=channel.get('logo'))

            context_menu = [(
                self._kodi.localize(30103),  # Watch live
                'XBMC.PlayMedia(%s)' %
                self._kodi.url_for('play', category='channels', item=channel_info.channel_id)
            ), (
                self._kodi.localize(30104),  # TV Guide
                'XBMC.Container.Update(%s)' %
                self._kodi.url_for('show_tvguide_channel', channel=channel.get('epg'))
            )]

            title = channel.get('label')
            if channel_info and channel_info.epg:
                title += '[COLOR gray] | {title}[/COLOR]'.format(title=channel_info.epg[0].title)

            listing.append(
                TitleItem(title=title,
                          path=self._kodi.url_for('show_channel_menu', channel=key),
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
                          context_menu=context_menu),
            )

        self._kodi.show_listing(listing, 30007)

    def show_channel_menu(self, key):
        """ Shows a TV channel """
        channel = CHANNELS[key]

        # Fetch EPG from API
        channel_info = self._vtm_go.get_live_channel(key)

        title = self._kodi.localize(30052, channel=channel.get('label'))
        if channel_info.epg:
            title += '[COLOR gray] | {title}[/COLOR]'.format(title=channel_info.epg[0].title)

        # Lookup the high resolution logo based on the channel name
        icon = '{path}/resources/logos/{logo}-white.png'.format(path=self._kodi.get_addon_path(), logo=channel.get('logo'))
        fanart = '{path}/resources/logos/{logo}.png'.format(path=self._kodi.get_addon_path(), logo=channel.get('logo'))

        listing = [
            TitleItem(title=title,
                      path=self._kodi.url_for('play', category='channels', item=channel_info.channel_id) + '?.pvr',
                      art_dict={
                          'icon': icon,
                          'thumb': icon,
                          'fanart': fanart,
                      },
                      info_dict={
                          'plot': self._menu.format_plot(channel_info),
                          'playcount': 0,
                          'mediatype': 'video',
                      },
                      stream_dict={
                          'codec': 'h264',
                          'height': 1080,
                          'width': 1920,
                      },
                      is_playable=True),
            TitleItem(title=self._kodi.localize(30053, channel=channel.get('label')),
                      path=self._kodi.url_for('show_tvguide_channel', channel=channel.get('epg')),
                      art_dict={
                          'icon': 'DefaultAddonTvInfo.png'
                      },
                      info_dict={
                          'plot': self._kodi.localize(30054, channel=channel.get('label')),
                      }),
        ]

        # Add YouTube channels
        if self._kodi.get_cond_visibility('System.HasAddon(plugin.video.youtube)') != 0:
            for youtube in channel.get('youtube', []):
                listing.append(
                    TitleItem(title='[B]{channel}[/B] on YouTube'.format(channel=youtube.get('label')),
                              path=youtube.get('path'),
                              info_dict={
                                  'plot': self._kodi.localize(30206, label=youtube.get('label')),
                              })
                )

        self._kodi.show_listing(listing, 30007)
