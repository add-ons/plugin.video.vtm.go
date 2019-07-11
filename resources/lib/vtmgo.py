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
    def __init__(self, channel_id=None, name=None, logo=None, epg=None):
        """
        Defines a TV channel that can be streamed live.
        :type id: basestring
        :type name: basestring
        :type logo: basestring
        :type epg: List[LiveChannelEpg]
        """
        self.id = channel_id
        self.name = name
        self.logo = logo
        self.epg = epg
        self.mediatype = 'video'

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
    def __init__(self, category_id=None, title=None):
        """
        Defines a Category from the Catalogue.
        :type category_id: string
        :type title: string
        """
        self.id = category_id
        self.title = title

    def __repr__(self):
        return "%r" % self.__dict__


class Content:
    CONTENT_TYPE_MOVIE = 'MOVIE'
    CONTENT_TYPE_PROGRAM = 'PROGRAM'

    def __init__(self, video_id=None, title=None, description=None, cover=None, video_type=None):
        """
        Defines a Category from the Catalogue.
        :type video_id: basestring
        :type title: basestring
        :type description: basestring
        :type cover: basestring
        :type video_type: basestring
        """
        self.id = video_id
        self.title = title
        self.description = description
        self.cover = cover
        self.type = video_type
        # If it is a TV show we return None to get a folder icon
        self.mediatype = 'movie' if video_type == self.CONTENT_TYPE_MOVIE else None

    def __repr__(self):
        return "%r" % self.__dict__


class Movie:
    def __init__(self, movie_id=None, name=None, description=None, year=None, cover=None, duration=None, remaining=None):
        self.id = movie_id
        self.name = name
        self.description = description
        self.year = year
        self.cover = cover
        self.duration = duration
        self.remaining = remaining
        self.mediatype = 'movie'

    def __repr__(self):
        return "%r" % self.__dict__


class Program:
    def __init__(self, program_id=None, name=None, description=None, cover=None, seasons=None):
        """
        Defines a Program.
        :type program_id: basestring
        :type name: basestring
        :type description: basestring
        :type cover: basestring
        :type seasons: List[Season]
        """
        self.id = program_id
        self.name = name
        self.description = description
        self.cover = cover
        self.seasons = seasons
        self.mediatype = 'tvshow'

    def __repr__(self):
        return "%r" % self.__dict__


class Season:
    def __init__(self, number=None, episodes=None, cover=None):
        """

        :type number: basestring
        :type episodes: List[Episode]
        :type cover: basestring
        """
        self.number = int(number)
        self.episodes = episodes
        self.cover = cover

    def __repr__(self):
        return "%r" % self.__dict__


class Episode:
    def __init__(self, episode_id=None, number=None, season=None, name=None, description=None, cover=None, duration=None, remaining=None):
        self.id = episode_id
        self.number = int(number)
        self.season = int(season)
        self.name = name
        self.description = description
        self.cover = cover
        self.duration = int(duration) if duration else None
        self.remaining = int(remaining) if remaining is not None else None
        self.mediatype = 'episode'

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
                channel_id=item['channelId'],
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
                category_id=item['id'],
                title=item['title'],
            ))

        return categories

    def get_items(self, category=None):
        if category and category != 'all':
            response = self._get_url('/vtmgo/catalog?pageSize=%d&filter=%s' % (1000, quote(category)))
        else:
            response = self._get_url('/vtmgo/catalog?pageSize=1000')
        info = json.loads(response)

        items = []
        for item in info['pagedTeasers']['content']:
            items.append(Content(
                video_id=item['target']['id'],
                title=item['title'],
                cover=item['imageUrl'],
                video_type=item['target']['type'],
            ))

        return items

    def get_movie(self, movie_id):
        response = self._get_url('/vtmgo/movies/' + movie_id)
        info = json.loads(response)

        return Movie(
            movie_id=info['movie']['id'],
            name=info['movie']['name'],
            description=info['movie']['description'],
            duration=info['movie']['durationSeconds'],
            cover=info['movie']['bigPhotoUrl'],
            year=info['movie']['productionYear'],
            remaining=info['movie']['remainingDaysAvailable'],
        )

    def get_program(self, program_id):
        response = self._get_url('/vtmgo/programs/' + program_id)
        info = json.loads(response)

        seasons = {}
        for item_season in info['program']['seasons']:
            episodes = {}
            for item_episode in item_season['episodes']:
                episodes[item_episode['index']] = Episode(
                    episode_id=item_episode['id'],
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
                episodes=episodes,
                cover=item_season['episodes'][0]['bigPhotoUrl'],
            )

        return Program(
            program_id=info['program']['id'],
            name=info['program']['name'],
            description=info['program']['description'],
            cover=info['program']['bigPhotoUrl'],
            seasons=seasons,
        )

    # def get_episodes(self, episode_id):
    #     response = self._get_url('/vtmgo/episodes/' + episode_id)
    #     info = json.loads(response)
    #
    #     return info

    def do_search(self, search):
        response = self._get_url('/vtmgo/autocomplete/?maxItems=50&keywords=%s' % quote(search))
        results = json.loads(response)

        items = []
        for item in results['suggestions']:
            items.append(Content(
                video_id=item['id'],
                title=item['name'],
                video_type=item['type'],
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
