# -*- coding: utf-8 -*-
""" Metadata """

from __future__ import absolute_import, division, unicode_literals

from resources.lib import GeoblockedException, UnavailableException
from resources.lib.kodiwrapper import TitleItem
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoepg import VtmGoEpg
from resources.lib.vtmgo.vtmgostream import VtmGoStream


class Player:
    """ Code responsible for playing something """

    def __init__(self, _kodi):
        """ Initialise object """
        self._kodi = _kodi
        self.vtm_go = VtmGo(self._kodi)

    def play_datetime(self, channel, timestamp):
        """ Play a program based on the channel and the timestamp when it was aired. """
        _vtmGoEpg = VtmGoEpg(self._kodi)
        broadcast = _vtmGoEpg.get_broadcast(channel, timestamp)
        if not broadcast:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30713))  # The requested video was not found in the guide.
            return

        self.play_epg(channel, broadcast.playable_type, broadcast.uuid)

    def play_epg(self, channel, program_type, epg_id):
        """ Play a program based on the channel and information from the EPG. """
        _vtmGoEpg = VtmGoEpg(self._kodi)
        details = _vtmGoEpg.get_details(channel=channel, program_type=program_type, epg_id=epg_id)
        if not details:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30713))  # The requested video was not found in the guide.
            return

        self.play(details.playable_type, details.playable_uuid)

    def play(self, category, item):
        """ Play the requested item. Uses setResolvedUrl(). """
        _vtmgostream = VtmGoStream(self._kodi)

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
            resolved_stream = _vtmgostream.get_stream(category, item)

        except GeoblockedException:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30709), message=self._kodi.localize(30710))  # Geo-blocked
            return

        except UnavailableException:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30711), message=self._kodi.localize(30712))  # Unavailable
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
            if category == 'movies':
                info_dict.update({'mediatype': 'movie'})

                # Get details
                details = VtmGo(self._kodi).get_movie(item)
                info_dict.update({
                    'plot': details.description,
                    'year': details.year,
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
                info_dict.update({'mediatype': 'video'})

                # For live channels, we need to keep on updating the manifest
                # This might not be needed, and could be done with the Location-tag updates if inputstream.adaptive supports it
                # See https://github.com/peak3d/inputstream.adaptive/pull/298#issuecomment-524206935
                prop_dict.update({
                    'inputstream.adaptive.manifest_update_parameter': 'full',
                })

            else:
                raise Exception('Unknown category %s' % category)

        except GeoblockedException:
            self._kodi.show_ok_dialog(heading=self._kodi.localize(30709), message=self._kodi.localize(30710))  # Geo-blocked
            return

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
            license_key=_vtmgostream.create_license_key(resolved_stream.license_url))
