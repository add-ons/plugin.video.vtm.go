# -*- coding: utf-8 -*-
""" VTM GO API """
# pylint: disable=missing-function-docstring

from __future__ import absolute_import, division, unicode_literals

import json

import requests

from resources.lib import UnavailableException
from resources.lib.kodiwrapper import LOG_DEBUG, KodiWrapper, to_unicode, LOG_INFO  # pylint: disable=unused-import
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth

try:  # Python 3
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib import quote


class LiveChannel:
    """ Defines a tv channel that can be streamed live """
    def __init__(self, channel_id=None, name=None, logo=None, epg=None, geoblocked=False):
        """
        :type channel_id: str
        :type name: str
        :type logo: str
        :type epg: list[LiveChannelEpg]
        :type geoblocked: bool
        """
        self.channel_id = channel_id
        self.name = name
        self.logo = logo
        self.epg = epg
        self.geoblocked = geoblocked

    def __repr__(self):
        return "%r" % self.__dict__


class LiveChannelEpg:
    """ Defines a program that is broadcast on a live tv channel"""
    def __init__(self, title=None, start=None, end=None):
        """
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
    """ Defines a category from the catalogue"""
    def __init__(self, category_id=None, title=None, content=None):
        """
        :type category_id: str
        :type title: str
        :type content: list[Content]
        """
        self.category_id = category_id
        self.title = title
        self.content = content

    def __repr__(self):
        return "%r" % self.__dict__


class Content:
    """ Defines an item from the catalogue"""
    CONTENT_TYPE_MOVIE = 'MOVIE'
    CONTENT_TYPE_PROGRAM = 'PROGRAM'

    def __init__(self, content_id=None, title=None, description=None, cover=None, video_type=None, my_list=False, geoblocked=None):
        """
        :type content_id: str
        :type title: str
        :type description: str
        :type cover: str
        :type video_type: str
        :type my_list: bool
        :type geoblocked: bool
        """
        self.content_id = content_id
        self.title = title
        self.description = description if description else ''
        self.cover = cover
        self.video_type = video_type
        self.my_list = my_list
        self.geoblocked = geoblocked

    def __repr__(self):
        return "%r" % self.__dict__


class Movie:
    """ Defines a Movie"""
    def __init__(self, movie_id=None, name=None, description=None, year=None, cover=None, duration=None, remaining=None, geoblocked=None,
                 channel=None, legal=None, aired=None):
        """
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
        self.movie_id = movie_id
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

    def __repr__(self):
        return "%r" % self.__dict__


class Program:
    """ Defines a Program"""
    def __init__(self, program_id=None, name=None, description=None, cover=None, seasons=None, geoblocked=None, channel=None, legal=None):
        """
        :type program_id: str
        :type name: str
        :type description: str
        :type cover: str
        :type seasons: dict[int, Season]
        :type geoblocked: bool
        :type channel: str
        :type legal: str
        """
        self.program_id = program_id
        self.name = name
        self.description = description if description else ''
        self.cover = cover
        self.seasons = seasons
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal

    def __repr__(self):
        return "%r" % self.__dict__


class Season:
    """ Defines a Season"""
    def __init__(self, number=None, episodes=None, cover=None, geoblocked=None, channel=None, legal=None):
        """
        :type number: str
        :type episodes: dict[int, Episode]
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
    """ Defines an Episode """
    def __init__(self, episode_id=None, number=None, season=None, name=None, description=None, cover=None, duration=None, remaining=None, geoblocked=None,
                 channel=None, legal=None, aired=None):
        """
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
        self.episode_id = episode_id
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

    def __repr__(self):
        return "%r" % self.__dict__


class VtmGo:
    """ VTM GO API """
    def __init__(self, kodi):
        self._kodi = kodi  # type: KodiWrapper
        self._proxies = kodi.get_proxies()
        self._auth = VtmGoAuth(kodi)

        # This can be vtmgo or vtmgo-kids
        self._mode = 'vtmgo-kids' if self._kodi.kids_mode() else 'vtmgo'

    def get_config(self):
        """ Returns the config for the app. """
        # This is currently not used
        response = self._get_url('/config')
        info = json.loads(response)

        # This contains a player.updateIntervalSeconds that could be used to notify VTM GO about the playing progress
        return info

    def get_recommendations(self):
        """ Returns the config for the dashboard. """
        response = self._get_url('/%s/main' % self._mode)
        recommendations = json.loads(response)

        categories = []
        for cat in recommendations.get('rows', []):
            if cat.get('rowType') in ['SWIMLANE_DEFAULT']:
                items = []

                for item in cat.get('teasers'):
                    items.append(Content(
                        content_id=item.get('target', {}).get('id'),
                        video_type=item.get('target', {}).get('type'),
                        title=item.get('title'),
                        geoblocked=item.get('geoBlocked'),
                        cover=item.get('imageUrl'),
                    ))

                categories.append(Category(
                    category_id=cat.get('id'),
                    title=cat.get('title'),
                    content=items,
                ))

        return categories

    def get_mylist(self):
        """ Returns the contents of My List """
        response = self._get_url('/%s/main/swimlane/my-list' % self._mode)

        # My list can be empty
        if not response:
            return []

        result = json.loads(response)

        items = []
        for item in result.get('teasers'):
            items.append(Content(
                content_id=item.get('target', {}).get('id'),
                video_type=item.get('target', {}).get('type'),
                title=item.get('title'),
                geoblocked=item.get('geoBlocked'),
                cover=item.get('imageUrl'),
            ))

        return items

    def add_mylist(self, video_type, content_id):
        """ Add an item to My List """
        self._put_url('/%s/userData/myList/%s/%s' % (self._mode, video_type, content_id))

    def del_mylist(self, video_type, content_id):
        """ Delete an item from My List """
        self._delete_url('/%s/userData/myList/%s/%s' % (self._mode, video_type, content_id))

    def get_live_channels(self):
        """ Get a list of all the live tv channels.
        :rtype list[LiveChannel]
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
        :rtype list[Category]
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
        :rtype list[Content]
        """
        if category and category != 'all':
            response = self._get_url('/%s/catalog?pageSize=%d&filter=%s' % (self._mode, 1000, quote(category)))
        else:
            response = self._get_url('/%s/catalog?pageSize=%d' % (self._mode, 1000))
        info = json.loads(response)

        items = []
        for item in info.get('pagedTeasers', {}).get('content', []):
            items.append(Content(
                content_id=item.get('target', {}).get('id'),
                title=item.get('title'),
                cover=item.get('imageUrl'),
                video_type=item.get('target', {}).get('type'),
                geoblocked=item.get('geoBlocked'),
            ))

        return items

    def get_movie(self, movie_id, only_cache=False):
        """ Get the details of the specified movie.
        :type movie_id: str
        :type only_cache: bool
        :rtype Movie
        """
        if only_cache:
            # Fetch from cache if asked
            movie = self._kodi.get_cache(['movie', movie_id])
            if not movie:
                return None
        else:
            # Fetch from API
            response = self._get_url('/%s/movies/%s' % (self._mode, movie_id))
            info = json.loads(response)
            movie = info.get('movie', {})
            self._kodi.set_cache(['movie', movie_id], movie)

        channel_url = movie.get('channelLogoUrl')
        if channel_url:
            import os.path
            channel = os.path.basename(channel_url).split('-')[0].upper()
        else:
            channel = 'VTM GO'

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

    def get_program(self, program_id, only_cache=False):
        """ Get the details of the specified program.
        :type program_id: str
        :type only_cache: bool
        :rtype Program
        """
        if only_cache:
            # Fetch from cache if asked
            program = self._kodi.get_cache(['program', program_id])
            if not program:
                return None
        else:
            # Fetch from API
            response = self._get_url('/%s/programs/%s' % (self._mode, program_id))
            info = json.loads(response)
            program = info.get('program', {})
            self._kodi.set_cache(['program', program_id], program)

        channel_url = program.get('channelLogoUrl')
        if channel_url:
            import os.path
            channel = os.path.basename(channel_url).split('-')[0].upper()
        else:
            channel = 'VTM GO'

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
                episodes=episodes,
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
            seasons=seasons,
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
        :rtype list[Content]
        """
        response = self._get_url('/%s/autocomplete/?maxItems=%d&keywords=%s' % (self._mode, 50, quote(search)))
        results = json.loads(response)

        items = []
        for item in results.get('suggestions', []):
            items.append(Content(
                content_id=item.get('id'),
                title=item.get('name'),
                video_type=item.get('type'),
            ))

        return items

    def _get_url(self, url):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        headers = {
            'x-app-version': '5',
            'x-persgroep-mobile-app': 'true',
            'x-persgroep-os': 'android',
            'x-persgroep-os-version': '23',
            'User-Agent': 'VTMGO/6.5.0 (be.vmma.vtm.zenderapp; build:11019; Android 23) okhttp/3.12.1'
        }

        token = self._auth.get_token()
        if token:
            headers['x-dpp-jwt'] = token

        self._kodi.log('Sending GET {url}...', LOG_INFO, url=url)

        response = requests.session().get('https://api.vtmgo.be' + url, headers=headers, verify=False, proxies=self._proxies)

        self._kodi.log('Got response: {response}', LOG_DEBUG, response=response.text)

        if response.status_code == 404:
            raise UnavailableException()

        if response.status_code not in [200, 204]:
            raise Exception('Error %s.' % response.status_code)

        return response.text

    def _put_url(self, url):
        """ Makes a PUT request for the specified URL.
        :type url: str
        :rtype str
        """
        headers = {
            'x-app-version': '5',
            'x-persgroep-mobile-app': 'true',
            'x-persgroep-os': 'android',
            'x-persgroep-os-version': '23',
            'User-Agent': 'VTMGO/6.5.0 (be.vmma.vtm.zenderapp; build:11019; Android 23) okhttp/3.12.1'
        }

        token = self._auth.get_token()
        if token:
            headers['x-dpp-jwt'] = token

        self._kodi.log('Sending PUT {url}...', LOG_INFO, url=url)

        response = requests.session().put('https://api.vtmgo.be' + url, headers=headers, verify=False, proxies=self._proxies)

        self._kodi.log('Got response: {response}', LOG_DEBUG, response=response.text)

        if response.status_code == 404:
            raise UnavailableException()

        if response.status_code not in [200, 204]:
            raise Exception('Error %s.' % response.status_code)

        return response.text

    def _delete_url(self, url):
        """ Makes a DELETE request for the specified URL.
        :type url: str
        :rtype str
        """
        headers = {
            'x-app-version': '5',
            'x-persgroep-mobile-app': 'true',
            'x-persgroep-os': 'android',
            'x-persgroep-os-version': '23',
            'User-Agent': 'VTMGO/6.5.0 (be.vmma.vtm.zenderapp; build:11019; Android 23) okhttp/3.12.1'
        }

        token = self._auth.get_token()
        if token:
            headers['x-dpp-jwt'] = token

        self._kodi.log('Sending DELETE {url}...', LOG_INFO, url=url)

        response = requests.session().delete('https://api.vtmgo.be' + url, headers=headers, verify=False, proxies=self._proxies)

        self._kodi.log('Got response: {response}', LOG_DEBUG, response=response.text)

        if response.status_code == 404:
            raise UnavailableException()

        if response.status_code not in [200, 204]:
            raise Exception('Error %s.' % response.status_code)

        return response.text
