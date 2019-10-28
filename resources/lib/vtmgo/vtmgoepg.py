# -*- coding: utf-8 -*-
""" VTM GO EPG API """

from __future__ import absolute_import, division, unicode_literals

import json
from datetime import datetime, timedelta

import dateutil.parser
import dateutil.tz
import requests

from resources.lib.kodiwrapper import LOG_DEBUG, KodiWrapper, LOG_ERROR, LOG_INFO  # pylint: disable=unused-import


class EpgChannel:
    """ Defines an Channel with EPG information """

    def __init__(self, uuid=None, key=None, name=None, logo=None, broadcasts=None):
        """
        :type uuid: str
        :type key: str
        :type name: str
        :type logo: str
        :type broadcasts: list[EpgBroadcast]
        """
        self.uuid = uuid
        self.key = key
        self.name = name
        self.logo = logo
        self.broadcasts = broadcasts

    def __repr__(self):
        return "%r" % self.__dict__


class EpgBroadcast:
    """ Defines an EPG broadcast"""

    def __init__(self, uuid=None, playable_type=None, title=None, time=None, duration=None, image=None, description=None, live=None, rerun=None, tip=None,
                 program_uuid=None, playable_uuid=None, airing=None):
        """
        :type uuid: str
        :type playable_type: str
        :type title: str
        :type time: datetime
        :type duration: int
        :type image: str
        :type description: str
        :type live: str
        :type rerun: str
        :type tip: str
        :type program_uuid: str
        :type playable_uuid: str
        :type airing: bool
        """
        self.uuid = uuid
        self.playable_type = playable_type
        self.title = title
        self.time = time
        self.duration = duration
        self.image = image
        self.description = description
        self.live = live
        self.rerun = rerun
        self.tip = tip
        self.program_uuid = program_uuid
        self.playable_uuid = playable_uuid
        self.airing = airing

    def __repr__(self):
        return "%r" % self.__dict__


class VtmGoEpg:
    """ VTM GO EPG API """
    EPG_URL = 'https://vtm.be/tv-gids/api/v2/broadcasts/{date}'
    DETAILS_URL = 'https://vtm.be/tv-gids/{channel}/uitzending/{type}/{uuid}'

    def __init__(self, kodi):
        self._kodi = kodi  # type: KodiWrapper

        self._session = requests.session()
        self._session.cookies.set('pws', 'functional|analytics|content_recommendation|targeted_advertising|social_media')
        self._session.cookies.set('pwv', '1')

    def get_epg(self, channel, date=None):
        """ Load EPG information for the specified channel and date.
        :type channel: str
        :type date: str
        :rtype: EpgChannel
        """
        if date is None:
            # Fetch today when no date is specified
            date = datetime.today().strftime('%Y-%m-%d')
        elif date == 'yesterday':
            date = (datetime.today() + timedelta(days=-1)).strftime('%Y-%m-%d')
        elif date == 'today':
            date = datetime.today().strftime('%Y-%m-%d')
        elif date == 'tomorrow':
            date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

        response = self._get_url(self.EPG_URL.format(date=date))
        epg = json.loads(response)

        # We get an EPG for all channels, but we only return the requested channel.
        for epg_channel in epg.get('channels', []):
            if epg_channel.get('seoKey') == channel:
                return EpgChannel(
                    name=epg_channel.get('name'),
                    key=epg_channel.get('seoKey'),
                    logo=epg_channel.get('channelLogoUrl'),
                    uuid=epg_channel.get('uuid'),
                    broadcasts=[self._parse_broadcast(broadcast) for broadcast in epg_channel.get('broadcasts', [])]
                )

        raise Exception('Channel %s not found in the EPG' % channel)

    def get_broadcast(self, channel, timestamp):
        """ Load EPG information for the specified channel and date.
        :type channel: str
        :type timestamp: str
        :rtype: EpgBroadcast
        """
        # Parse to a real datetime
        timestamp = dateutil.parser.parse(timestamp)

        # Load guide info for this date
        epg = self.get_epg(channel=channel, date=timestamp.strftime('%Y-%m-%d'))

        # Find a matching broadcast
        for broadcast in epg.broadcasts:
            if timestamp <= broadcast.time < (broadcast.time + timedelta(seconds=broadcast.duration)):
                return broadcast

        return None

    def get_details(self, channel, program_type, epg_id):
        """ Load the EPG details for the specified program.
        :type channel: str
        :type program_type: str
        :type epg_id: str
        :rtype: EpgBroadcast
        """
        import re

        # Do mapping
        if program_type == 'episodes':
            url = self.DETAILS_URL.format(channel=channel, type='aflevering', uuid=epg_id)
        elif program_type == 'movies':
            url = self.DETAILS_URL.format(channel=channel, type='film', uuid=epg_id)
        elif program_type == 'oneoffs':
            url = self.DETAILS_URL.format(channel=channel, type='oneoff', uuid=epg_id)
        else:
            self._kodi.log('Unknown broadcast type {type}.', LOG_ERROR, type=program_type)
            return None

        # Fetch data
        response = self._get_url(url)

        # Extract data
        matches = re.search(r'__EPG_REDUX_DATA__=([^;]+);', response)
        if not matches:
            self._kodi.log('Could not parse EPG details.', LOG_ERROR)
            return None

        data = json.loads(matches.group(1))

        self._kodi.log('Got EPG data: {data}', LOG_DEBUG, data=data)

        return self._parse_broadcast(data['details'][epg_id])

    @staticmethod
    def _parse_broadcast(broadcast_json):
        """ Parse the epg data.
        :type broadcast_json: dict
        :rtype: EpgBroadcast
        """
        # The broadcast_json.get('duration') field doesn't include the advertisements, so the total time is incorrect
        duration = (broadcast_json.get('to') - broadcast_json.get('from')) / 1000

        # Check if this broadcast is currently airing
        timestamp = datetime.now(dateutil.tz.tzlocal())
        start = dateutil.parser.parse(broadcast_json.get('fromIso') + 'Z').astimezone(dateutil.tz.gettz('CET'))
        airing = bool(start <= timestamp < (start + timedelta(seconds=duration)))

        return EpgBroadcast(
            uuid=broadcast_json.get('uuid'),
            playable_type=broadcast_json.get('playableType'),
            playable_uuid=broadcast_json.get('playableUuid'),
            title=broadcast_json.get('title'),
            time=start,
            duration=duration,
            image=broadcast_json.get('imageUrl'),
            description=broadcast_json.get('synopsis'),
            live=broadcast_json.get('live'),
            rerun=broadcast_json.get('rerun'),
            tip=broadcast_json.get('tip'),
            program_uuid=broadcast_json.get('programUuid'),
            airing=airing,
        )

    def get_dates(self, date_format):
        """ Return a dict of dates.
        :rtype: list[dict]
        """
        dates = []
        today = datetime.today()

        # The API provides 2 days in the past and 7 days in the future
        for i in range(-2, 7):
            day = today + timedelta(days=i)

            if i == -1:
                dates.append({
                    'title': '%s, %s' % (self._kodi.localize(30301), day.strftime(date_format)),  # Yesterday,
                    'date': 'yesterday',
                    'highlight': False,
                })
            elif i == 0:
                dates.append({
                    'title': '%s, %s' % (self._kodi.localize(30302), day.strftime(date_format)),  # Today
                    'date': 'today',
                    'highlight': True,
                })
            elif i == 1:
                dates.append({
                    'title': '%s, %s' % (self._kodi.localize(30303), day.strftime(date_format)),  # Tomorrow
                    'date': 'tomorrow',
                    'highlight': False,
                })
            else:
                dates.append({
                    'title': day.strftime(date_format),
                    'date': day.strftime('%Y-%m-%d'),
                    'highlight': False,
                })

        return dates

    def _get_url(self, url):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        self._kodi.log('Sending GET {url}...', LOG_INFO, url=url)

        response = self._session.get(url, verify=False)

        if response.status_code != 200:
            raise Exception('Error %s.' % response.status_code)

        return response.text
