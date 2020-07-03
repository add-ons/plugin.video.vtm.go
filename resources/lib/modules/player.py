# -*- coding: utf-8 -*-
""" Player module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib.kodiwrapper import TitleItem
from resources.lib.vtmgo.vtmgo import VtmGo, UnavailableException
from resources.lib.vtmgo.vtmgostream import VtmGoStream, StreamGeoblockedException, StreamUnavailableException

_LOGGER = logging.getLogger('player')


class Player:
    """ Code responsible for playing media """

    def __init__(self, kodi):
        """ Initialise object
        :type kodi: resources.lib.kodiwrapper.KodiWrapper
        """
        self._kodi = kodi
        self._vtm_go = VtmGo(self._kodi)
        self._vtm_go_stream = VtmGoStream(self._kodi)

    def play_or_live(self, category, item, channel):
        """ Ask to play the requested item or switch to the live channel
        :type category: str
        :type item: str
        :type channel: str
        """
        res = self._kodi.show_context_menu([self._kodi.localize(30103), self._kodi.localize(30105)])  # Watch Live | Play from Catalog
        if res == -1:  # user has cancelled
            return
        if res == 0:  # user selected "Watch Live"
            # Play live
            self.play('channels', channel)
            return

        # Play this program
        self.play(category, item)

    def play(self, category, item):
        """ Play the requested item.
        :type category: string
        :type item: string
        """
        if not self._check_credentials():
            self._kodi.end_of_directory()
            return

        # Check if inputstreamhelper is correctly installed
        if not self._check_inputstream():
            self._kodi.end_of_directory()
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
                movie_details = self._vtm_go.get_movie(item)
                if movie_details:
                    info_dict.update({
                        'plot': movie_details.description,
                        'year': movie_details.year,
                        'aired': movie_details.aired,
                    })

            elif category == 'episodes':
                info_dict.update({'mediatype': 'episode'})

                # There is no direct API to get episode details, so we go trough the cached program details
                program = self._vtm_go.get_program(resolved_stream.program_id)
                if program:
                    episode_details = self._vtm_go.get_episode_from_program(program, item)
                    if episode_details:
                        info_dict.update({
                            'plot': episode_details.description,
                            'season': episode_details.season,
                            'episode': episode_details.number,
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
                _LOGGER.warning('Unknown category %s', category)

        except UnavailableException:
            # We continue without details.
            # This allows to play some programs that don't have metadata (yet).
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

    def _check_credentials(self):
        """ Check if the user has credentials """
        if self._kodi.has_credentials():
            return True

        # You need to configure your credentials before you can access the content of VTM GO.
        confirm = self._kodi.show_yesno_dialog(message=self._kodi.localize(30701))
        if confirm:
            self._kodi.open_settings()
            if self._kodi.has_credentials():
                return True

        return False

    def _check_inputstream(self):
        """ Check if inputstreamhelper and inputstream.adaptive are fine.
        :rtype boolean
        """
        try:
            from inputstreamhelper import Helper
            is_helper = Helper('mpd', drm='com.widevine.alpha')
            if not is_helper.check_inputstream():
                # inputstreamhelper has already shown an error
                return False

        except ImportError:
            self._kodi.show_ok_dialog(message=self._kodi.localize(30708))  # Please reboot Kodi
            return False

        return True
