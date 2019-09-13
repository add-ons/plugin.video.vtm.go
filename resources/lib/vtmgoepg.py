# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import json
from datetime import datetime, timedelta

import dateutil.parser
import requests


class EpgChannel:
    def __init__(self, uuid=None, key=None, name=None, logo=None, broadcasts=None):
        self.uuid = uuid
        self.key = key
        self.name = name
        self.logo = logo
        self.broadcasts = broadcasts


class EpgBroadcast:
    def __init__(self, uuid=None, mediatype=None, title=None, time=None, duration=None, image=None, description=None, live=None, rerun=None, tip=None):
        self.uuid = uuid
        self.mediatype = mediatype
        self.title = title
        self.time = time
        self.duration = duration
        self.image = image
        self.description = description
        self.live = live
        self.rerun = rerun
        self.tip = tip

    def __repr__(self):
        return "%r" % self.__dict__


class VtmGoEpg:
    EPG_URL = 'https://vtm.be/tv-gids/api/v2/broadcasts/{date}'

    def __init__(self):
        self._session = requests.session()

    def get_epg(self, date=None):
        # TODO: implement caching

        if date is None:
            date = datetime.today().strftime('%Y-%m-%d')

        response = self._session.get(self.EPG_URL.format(date=date))
        if response.status_code != 200:
            raise Exception('Error %s in _get_epg when fetching %s.' % (response.status_code, self.EPG_URL.format(date=date)))

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

    @staticmethod
    def _parse_broadcast(broadcast_json):

        # Sometimes, the duration field is empty, but luckily, we can calculate it.
        duration = broadcast_json.get('duration')
        if duration is None:
            duration = (broadcast_json.get('to') - broadcast_json.get('from')) / 1000

        return EpgBroadcast(
            uuid=broadcast_json.get('uuid'),
            mediatype=broadcast_json.get('playableType'),
            title=broadcast_json.get('title'),
            time=dateutil.parser.parse(broadcast_json.get('fromIso')),
            duration=duration,
            image=broadcast_json.get('imageUrl'),
            description=broadcast_json.get('synopsis'),
            live=broadcast_json.get('live'),
            rerun=broadcast_json.get('rerun'),
            tip=broadcast_json.get('tip'),
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
