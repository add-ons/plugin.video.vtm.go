# -*- coding: utf-8 -*-
""" Player module """

from __future__ import absolute_import, division, unicode_literals

from resources.lib.kodiwrapper import TitleItem
from resources.lib.vtmgo.vtmgo import VtmGo, UnavailableException
from resources.lib.vtmgo.vtmgostream import VtmGoStream, StreamGeoblockedException, StreamUnavailableException


class Player:
    """ Code responsible for playing media """

    def __init__(self, kodi):
        """ Initialise object
        :type kodi: KodiWrapper
        """
        self._kodi = kodi
        self._vtm_go = VtmGo(self._kodi)
        self._vtm_go_stream = VtmGoStream(self._kodi)

    def play(self, category, item):
        """ Play the requested item.
        :type category: string
        :type item: string
        """
        # Check if inputstreamhelper is correctly installed
        try:
            from inputstreamhelper import Helper
            is_helper = Helper('mpd', drm='com.widevine.alpha')
            if not is_helper.check_inputstream():
                # inputstreamhelper has already shown an error
                return

        except ImportError:
            self._kodi.show_ok_dialog(message=self._kodi.localize(30708))  # Please reboot Kodi
            return

        try:
            # Get stream information
            resolved_stream = self._vtm_go_stream.get_stream(category, item)

        except StreamGeoblockedException:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30709), message=self._kodi.localize(30710))  # This video is geo-blocked...
            self._kodi.end_of_directory()
            return

        except StreamUnavailableException:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30712))  # The video is unavailable...
            self._kodi.end_of_directory()
            return

        info_dict = {
            'tvshowtitle': resolved_stream.program,
            'title': resolved_stream.title,
            'duration': resolved_stream.duration,
        }

        prop_dict = {}

        stream_dict = {
            'duration': resolved_stream.duration,
        }

        # Lookup metadata
        try:
            if category in ['movies', 'oneoffs']:
                info_dict.update({'mediatype': 'movie'})

                # Get details
                details = VtmGo(self._kodi).get_movie(item)
                info_dict.update({
                    'plot': details.description,
                    'year': details.year,
                    'aired': details.aired,
                })

            elif category == 'episodes':
                info_dict.update({'mediatype': 'episode'})

                # Get details
                details = VtmGo(self._kodi).get_episode(item)
                info_dict.update({
                    'plot': details.description,
                    'season': details.season,
                    'episode': details.number,
                })

            elif category == 'channels':
                info_dict.update({'mediatype': 'episode'})

                # For live channels, we need to keep on updating the manifest
                # This might not be needed, and could be done with the Location-tag updates if inputstream.adaptive supports it
                # See https://github.com/peak3d/inputstream.adaptive/pull/298#issuecomment-524206935
                prop_dict.update({
                    'inputstream.adaptive.manifest_update_parameter': 'full',
                })

            else:
                raise Exception('Unknown category %s' % category)

        except UnavailableException:
            # We continue without details.
            # This seems to make it possible to play some programs what don't have metadata.
            pass

        # Play this item
        self._kodi.play(
            TitleItem(
                title=resolved_stream.title,
                path=resolved_stream.url,
                subtitles_path=resolved_stream.subtitles,
                art_dict={},
                info_dict=info_dict,
                prop_dict=prop_dict,
                stream_dict=stream_dict,
                is_playable=True,
            ),
            license_key=self._vtm_go_stream.create_license_key(resolved_stream.license_url))
