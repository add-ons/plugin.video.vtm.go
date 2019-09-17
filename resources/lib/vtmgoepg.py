# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import json
from datetime import datetime, timedelta

import dateutil.parser
import dateutil.tz
import requests

from resources.lib import kodilogging


class EpgChannel:
    def __init__(self, uuid=None, key=None, name=None, logo=None, broadcasts=None):
        self.uuid = uuid
        self.key = key
        self.name = name
        self.logo = logo
        self.broadcasts = broadcasts

    def __repr__(self):
        return "%r" % self.__dict__


class EpgBroadcast:
    def __init__(self, uuid=None, playable_type=None, title=None, time=None, duration=None, image=None, description=None, live=None, rerun=None, tip=None,
                 program_uuid=None, playable_uuid=None):
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

    def __repr__(self):
        return "%r" % self.__dict__


class VtmGoEpg:
    EPG_URL = 'https://vtm.be/tv-gids/api/v2/broadcasts/{date}'
    DETAILS_URL = 'https://vtm.be/tv-gids/{channel}/uitzending/{type}/{uuid}'

    def __init__(self):
        self._session = requests.session()

    def get_epg(self, date=None):
        # TODO: implement caching

        # Fetch today when no date is specified
        if date is None:
            date = datetime.today().strftime('%Y-%m-%d')

        url = self.EPG_URL.format(date=date)

        kodilogging.log('Fetching %s...' % url, kodilogging.LOGDEBUG)

        response = self._session.get(url)
        if response.status_code != 200:
            raise Exception('Error %s while fetching EPG data.' % response.status_code)

        epg = json.loads(response.text)

        result = {}
        for channel in epg.get('channels', []):
            broadcasts = [self._parse_broadcast(broadcast) for broadcast in channel.get('broadcasts', [])]
            result[channel.get('seoKey')] = EpgChannel(
                name=channel.get('name'),
                key=channel.get('seoKey'),
                logo=channel.get('channelLogoUrl'),
                broadcasts=broadcasts
            )

        return result

    def get_details(self, channel, program_type, epg_id):
        import re

        # Do mapping
        if program_type == 'episodes':
            url = self.DETAILS_URL.format(channel=channel, type='aflevering', uuid=epg_id)
        elif program_type == 'movies':
            url = self.DETAILS_URL.format(channel=channel, type='film', uuid=epg_id)
        elif program_type == 'oneoffs':
            url = self.DETAILS_URL.format(channel=channel, type='oneoff', uuid=epg_id)
        else:
            raise Exception('Unknown broadcast type %s.' % program_type)

        # Add cookies
        self._session.cookies.set('pws', 'functional|analytics|content_recommendation|targeted_advertising|social_media')
        self._session.cookies.set('pwv', '1')

        # Fetch data
        kodilogging.log('Fetching %s...' % url, kodilogging.LOGDEBUG)
        response = self._session.get(url, )
        if response.status_code != 200:
            raise Exception('Error %s while fetching EPG details.' % response.status_code)

        # Extract data
        matches = re.search(r'EPG_REDUX_DATA=([^;]+);', response.content.decode('utf-8'))
        if not matches:
            raise Exception('Could not parse EPG details.')

        # Parse data
        data = json.loads(matches.group(1))

        return self._parse_broadcast(data['details'][epg_id])

    @staticmethod
    def _parse_broadcast(broadcast_json):
        # Sometimes, the duration field is empty, but luckily, we can calculate it.
        duration = broadcast_json.get('duration')
        if duration is None:
            duration = (broadcast_json.get('to') - broadcast_json.get('from')) / 1000

        return EpgBroadcast(
            uuid=broadcast_json.get('uuid'),
            playable_type=broadcast_json.get('playableType'),
            playable_uuid=broadcast_json.get('playableUuid'),
            title=broadcast_json.get('title'),
            time=dateutil.parser.isoparse(broadcast_json.get('fromIso') + 'Z').astimezone(dateutil.tz.gettz('CET')),
            duration=duration,
            image=broadcast_json.get('imageUrl'),
            description=broadcast_json.get('synopsis'),
            live=broadcast_json.get('live'),
            rerun=broadcast_json.get('rerun'),
            tip=broadcast_json.get('tip'),
            program_uuid=broadcast_json.get('programUuid'),
        )

    @staticmethod
    def get_dates():
        dates = []

        today = datetime.today()

        # The API provides 2 days in the past and 7 days in the future
        for i in range(-2, 7):
            day = today + timedelta(days=i)

            # TODO: make this pretty
            if i == -1:
                title = 'Yesterday'
            elif i == 0:
                title = 'Today'
            elif i == 1:
                title = 'Tomorrow'
            else:
                title = day.strftime('%Y-%m-%d')

            dates.append({
                'title': title,
                'date': day.strftime('%Y-%m-%d'),
            })

        return dates
