# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import json
import random
try:  # Python 3
    from urllib.parse import urlencode, quote
except ImportError:  # Python 2
    from urllib import urlencode, quote

import requests

from resources.lib.kodiutils import localize, proxies, show_ok_dialog
from resources.lib.kodilogging import getLogger

logger = getLogger('VtmGoStream')


class ResolvedStream:
    def __init__(self, program=None, title=None, duration=None, url=None, license_url=None, subtitles=None, cookies=None):
        """
        Object to hold details of a stream that we can play.
        :type program: string
        :type title: string
        :type duration: string
        :type url: string
        :type license_url: string
        :type subtitles: List
        :type cookies: dict
        """
        self.program = program
        self.title = title
        self.duration = duration
        self.url = url
        self.license_url = license_url
        self.subtitles = subtitles
        self.cookies = cookies


class VtmGoStream:
    _VTM_API_KEY = 'zTxhgTEtb055Ihgw3tN158DZ0wbbaVO86lJJulMl'
    _ANVATO_API_KEY = 'HOydnxEYtxXYY1UfT3ADuevMP7xRjPg6XYNrPLhFISL'
    _ANVATO_USER_AGENT = 'ANVSDK Android/5.0.39 (Linux; Android 6.0.1; Nexus 5)'

    def __init__(self):
        self._session = requests.session()

    def get_stream(self, stream_type, stream_id):
        # We begin with asking vtm about the stream info.
        stream_info = self._get_stream_info(stream_type, stream_id)

        # Extract the anvato stream from our stream_info.
        anvato_info = self._extract_anvato_stream_from_stream_info(stream_info)

        # Ask the anvacks to know where we have to send our requests. (I hardcoded this for now)
        # anv_acks = self._anvato_get_anvacks(anvato_info.get('accessKey'))

        # Get the server time. (We don't seem to need this)
        # server_time = self._anvato_get_server_time(anvato_info.get('accessKey'))

        # Send a request for the stream info.
        anvato_stream_info = self._anvato_get_stream_info(anvato_info=anvato_info, stream_info=stream_info)
        if anvato_stream_info is None:
            return None  # No stream available (i.e. geo-blocked)

        # Get published urls.
        url = anvato_stream_info['published_urls'][0]['embed_url']
        license_url = anvato_stream_info['published_urls'][0]['license_url']

        # Get MPEG DASH manifest url
        url = self._download_manifest(url)

        # Follow Location tag redirection because InputStream Adaptive doesn't support this yet
        # https://github.com/peak3d/inputstream.adaptive/issues/286
        url = self._redirect_manifest(url)

        # Extract subtitle info from our stream_info.
        subtitle_info = self._extract_subtitles_from_stream_info(stream_info)

        if stream_type == 'episodes':
            # TV episode
            return ResolvedStream(
                program=stream_info['video']['metadata']['program']['title'],
                title=stream_info['video']['metadata']['title'],
                duration=stream_info['video']['duration'],
                url=url,
                subtitles=subtitle_info,
                license_url=license_url,
                cookies=self._session.cookies.get_dict()
            )
        if stream_type == 'movies':
            # Movie
            return ResolvedStream(
                program=None,
                title=stream_info['video']['metadata']['title'],
                duration=stream_info['video']['duration'],
                url=url,
                subtitles=subtitle_info,
                license_url=license_url,
                cookies=self._session.cookies.get_dict()
            )
        if stream_type == 'channels':
            # Live TV
            return ResolvedStream(
                program=None,
                title=stream_info['video']['metadata']['title'],
                duration=None,
                url=url,
                subtitles=subtitle_info,
                license_url=license_url,
                cookies=self._session.cookies.get_dict()
            )

        raise Exception(localize(30707, type=stream_type))  # Unhandled videoType

    def _get_stream_info(self, strtype, stream_id):
        url = 'https://videoplayer-service.api.persgroep.cloud/config/%s/%s' % (strtype, stream_id)
        logger.debug('Getting stream info from %s', url)
        response = self._session.get(url,
                                     params={
                                         'startPosition': '0.0',
                                         'autoPlay': 'true',
                                     },
                                     headers={
                                         'x-api-key': self._VTM_API_KEY,
                                         'Popcorn-SDK-Version': '1',
                                         'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; Nexus 5 Build/M4B30Z)',
                                     },
                                     proxies=proxies)

        if response.status_code == 403:
            show_ok_dialog(heading='HTTP 403 Forbidden', message=localize(30704))  # Geo-blocked
            return None
        if response.status_code != 200:
            raise Exception('Error %s in _get_stream_info.' % response.status_code)

        info = json.loads(response.text)
        return info

    def _extract_anvato_stream_from_stream_info(self, stream_info):
        # Loop over available streams, and return the one from anvato
        for stream in stream_info['video']['streams']:
            if stream['type'] == 'anvato':
                return stream['anvato']

        raise Exception(localize(30706))  # No stream found that we can handle

    def _extract_subtitles_from_stream_info(self, stream_info):
        subtitles = []
        try:
            for subtitle in stream_info['video']['subtitles']:
                subtitles.append(subtitle['url'])
        except KeyError:
            pass

        return subtitles

    def _anvato_get_anvacks(self, access_key):
        url = 'https://access-prod.apis.anvato.net/anvacks/{key}'.format(key=access_key)
        logger.debug('Getting anvacks from %s', url)
        response = self._session.get(url,
                                     params={
                                         'apikey': self._ANVATO_API_KEY,
                                     },
                                     headers={
                                         'X-Anvato-User-Agent': self._ANVATO_USER_AGENT,
                                         'User-Agent': self._ANVATO_USER_AGENT,
                                     })

        if response.status_code != 200:
            raise Exception('Error %s in _anvato_get_anvacks.' % response.status_code)

        info = json.loads(response.text)
        return info

    def _anvato_get_server_time(self, access_key):
        url = 'https://tkx.apis.anvato.net/rest/v2/server_time'
        logger.debug('Getting servertime from %s with access_key %s', url, access_key)
        response = self._session.get(url,
                                     params={
                                         'anvack': access_key,
                                         'anvtrid': self._generate_random_id(),
                                     },
                                     headers={
                                         'X-Anvato-User-Agent': self._ANVATO_USER_AGENT,
                                         'User-Agent': self._ANVATO_USER_AGENT,
                                     })
        if response.status_code != 200:
            raise Exception('Error %s.' % response.status_code)

        info = json.loads(response.text)
        return info

    def _anvato_get_stream_info(self, anvato_info, stream_info):
        url = 'https://tkx.apis.anvato.net/rest/v2/mcp/video/{video}'.format(**anvato_info)
        logger.debug('Getting stream info from %s with access_key %s and token %s', url, anvato_info['accessKey'], anvato_info['token'])

        response = self._session.post(url,
                                      json={
                                          "ads": {
                                              "freewheel": {
                                                  "custom": {
                                                      "ml_userid": "",  # TODO: fill in
                                                      "ml_dmp_userid": "",  # TODO: fill in
                                                      "ml_gdprconsent": "",
                                                      "ml_apple_advertising_id": "",
                                                      "ml_google_advertising_id": ""
                                                  },
                                                  "network_id": stream_info['video']['ads']['freewheel']['networkId'],
                                                  "profile_id": stream_info['video']['ads']['freewheel']['profileId'],
                                                  "server_url": stream_info['video']['ads']['freewheel']['serverUrl'],
                                                  "site_section_id": "mdl_vtmgo_phone_android_default",
                                                  "video_asset_id": stream_info['video']['ads']['freewheel'].get('assetId', ''),
                                              }
                                          },
                                          "api": {
                                              "anvstk2": anvato_info['token']
                                          },
                                          "content": {
                                              "mcp_video_id": anvato_info['video']
                                          },
                                          "sdkver": "5.0.39",
                                          "user": {
                                              "adobepass": {
                                                  "err_msg": "",
                                                  "maxrating": "",
                                                  "mvpd": "",
                                                  "resource": "",
                                                  "short_token": ""
                                              },
                                              "device": "android",
                                              "device_id": "b93616a0-4204-4872-a1cc-999999999999"  # TODO: randomize
                                          },
                                          "version": "3.0"
                                      },
                                      params={
                                          'anvack': anvato_info['accessKey'],
                                          'anvtrid': self._generate_random_id(),
                                          'rtyp': 'fp',
                                      },
                                      headers={
                                          'X-Anvato-User-Agent': self._ANVATO_USER_AGENT,
                                          'User-Agent': self._ANVATO_USER_AGENT,
                                      })
        if response.status_code == 403:
            show_ok_dialog(heading='HTTP 403 Forbidden', message=localize(30704))  # Geo-blocked error
            return None
        if response.status_code != 200:
            raise Exception('Error %s.' % response.status_code)

        import re
        matches = re.search(r"^anvatoVideoJSONLoaded\((.*)\)$", response.text)
        if not matches:
            raise Exception(localize(30705))  # Could not parse media info
        info = json.loads(matches.group(1))
        return info

    def _generate_random_id(self, length=32):
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(letters) for i in range(length))

    def _download_text(self, url):
        logger.debug('Downloading text from %s', url)
        response = self._session.get(url,
                                     headers={
                                         'X-Anvato-User-Agent': self._ANVATO_USER_AGENT,
                                         'User-Agent': self._ANVATO_USER_AGENT,
                                     })
        if response.status_code != 200:
            raise Exception('Error %s.' % response.status_code)

        return response.text

    def _download_manifest(self, url):
        download = self._download_text(url)
        try:
            decoded = json.loads(download)
            if decoded.get('master_m3u8'):
                logger.debug('Followed redirection from %s to %s', url, decoded.get('master_m3u8'))
                return decoded.get('master_m3u8')
        except Exception:
            logger.error('No manifest url found %s', url)

        # Fallback to the url like we have it
        return url

    def _redirect_manifest(self, url):
        import re
        # Follow when a <Location>url</Location> tag is found.
        # https://github.com/peak3d/inputstream.adaptive/issues/286
        download = self._download_text(url)
        matches = re.search(r"<Location>([^<]+)</Location>", download)
        if matches:
            logger.debug('Followed redirection from %s to %s', url, matches.group(1))
            return matches.group(1)

        # Fallback to the url like we have it
        return url

    def create_license_key(self, key_url, key_type='R', key_headers=None, key_value=None):
        header = ''
        if key_headers:
            header = urlencode(key_headers)

        if key_type in ('A', 'R', 'B'):
            key_value = key_type + '{SSM}'
        elif key_type == 'D':
            if 'D{SSM}' not in key_value:
                raise ValueError('Missing D{SSM} placeholder')
            key_value = quote(key_value)

        return '%s|%s|%s|' % (key_url, header, key_value)
