# -*- coding: utf-8 -*-
""" Background service code """

from __future__ import absolute_import, division, unicode_literals

import logging
from time import time

from xbmc import getInfoLabel, Monitor, Player

from resources.lib import kodilogging
from resources.lib.kodiwrapper import KodiWrapper, to_unicode
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth
from resources.lib.vtmgo.vtmgostream import VtmGoStream

kodilogging.config()
_LOGGER = logging.getLogger('service')


class BackgroundService(Monitor):
    """ Background service code """

    def __init__(self):
        Monitor.__init__(self)
        self._kodi = KodiWrapper()
        self._player = PlayerMonitor(kodi=self._kodi)
        self.vtm_go = VtmGo(self._kodi)
        self.vtm_go_auth = VtmGoAuth(self._kodi)
        self.update_interval = 24 * 3600  # Every 24 hours
        self.cache_expiry = 30 * 24 * 3600  # One month

    def run(self):
        """ Background loop for maintenance tasks """
        _LOGGER.debug('Service started')

        while not self.abortRequested():
            # Update every `update_interval` after the last update
            if self._kodi.get_setting_as_bool('metadata_update') and int(self._kodi.get_setting('metadata_last_updated', 0)) + self.update_interval < time():
                self._update_metadata()

            # Stop when abort requested
            if self.waitForAbort(10):
                break

        _LOGGER.debug('Service stopped')

    def onSettingsChanged(self):  # pylint: disable=invalid-name
        """ Callback when a setting has changed """
        # Refresh our VtmGo instance
        self.vtm_go = VtmGo(self._kodi)

        if self.vtm_go_auth.has_credentials_changed():
            _LOGGER.debug('Clearing auth tokens due to changed credentials')
            self.vtm_go_auth.clear_token()

            # Refresh container
            self._kodi.container_refresh()

    def _update_metadata(self):
        """ Update the metadata for the listings """
        from resources.lib.modules.metadata import Metadata

        # Clear outdated metadata
        self._kodi.invalidate_cache(self.cache_expiry)

        def update_status(_i, _total):
            """ Allow to cancel the background job """
            return self.abortRequested() or not self._kodi.get_setting_as_bool('metadata_update')

        success = Metadata(self._kodi).fetch_metadata(callback=update_status)

        # Update metadata_last_updated
        if success:
            self._kodi.set_setting('metadata_last_updated', str(int(time())))

class PlayerMonitor(Player):
    """ A custom Player object to check subtitles """

    def __init__(self, kodi=None):
        """ Initialises a custom Player object
        :type kodi: resources.lib.kodiwrapper.KodiWrapper
        """
        self._kodi = kodi
        self.__listen = False
        self.__av_started = False
        self.__path = None
        self.__subtitle_path = None
        Player.__init__(self)

    def onPlayBackStarted(self):  # pylint: disable=invalid-name
        """ Will be called when Kodi player starts """
        self.__path = getInfoLabel('Player.FilenameAndPath')
        if not self.__path.startswith('plugin://plugin.video.vtm.go/'):
            self.__listen = False
            return
        self.__listen = True
        _LOGGER.debug('Player: [onPlayBackStarted] called')
        self.__subtitle_path = None
        self.__av_started = False

    def onAVStarted(self):  # pylint: disable=invalid-name
        """ Will be called when Kodi has a video or audiostream """
        if not self.__listen:
            return
        _LOGGER.debug('Player: [onAVStarted] called')
        self.__subtitle_path = self.__get_subtitle_path()
        self.__av_started = True
        self.__check_subtitles()

    def onAVChange(self):  # pylint: disable=invalid-name
        """ Will be called when Kodi has a video, audio or subtitle stream. Also happens when the stream changes """
        if not self.__listen:
            return
        _LOGGER.debug('Player: [onAVChange] called')
        self.__check_subtitles()

    def __check_subtitles(self):
        """ Check subtitles """

        # Check if subtitles are enabled before making any changes
        response = self._kodi.jsonrpc(method='Player.GetProperties', params=dict(playerid=1, properties=['currentsubtitle', 'subtitleenabled', 'subtitles']))
        subtitle_enabled = response.get('result').get('subtitleenabled')

        # Make sure an internal InputStream Adaptive subtitle is selected, if available
        available_subtitles = self.getAvailableSubtitleStreams()
        if available_subtitles:
            for i, subtitle in enumerate(available_subtitles):
                if '(External)' not in subtitle and '(External)' in self.getSubtitles():
                    self.setSubtitleStream(i)
                    break
        elif self.__av_started:
            _LOGGER.debug('Player: No internal subtitles found')

            # Add external subtitles
            if self.__subtitle_path:
                _LOGGER.debug('Player: Adding external subtitles %s', self.__subtitle_path)
                self.setSubtitles(self.__subtitle_path)

        # Enable subtitles if needed
        show_subtitles = self._kodi.get_setting_as_bool('showsubtitles')
        if show_subtitles and not subtitle_enabled:
            _LOGGER.debug('Player: Enabling subtitles')
            self.showSubtitles(True)
        elif not subtitle_enabled:
            _LOGGER.debug('Player: Disabling subtitles')
            self.showSubtitles(False)

    def onPlayBackSeek(self, seekTime, seekOffset):  # pylint: disable=invalid-name, unused-argument
        """ Will be called when user seeks to a time """
        if not self.__listen:
            return
        _LOGGER.debug('Player: [onPlayBackSeek] called')

    def onPlayBackEnded(self):  # pylint: disable=invalid-name
        """ Will be called when [Kodi] stops playing a file """
        if not self.__listen:
            return
        _LOGGER.debug('Player: [onPlayBackEnded] called')
        self.__av_started = False
        self.__subtitle_path = None

    def onPlayBackStopped(self):  # pylint: disable=invalid-name
        """ Will be called when [user] stops Kodi playing a file """
        if not self.__listen:
            return
        _LOGGER.debug('Player: [onPlayBackStopped] called')
        self.__av_started = False
        self.__subtitle_path = None

    def onPlayBackError(self):  # pylint: disable=invalid-name
        """ Will be called when playback stops due to an error. """
        if not self.__listen:
            return
        _LOGGER.debug('Player: [onPlayBackError] called')
        self.__av_started = False
        self.__subtitle_path = None

    def __get_subtitle_path(self):
        """ Get the external subtitles path """
        temp_path = self._kodi.get_userdata_path() + 'temp/'
        files = None
        if self._kodi.check_if_path_exists(temp_path):
            _, files = self._kodi.listdir(temp_path)
        if files and len(files) == 1:
            return temp_path + files[0]
        _LOGGER.debug('Player: No subtitle path')
        return None


    def __send_upnext(self, episode_id, season, episode):
        """ Send a message to Up Next with information about the next Episode.
        :type string: episode_id
        :type season: int
        :type episode: int
        """
        from base64 import b64encode
        from json import dumps

        # Get episode details from episode_id
        program_id = self._vtm_go_stream.get_stream('episodes', episode_id).program_id
        program = self._vtm_go.get_program(program_id)
        episode_details = self._vtm_go.get_episode_from_program(program, episode_id)

        # Lookup the next episode
        next_episode_details = self._vtm_go.get_next_episode_from_program(program, season, episode)

        # Create the info for Up Next
        if next_episode_details:
            upnext_info = self.__generate_upnext(episode_details, next_episode_details)

        data = [to_unicode(b64encode(dumps(upnext_info).encode()))]
        sender = '{addon_id}.SIGNAL'.format(addon_id='plugin.video.vtm.go')
        _LOGGER.debug('Sending Up Next data: %s', upnext_info)
        self._kodi.notify(sender=sender, message='upnext_data', data=data)

    @staticmethod
    def __generate_upnext(current_episode, next_episode):
        """ Construct the data for Up Next.
        :type current_episode: resources.lib.vtmgo.vtmgo.Episode
        :type next_episode: resources.lib.vtmgo.vtmgo.Episode
        """
        upnext_info = dict(
            current_episode=dict(
                episodeid=current_episode.episode_id,
                tvshowid=current_episode.program_id,
                title=current_episode.name,
                art={
                    'thumb': current_episode.cover,
                },
                season=current_episode.season,
                episode=current_episode.number,
                showtitle=current_episode.program_name,
                plot=current_episode.description,
                playcount=None,
                rating=None,
                firstaired=current_episode.aired[:10] if current_episode.aired else '',
                runtime=current_episode.duration,
            ),
            next_episode=dict(
                episodeid=next_episode.episode_id,
                tvshowid=next_episode.program_id,
                title=next_episode.name,
                art={
                    'thumb': next_episode.cover,
                },
                season=next_episode.season,
                episode=next_episode.number,
                showtitle=next_episode.program_name,
                plot=next_episode.description,
                playcount=None,
                rating=None,
                firstaired=next_episode.aired[:10] if next_episode.aired else '',
                runtime=next_episode.duration,
            ),
            play_url='plugin://plugin.video.vtm.go/play/catalog/episodes/%s' % next_episode.episode_id,
        )

        return upnext_info

def run():
    """ Run the BackgroundService """
    BackgroundService().run()
