# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals
import json
import logging
from urllib import quote

import dateutil.parser
import requests
from xbmcaddon import Addon

ADDON = Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))


class LiveChannel:
    def __init__(self, id=None, name=None, logo=None, epg=None):
        """
        Defines a TV channel that can be streamed live.
        :type id: basestring
        :type name: basestring
        :type logo: basestring
        :type epg: List[LiveChannelEpg]
        """
        self.id = id
        self.name = name
        self.logo = logo
        self.epg = epg

    def __repr__(self):
        return "%r" % self.__dict__


class LiveChannelEpg:
    def __init__(self, title=None, start=None, end=None):
        """
        Defines a Program that is broadcasted on a live TV Channel.
        :type title: string
        :type start: datetime.datetime
        :type end: datetime.datetime
        """
        self.title = title
        self.start = start
        self.end = end

    def __repr__(self):
        return "%r" % self.__dict__


class Category:
    def __init__(self, id=None, title=None):
        """
        Defines a Category from the Catalogue.
        :type id: string
        :type title: string
        """
        self.id = id
        self.title = title

    def __repr__(self):
        return "%r" % self.__dict__


class Content:
    CONTENT_TYPE_MOVIE = 'MOVIE'
    CONTENT_TYPE_PROGRAM = 'PROGRAM'

    def __init__(self, id=None, title=None, description=None, cover=None, type=None):
        """
        Defines a Category from the Catalogue.
        :type id: string
        :type title: string
        :type description: string
        :type cover: string
        :type type: string
        """
        self.id = id
        self.title = title
        self.description = description
        self.cover = cover
        self.type = type

    def __repr__(self):
        return "%r" % self.__dict__


class Movie:
    def __init__(self, id=None, name=None, description=None, year=None, cover=None, duration=None, remaining=None):
        self.id = id
        self.name = name
        self.description = description
        self.year = year
        self.cover = cover
        self.duration = duration
        self.remaining = remaining

    def __repr__(self):
        return "%r" % self.__dict__


class Program:
    def __init__(self, id=None, name=None, description=None, cover=None, seasons=None):
        """
        Defines a Program.
        :type id: basestring
        :type name: basestring
        :type description: basestring
        :type cover: basestring
        :type seasons: List[Season]
        """
        self.id = id
        self.name = name
        self.description = description
        self.cover = cover
        self.seasons = seasons

    def __repr__(self):
        return "%r" % self.__dict__


class Season:
    def __init__(self, number=None, episodes=None):
        """

        :type number: basestring
        :type episodes: List[Episode]
        """
        self.number = int(number)
        self.episodes = episodes

    def __repr__(self):
        return "%r" % self.__dict__


class Episode:
    def __init__(self, id=None, number=None, season=None, name=None, description=None, cover=None, duration=None, remaining=None):
        self.id = id
        self.number = int(number)
        self.season = int(season)
        self.name = name
        self.description = description
        self.cover = cover
        self.duration = int(duration) if duration else None
        self.remaining = int(remaining) if remaining else None

    def __repr__(self):
        return "%r" % self.__dict__


class VtmGo:

    def get_config(self):
        ''' Not sure if we need this '''
        response = self._get_url('/config')
        info = json.loads(response)
        return info

    def get_main(self):
        ''' Not sure if we need this '''
        response = self._get_url('/vtmgo/main')
        info = json.loads(response)
        return info

    def get_live(self):
        response = self._get_url('/vtmgo/live')
        info = json.loads(response)

        channels = []
        for item in info['channels']:
            epg = []
            for item_epg in item['broadcasts']:
                epg.append(LiveChannelEpg(
                    title=item_epg['name'],
                    start=dateutil.parser.parse(item_epg['startsAt']),
                    end=dateutil.parser.parse(item_epg['endsAt']),
                ))
            channels.append(LiveChannel(
                id=item['channelId'],
                logo=item['channelLogoUrl'],
                name=item['name'],
                epg=epg,
            ))

        return channels

    def get_categories(self):
        response = self._get_url('/vtmgo/catalog/filters')
        info = json.loads(response)

        categories = []
        for item in info['catalogFilters']:
            categories.append(Category(
                id=item['id'],
                title=item['title'],
            ))

        return categories

    def get_items(self, category=None):
        if category:
            response = self._get_url('/vtmgo/catalog?filter=' + category)
        else:
            response = self._get_url('/vtmgo/catalog')
        info = json.loads(response)

        items = []
        for item in info['pagedTeasers']['content']:
            items.append(Content(
                id=item['target']['id'],
                title=item['title'],
                cover=item['imageUrl'],
                type=item['target']['type'],
            ))

        return items

    def get_movie(self, id):
        response = self._get_url('/vtmgo/movies/' + id)
        info = json.loads(response)

        return Movie(
            id=info['movie']['id'],
            name=info['movie']['name'],
            description=info['movie']['description'],
            duration=info['movie']['durationSeconds'],
            cover=info['movie']['bigPhotoUrl'],
            year=info['movie']['productionYear'],
            remaining=info['movie']['remainingDaysAvailable'],
        )

    def get_program(self, id):
        response = self._get_url('/vtmgo/programs/' + id)
        info = json.loads(response)

        seasons = {}
        for item_season in info['program']['seasons']:
            episodes = {}
            for item_episode in item_season['episodes']:
                episodes[item_episode['index']] = Episode(
                    id=item_episode['id'],
                    number=item_episode['index'],
                    season=item_season['index'],
                    name=item_episode['name'],
                    description=item_episode['description'],
                    duration=item_episode['durationSeconds'],
                    cover=item_episode['bigPhotoUrl'],
                    remaining=item_episode['remainingDaysAvailable'],
                )

            seasons[item_season['index']] = Season(
                number=item_season['index'],
                episodes=episodes
            )

        return Program(
            id=info['program']['id'],
            name=info['program']['name'],
            description=info['program']['description'],
            cover=info['program']['bigPhotoUrl'],
            seasons=seasons,
        )

    # def get_episodes(self, id):
    #     response = self._get_url('/vtmgo/episodes/' + id)
    #     info = json.loads(response)
    #
    #     return info

    def do_search(self, search):
        response = self._get_url('/vtmgo/autocomplete/?maxItems=10&keywords=%s' % quote(search))
        results = json.loads(response)

        items = []
        for item in results['suggestions']:
            items.append(Content(
                id=item['id'],
                title=item['name'],
                type=item['type'],
            ))

        return items

    def _get_url(self, url, auth=None):
        headers = {
            # ':authority': 'api.vtmgo.be',
            'x-app-version': '5',
            'x-persgroep-mobile-app': 'true',
            'x-persgroep-os': 'android',
            'x-persgroep-os-version': '23',
            'User-Agent': 'VTMGO/6.5.0 (be.vmma.vtm.zenderapp; build:11019; Android 23) okhttp/3.12.1'
        }
        if auth:
            headers['x-dpp-jwt'] = auth

        response = requests.session().get('https://api.vtmgo.be' + url, headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception('Error %s.' % response.status_code)

        return response.text
