# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import json
import logging

try:  # Python 3
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib import quote

import requests
from resources.lib.kodiutils import proxies

logger = logging.getLogger()


class LiveChannel:
    def __init__(self, channel_id=None, name=None, logo=None, epg=None):
        """ Defines a tv channel that can be streamed live.
        :type channel_id: str
        :type name: str
        :type logo: str
        :type epg: List[LiveChannelEpg]
        """
        self.id = channel_id
        self.name = name
        self.logo = logo
        self.epg = epg
        self.geoblocked = True
        self.mediatype = 'video'

    def __repr__(self):
        return "%r" % self.__dict__


class LiveChannelEpg:
    def __init__(self, title=None, start=None, end=None):
        """ Defines a program that is broadcast on a live tv channel.
        :type title: str
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
        """ Defines a category from the catalogue.
        :type category_id: str
        :type title: str
        """
        self.id = category_id
        self.title = title

    def __repr__(self):
        return "%r" % self.__dict__


class Content:
    CONTENT_TYPE_MOVIE = 'MOVIE'
    CONTENT_TYPE_PROGRAM = 'PROGRAM'

    def __init__(self, video_id=None, title=None, description=None, cover=None, video_type=None, geoblocked=None):
        """ Defines an item from the catalogue.
        :type video_id: str
        :type title: str
        :type description: str
        :type cover: str
        :type video_type: str
        :type geoblocked: bool
        """
        self.id = video_id
        self.title = title
        self.description = description if description else ''
        self.cover = cover
        self.type = video_type
        self.geoblocked = geoblocked
        # If it is a TV show we return None to get a folder icon
        self.mediatype = 'movie' if video_type == self.CONTENT_TYPE_MOVIE else None

    def __repr__(self):
        return "%r" % self.__dict__


class Movie:
    def __init__(self, movie_id=None, name=None, description=None, year=None, cover=None, duration=None, remaining=None, geoblocked=None,
                 channel=None, legal=None, aired=None):
        """ Defines a Movie.
        :type movie_id: str
        :type name: str
        :type description: str
        :type year: int
        :type cover: str
        :type duration: int
        :type remaining: str
        :type geoblocked: bool
        :type channel: str
        :type legal: str
        :type aired: str
        """
        self.id = movie_id
        self.name = name
        self.description = description if description else ''
        self.year = year
        self.cover = cover
        self.duration = duration
        self.remaining = remaining
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal
        self.aired = aired
        self.mediatype = 'movie'

    def __repr__(self):
        return "%r" % self.__dict__


class Program:
    def __init__(self, program_id=None, name=None, description=None, cover=None, seasons=None, geoblocked=None, channel=None, legal=None):
        """ Defines a Program.
        :type program_id: str
        :type name: str
        :type description: str
        :type cover: str
        :type seasons: List[Season]
        :type geoblocked: bool
        :type channel: str
        :type legal: str
        """
        self.id = program_id
        self.name = name
        self.description = description if description else ''
        self.cover = cover
        self.seasons = seasons
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal
        self.mediatype = 'tvshow'

    def __repr__(self):
        return "%r" % self.__dict__


class Season:
    def __init__(self, number=None, episodes=None, cover=None, geoblocked=None, channel=None, legal=None):
        """ Defines a Season.
        :type number: str
        :type episodes: List[Episode]
        :type cover: str
        :type geoblocked: bool
        :type channel: str
        :type legal: str
        """
        self.number = int(number)
        self.episodes = episodes
        self.cover = cover
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal

    def __repr__(self):
        return "%r" % self.__dict__


class Episode:
    def __init__(self, episode_id=None, number=None, season=None, name=None, description=None, cover=None, duration=None, remaining=None, geoblocked=None,
                 channel=None, legal=None, aired=None):
        """ Defines an Episode.
        :type episode_id: str
        :type number: int
        :type season: str
        :type name: str
        :type description: str
        :type cover: str
        :type duration: int
        :type remaining: int
        :type geoblocked: bool
        :type channel: str
        :type legal: str
        :type aired: str
        """
        import re
        self.id = episode_id
        self.number = int(number)
        self.season = int(season)
        self.name = re.compile('^%d. ' % number).sub('', name)  # Strip episode from name
        self.description = description if description else ''
        self.cover = cover
        self.duration = int(duration) if duration else None
        self.remaining = int(remaining) if remaining is not None else None
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal
        self.aired = aired
        self.mediatype = 'episode'

    def __repr__(self):
        return "%r" % self.__dict__


class VtmGo:
    def __init__(self, kids=False):
        # This can be vtmgo or vtmgo-kids
        self._mode = 'vtmgo-kids' if kids else 'vtmgo'

    def get_config(self):
        """ Returns the config for the app. """
        # This is currently not used
        response = self._get_url('/config')
        info = json.loads(response)
        return info

    def get_main(self):
        """ Returns the config for the dashboard. """
        # This is currently not used
        response = self._get_url('/%s/main' % self._mode)
        info = json.loads(response)
        return info

    def get_live(self):
        """ Get a list of all the live tv channels.
        :rtype List[LiveChannel]
        """
        import dateutil.parser
        response = self._get_url('/%s/live' % self._mode)
        info = json.loads(response)

        channels = []
        for item in info.get('channels'):
            epg = []
            for item_epg in item.get('broadcasts', []):
                epg.append(LiveChannelEpg(
                    title=item_epg.get('name'),
                    start=dateutil.parser.parse(item_epg.get('startsAt')),
                    end=dateutil.parser.parse(item_epg.get('endsAt')),
                ))
            channels.append(LiveChannel(
                channel_id=item.get('channelId'),
                logo=item.get('channelLogoUrl'),
                name=item.get('name'),
                epg=epg,
            ))

        return channels

    def get_categories(self):
        """ Get a list of all the categories.
        :rtype List[Category]
        """
        response = self._get_url('/%s/catalog/filters' % self._mode)
        info = json.loads(response)

        categories = []
        for item in info.get('catalogFilters', []):
            categories.append(Category(
                category_id=item.get('id'),
                title=item.get('title'),
            ))

        return categories

    def get_items(self, category=None):
        """ Get a list of all the items in a category.
        :type category: str
        :rtype List[Content]
        """
        if category and category != 'all':
            response = self._get_url('/%s/catalog?pageSize=%d&filter=%s' % (self._mode, 1000, quote(category)))
        else:
            response = self._get_url('/%s/catalog?pageSize=%d' % (self._mode, 1000))
        info = json.loads(response)

        items = []
        for item in info.get('pagedTeasers', {}).get('content', []):
            items.append(Content(
                video_id=item.get('target', {}).get('id'),
                title=item.get('title'),
                cover=item.get('imageUrl'),
                video_type=item.get('target', {}).get('type'),
                geoblocked=item.get('geoBlocked'),
            ))

        return items

    def get_movie(self, movie_id):
        """ Get the details of the specified movie.
        :type movie_id: str
        :rtype Movie
        """
        response = self._get_url('/%s/movies/%s' % (self._mode, movie_id))
        info = json.loads(response)
        movie = info.get('movie', {})
        channel_url = movie.get('channelLogoUrl')
        if channel_url:
            import os.path
            channel = os.path.basename(channel_url).split('-')[0]
        else:
            channel = 'vtmgo'

        return Movie(
            movie_id=movie.get('id'),
            name=movie.get('name'),
            description=movie.get('description'),
            duration=movie.get('durationSeconds'),
            cover=movie.get('bigPhotoUrl'),
            year=movie.get('productionYear'),
            geoblocked=movie.get('geoBlocked'),
            remaining=movie.get('remainingDaysAvailable'),
            legal=movie.get('legalIcons'),
            aired=movie.get('broadcastTimestamp'),
            channel=channel,
        )

    def get_program(self, program_id):
        """ Get the details of the specified program.
        :type program_id: str
        :rtype Program
        """
        response = self._get_url('/%s/programs/%s' % (self._mode, program_id))
        info = json.loads(response)
        program = info.get('program', {})
        channel_url = program.get('channelLogoUrl')
        if channel_url:
            import os.path
            channel = os.path.basename(channel_url).split('-')[0]
        else:
            channel = 'vtmgo'

        seasons = {}
        for item_season in program.get('seasons', []):
            episodes = {}

            for item_episode in item_season.get('episodes', []):
                episodes[item_episode.get('index')] = Episode(
                    episode_id=item_episode.get('id'),
                    number=item_episode.get('index'),
                    season=item_season.get('index'),
                    name=item_episode.get('name'),
                    description=item_episode.get('description'),
                    duration=item_episode.get('durationSeconds'),
                    cover=item_episode.get('bigPhotoUrl'),
                    geoblocked=program.get('geoBlocked'),
                    remaining=item_episode.get('remainingDaysAvailable'),
                    channel=channel,
                    legal=program.get('legalIcons'),
                    aired=item_episode.get('broadcastTimestamp'),
                )

            seasons[item_season.get('index')] = Season(
                number=item_season.get('index'),
                episodes=episodes.values(),
                cover=item_season.get('episodes', [{}])[0].get('bigPhotoUrl') if episodes else program.get('bigPhotoUrl'),
                geoblocked=program.get('geoBlocked'),
                channel=channel,
                legal=program.get('legalIcons'),
            )

        return Program(
            program_id=program.get('id'),
            name=program.get('name'),
            description=program.get('description'),
            cover=program.get('bigPhotoUrl'),
            geoblocked=program.get('geoBlocked'),
            seasons=seasons.values(),
            channel=channel,
            legal=program.get('legalIcons'),
        )

    def get_episode(self, episode_id):
        """ Get the details of the specified episode.
        :type episode_id: str
        :rtype Episode
        """
        response = self._get_url('/%s/episodes/%s' % (self._mode, episode_id))
        info = json.loads(response)
        episode = info.get('episode', {})

        return Episode(
            episode_id=episode.get('id'),
            number=episode.get('index'),
            season=episode.get('seasonIndex'),
            name=episode.get('name'),
            description=episode.get('description'),
            cover=episode.get('bigPhotoUrl'),
        )

    def do_search(self, search):
        """ Do a search in the full catalogue.
        :type search: str
        :rtype List[Content]
        """
        response = self._get_url('/%s/autocomplete/?maxItems=50&keywords=%s' % (self._mode, quote(search)))
        results = json.loads(response)

        items = []
        for item in results.get('suggestions', []):
            items.append(Content(
                video_id=item.get('id'),
                title=item.get('name'),
                video_type=item.get('type'),
            ))

        return items

    def _get_url(self, url, auth=None):
        """ Makes a GET request for the specified URL.
        :type url: str
        :type auth: str
        :rtype str
        """
        headers = {
            'x-app-version': '5',
            'x-persgroep-mobile-app': 'true',
            'x-persgroep-os': 'android',
            'x-persgroep-os-version': '23',
            'User-Agent': 'VTMGO/6.5.0 (be.vmma.vtm.zenderapp; build:11019; Android 23) okhttp/3.12.1'
        }
        if auth:
            headers['x-dpp-jwt'] = auth

        logging.debug('Fetching %s...', url)

        response = requests.session().get('https://api.vtmgo.be' + url, headers=headers, verify=False, proxies=proxies)

        if response.status_code != 200:
            raise Exception('Error %s.' % response.status_code)

        return response.text
