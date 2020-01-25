# -*- coding: utf-8 -*-
""" VTM GO API """

from __future__ import absolute_import, division, unicode_literals

import json

import requests

from resources.lib.kodiwrapper import LOG_DEBUG, LOG_INFO
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth

try:  # Python 3
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib import quote


class UnavailableException(Exception):
    """ Is thrown when an item is unavailable. """


class Profile:
    """ Defines a profile under your account. """

    def __init__(self, key=None, product=None, name=None, gender=None, birthdate=None, color=None, color2=None):
        """
        :type key: str
        :type product: str
        :type name: str
        :type gender: str
        :type birthdate: str
        :type color: str
        :type color2: str
        """
        self.key = key
        self.product = product
        self.name = name
        self.gender = gender
        self.birthdate = birthdate
        self.color = color
        self.color2 = color2

    def __repr__(self):
        return "%r" % self.__dict__


class LiveChannel:
    """ Defines a tv channel that can be streamed live """

    def __init__(self, key=None, channel_id=None, name=None, logo=None, epg=None, geoblocked=False):
        """
        :type key: str
        :type channel_id: str
        :type name: str
        :type logo: str
        :type epg: list[LiveChannelEpg]
        :type geoblocked: bool
        """
        self.key = key
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
    """ Defines a category from the catalog """

    def __init__(self, category_id=None, title=None, content=None):
        """
        :type category_id: str
        :type title: str
        :type content: list[Union[Movie, Program, Episode]]
        """
        self.category_id = category_id
        self.title = title
        self.content = content

    def __repr__(self):
        return "%r" % self.__dict__


class Movie:
    """ Defines a Movie """

    def __init__(self, movie_id=None, name=None, description=None, year=None, cover=None, image=None, duration=None, remaining=None, geoblocked=None,
                 channel=None, legal=None, aired=None, my_list=None):
        """
        :type movie_id: str
        :type name: str
        :type description: str
        :type year: int
        :type cover: str
        :type image: str
        :type duration: int
        :type remaining: str
        :type geoblocked: bool
        :type channel: Optional[str]
        :type legal: str
        :type aired: str
        :type my_list: bool
        """
        self.movie_id = movie_id
        self.name = name
        self.description = description if description else ''
        self.year = year
        self.cover = cover
        self.image = image
        self.duration = duration
        self.remaining = remaining
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal
        self.aired = aired
        self.my_list = my_list

    def __repr__(self):
        return "%r" % self.__dict__


class Program:
    """ Defines a Program """

    def __init__(self, program_id=None, name=None, description=None, cover=None, image=None, seasons=None, geoblocked=None, channel=None, legal=None,
                 my_list=None):
        """
        :type program_id: str
        :type name: str
        :type description: str
        :type cover: str
        :type image: str
        :type seasons: dict[int, Season]
        :type geoblocked: bool
        :type channel: str
        :type legal: str
        :type my_list: bool
        """
        self.program_id = program_id
        self.name = name
        self.description = description if description else ''
        self.cover = cover
        self.image = image
        self.seasons = seasons if seasons else {}
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal
        self.my_list = my_list

    def __repr__(self):
        return "%r" % self.__dict__


class Season:
    """ Defines a Season """

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
        self.episodes = episodes if episodes else {}
        self.cover = cover
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal

    def __repr__(self):
        return "%r" % self.__dict__


class Episode:
    """ Defines an Episode """

    def __init__(self, episode_id=None, program_id=None, program_name=None, number=None, season=None, name=None, description=None, cover=None, duration=None,
                 remaining=None, geoblocked=None, channel=None, legal=None, aired=None, progress=None, watched=False):
        """
        :type episode_id: str
        :type program_id: str
        :type program_name: str
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
        :type progress: int
        :type watched: bool
        """
        import re
        self.episode_id = episode_id
        self.program_id = program_id
        self.program_name = program_name
        self.number = int(number) if number else None
        self.season = int(season) if season else None
        if number:
            self.name = re.compile('^%d. ' % number).sub('', name)  # Strip episode from name
        else:
            self.name = name
        self.description = description if description else ''
        self.cover = cover
        self.duration = int(duration) if duration else None
        self.remaining = int(remaining) if remaining is not None else None
        self.geoblocked = geoblocked
        self.channel = channel
        self.legal = legal
        self.aired = aired
        self.progress = progress
        self.watched = watched

    def __repr__(self):
        return "%r" % self.__dict__


class VtmGo:
    """ VTM GO API """
    CONTENT_TYPE_MOVIE = 'MOVIE'
    CONTENT_TYPE_PROGRAM = 'PROGRAM'
    CONTENT_TYPE_EPISODE = 'EPISODE'

    _HEADERS = {
        'x-app-version': '8',
        'x-persgroep-mobile-app': 'true',
        'x-persgroep-os': 'android',
        'x-persgroep-os-version': '23',
        'User-Agent': 'VTMGO/6.11.3 (be.vmma.vtm.zenderapp; build:11672; Android 23) okhttp/3.14.2'
    }

    def __init__(self, kodi):
        """ Initialise object
        :type kodi: resources.lib.kodiwrapper.KodiWrapper
        """
        self._kodi = kodi
        self._proxies = kodi.get_proxies()
        self._auth = VtmGoAuth(kodi)

    def _mode(self):
        """ Return the mode that should be used for API calls """
        return 'vtmgo-kids' if self.get_product() == 'VTM_GO_KIDS' else 'vtmgo'

    def get_config(self):
        """ Returns the config for the app """
        # This is currently not used
        response = self._get_url('/config')
        info = json.loads(response)

        # This contains a player.updateIntervalSeconds that could be used to notify VTM GO about the playing progress
        return info

    def get_profiles(self, products='VTM_GO,VTM_GO_KIDS'):
        """ Returns the available profiles """
        response = self._get_url('/profiles', {'products': products})
        result = json.loads(response)

        profiles = [
            Profile(
                key=profile.get('id'),
                product=profile.get('product'),
                name=profile.get('name'),
                gender=profile.get('gender'),
                birthdate=profile.get('birthDate'),
                color=profile.get('color', {}).get('start'),
                color2=profile.get('color', {}).get('end'),
            )
            for profile in result
        ]

        return profiles

    def get_recommendations(self):
        """ Returns the config for the dashboard """
        response = self._get_url('/%s/main' % self._mode())
        recommendations = json.loads(response)

        categories = []
        for cat in recommendations.get('rows', []):
            if cat.get('rowType') not in ['SWIMLANE_DEFAULT']:
                self._kodi.log('Skipping recommendation {name} with type={type}', name=cat.get('title'), type=cat.get('rowType'))
                continue

            items = []
            for item in cat.get('teasers'):
                if item.get('target', {}).get('type') == self.CONTENT_TYPE_MOVIE:
                    movie = self.get_movie(item.get('target', {}).get('id'), cache=True)
                    if movie:
                        # We have a cover from the overview that we don't have in the details
                        movie.cover = item.get('imageUrl')
                        items.append(movie)
                    else:
                        items.append(Movie(
                            movie_id=item.get('target', {}).get('id'),
                            name=item.get('title'),
                            cover=item.get('imageUrl'),
                            image=item.get('imageUrl'),
                            geoblocked=item.get('geoBlocked'),
                        ))
                elif item.get('target', {}).get('type') == self.CONTENT_TYPE_PROGRAM:
                    program = self.get_program(item.get('target', {}).get('id'), cache=True)
                    if program:
                        # We have a cover from the overview that we don't have in the details
                        program.cover = item.get('imageUrl')
                        items.append(program)
                    else:
                        items.append(Program(
                            program_id=item.get('target', {}).get('id'),
                            name=item.get('title'),
                            cover=item.get('imageUrl'),
                            image=item.get('imageUrl'),
                            geoblocked=item.get('geoBlocked'),
                        ))

            categories.append(Category(
                category_id=cat.get('id'),
                title=cat.get('title'),
                content=items,
            ))

        return categories

    def get_swimlane(self, swimlane=None):
        """ Returns the contents of My List """
        response = self._get_url('/%s/main/swimlane/%s' % (self._mode(), swimlane))

        # Result can be empty
        if not response:
            return []

        result = json.loads(response)

        items = []
        for item in result.get('teasers'):
            if item.get('target', {}).get('type') == self.CONTENT_TYPE_MOVIE:
                movie = self.get_movie(item.get('target', {}).get('id'), cache=True)
                if movie:
                    # We have a cover from the overview that we don't have in the details
                    movie.cover = item.get('imageUrl')
                    items.append(movie)
                else:
                    items.append(Movie(
                        movie_id=item.get('target', {}).get('id'),
                        name=item.get('title'),
                        geoblocked=item.get('geoBlocked'),
                        cover=item.get('imageUrl'),
                        image=item.get('imageUrl'),
                    ))

            elif item.get('target', {}).get('type') == self.CONTENT_TYPE_PROGRAM:
                program = self.get_program(item.get('target', {}).get('id'), cache=True)
                if program:
                    # We have a cover from the overview that we don't have in the details
                    program.cover = item.get('imageUrl')
                    items.append(program)
                else:
                    items.append(Program(
                        program_id=item.get('target', {}).get('id'),
                        name=item.get('title'),
                        geoblocked=item.get('geoBlocked'),
                        cover=item.get('imageUrl'),
                        image=item.get('imageUrl'),
                    ))

            elif item.get('target', {}).get('type') == self.CONTENT_TYPE_EPISODE:
                program = self.get_program(item.get('target', {}).get('programId'), cache=True)
                episode = self.get_episode_from_program(program, item.get('target', {}).get('id')) if program else None

                items.append(Episode(
                    episode_id=item.get('target', {}).get('id'),
                    program_id=item.get('target', {}).get('programId'),
                    program_name=item.get('title'),
                    name=item.get('label'),
                    description=episode.description if episode else None,
                    geoblocked=item.get('geoBlocked'),
                    cover=item.get('imageUrl'),
                    progress=item.get('playerPositionSeconds'),
                    watched=False,
                    remaining=item.get('remainingDaysAvailable'),
                ))

        return items

    def add_mylist(self, video_type, content_id):
        """ Add an item to My List """
        self._put_url('/%s/userData/myList/%s/%s' % (self._mode(), video_type, content_id))

    def del_mylist(self, video_type, content_id):
        """ Delete an item from My List """
        self._delete_url('/%s/userData/myList/%s/%s' % (self._mode(), video_type, content_id))

    def get_live_channels(self):
        """ Get a list of all the live tv channels.
        :rtype list[LiveChannel]
        """
        import dateutil.parser
        response = self._get_url('/%s/live' % self._mode())
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
                key=item.get('seoKey'),
                channel_id=item.get('channelId'),
                logo=self._parse_channel(item.get('channelLogoUrl')),
                name=item.get('name'),
                epg=epg,
            ))

        return channels

    def get_live_channel(self, key):
        """ Get a the specified live tv channel.
        :rtype LiveChannel
        """
        channels = self.get_live_channels()
        return next(c for c in channels if c.key == key)

    def get_categories(self):
        """ Get a list of all the categories.
        :rtype list[Category]
        """
        response = self._get_url('/%s/catalog/filters' % self._mode())
        info = json.loads(response)

        categories = []
        for item in info.get('catalogFilters', []):
            categories.append(Category(
                category_id=item.get('id'),
                title=item.get('title'),
            ))

        return categories

    def get_items(self, category=None, cache=False):
        """ Get a list of all the items in a category.
        :type category: str
        :type cache: bool
        :rtype list[Union[Movie, Program]]
        """
        if cache and category is None:
            # Fetch from cache if asked
            content = self._kodi.get_cache(['catalog'])
            if not content:
                return None
        else:
            # Fetch from API
            if category is None:
                response = self._get_url('/%s/catalog' % self._mode(), {'pageSize': 1000})
                info = json.loads(response)
                content = info.get('pagedTeasers', {}).get('content', [])
                self._kodi.set_cache(['catalog'], content)
            else:
                response = self._get_url('/%s/catalog' % self._mode(), {'pageSize': 1000, 'filter': quote(category)})
                info = json.loads(response)
                content = info.get('pagedTeasers', {}).get('content', [])

        items = []
        for item in content:
            if item.get('target', {}).get('type') == self.CONTENT_TYPE_MOVIE:
                movie = self.get_movie(item.get('target', {}).get('id'), cache=True)
                if movie:
                    # We have a cover from the overview that we don't have in the details
                    movie.cover = item.get('imageUrl')
                    items.append(movie)
                else:
                    items.append(Movie(
                        movie_id=item.get('target', {}).get('id'),
                        name=item.get('title'),
                        cover=item.get('imageUrl'),
                        geoblocked=item.get('geoBlocked'),
                    ))
            elif item.get('target', {}).get('type') == self.CONTENT_TYPE_PROGRAM:
                program = self.get_program(item.get('target', {}).get('id'), cache=True)
                if program:
                    # We have a cover from the overview that we don't have in the details
                    program.cover = item.get('imageUrl')
                    items.append(program)
                else:
                    items.append(Program(
                        program_id=item.get('target', {}).get('id'),
                        name=item.get('title'),
                        cover=item.get('imageUrl'),
                        geoblocked=item.get('geoBlocked'),
                    ))

        return items

    def get_movie(self, movie_id, cache=False):
        """ Get the details of the specified movie.
        :type movie_id: str
        :type cache: bool
        :rtype Movie
        """
        if cache:
            # Fetch from cache if asked
            movie = self._kodi.get_cache(['movie', movie_id])
            if not movie:
                return None
        else:
            # Fetch from API
            response = self._get_url('/%s/movies/%s' % (self._mode(), movie_id))
            info = json.loads(response)
            movie = info.get('movie', {})
            self._kodi.set_cache(['movie', movie_id], movie)

        return Movie(
            movie_id=movie.get('id'),
            name=movie.get('name'),
            description=movie.get('description'),
            duration=movie.get('durationSeconds'),
            cover=movie.get('bigPhotoUrl'),
            image=movie.get('bigPhotoUrl'),
            year=movie.get('productionYear'),
            geoblocked=movie.get('geoBlocked'),
            remaining=movie.get('remainingDaysAvailable'),
            legal=movie.get('legalIcons'),
            # aired=movie.get('broadcastTimestamp'),
            channel=self._parse_channel(movie.get('channelLogoUrl')),
        )

    def get_program(self, program_id, cache=False):
        """ Get the details of the specified program.
        :type program_id: str
        :type cache: bool
        :rtype Program
        """
        if cache:
            # Fetch from cache if asked
            program = self._kodi.get_cache(['program', program_id])
            if not program:
                return None
        else:
            # Fetch from API
            response = self._get_url('/%s/programs/%s' % (self._mode(), program_id))
            info = json.loads(response)
            program = info.get('program', {})
            self._kodi.set_cache(['program', program_id], program)

        channel = self._parse_channel(program.get('channelLogoUrl'))

        seasons = {}
        for item_season in program.get('seasons', []):
            episodes = {}

            for item_episode in item_season.get('episodes', []):
                episodes[item_episode.get('index')] = Episode(
                    episode_id=item_episode.get('id'),
                    program_id=program_id,
                    program_name=program.get('name'),
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
                    progress=item_episode.get('playerPositionSeconds', 0),
                    watched=item_episode.get('doneWatching', False),
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
            image=program.get('bigPhotoUrl'),
            geoblocked=program.get('geoBlocked'),
            seasons=seasons,
            channel=channel,
            legal=program.get('legalIcons'),
        )

    @staticmethod
    def get_episode_from_program(program, episode_id):
        """ Extract the specified episode from the program data.
        :type program: Program
        :type episode_id: str
        :rtype Episode
        """
        for season in program.seasons.values():
            for episode in season.episodes.values():
                if episode.episode_id == episode_id:
                    return episode

        return None

    def get_episode(self, episode_id):
        """ Get the details of the specified episode.
        :type episode_id: str
        :rtype Episode
        """
        response = self._get_url('/%s/play/episode/%s' % (self._mode(), episode_id))
        episode = json.loads(response)

        # TODO: episode.get('nextPlayable') contains information for Up Next

        return Episode(
            episode_id=episode.get('id'),
            name=episode.get('title'),
            cover=episode.get('posterImageUrl'),
            progress=episode.get('playerPositionSeconds'),
        )

    def do_search(self, search):
        """ Do a search in the full catalog.
        :type search: str
        :rtype list[Union[Movie, Program]]
        """
        response = self._get_url('/%s/autocomplete/?maxItems=%d&keywords=%s' % (self._mode(), 50, quote(search)))
        results = json.loads(response)

        items = []
        for item in results.get('suggestions', []):
            if item.get('type') == self.CONTENT_TYPE_MOVIE:
                movie = self.get_movie(item.get('id'), cache=True)
                if movie:
                    items.append(movie)
                else:
                    items.append(Movie(
                        movie_id=item.get('id'),
                        name=item.get('name'),
                    ))
            elif item.get('type') == self.CONTENT_TYPE_PROGRAM:
                program = self.get_program(item.get('id'), cache=True)
                if program:
                    items.append(program)
                else:
                    items.append(Program(
                        program_id=item.get('id'),
                        name=item.get('name'),
                    ))

        return items

    def get_product(self):
        """ Return the product that is currently selected. """
        profile = self._kodi.get_setting('profile')
        try:
            return profile.split(':')[1]
        except IndexError:
            return None

    @staticmethod
    def _parse_channel(url):
        """ Parse the channel logo url, and return an icon that matches resource.images.studios.white
        :type url: str
        :rtype str
        """
        if not url:
            return None

        import os.path
        # The channels id's we use in resources.lib.modules.CHANNELS neatly matches this part in the url.
        return str(os.path.basename(url).split('-')[0])

    def _get_url(self, url, params=None):
        """ Makes a GET request for the specified URL.
        :type url: str
        :rtype str
        """
        headers = self._HEADERS
        token = self._auth.get_token()
        if token:
            headers['x-dpp-jwt'] = token

        profile = self._auth.get_profile()
        if profile:
            headers['x-dpp-profile'] = profile

        self._kodi.log('Sending GET {url}...', LOG_INFO, url=url)

        response = requests.session().get('https://lfvp-api.dpgmedia.net' + url, params=params, headers=headers, proxies=self._proxies)

        self._kodi.log('Got response (status={code}): {response}', LOG_DEBUG, code=response.status_code, response=response.text)

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
        headers = self._HEADERS
        token = self._auth.get_token()
        if token:
            headers['x-dpp-jwt'] = token

        profile = self._auth.get_profile()
        if profile:
            headers['x-dpp-profile'] = profile

        self._kodi.log('Sending PUT {url}...', LOG_INFO, url=url)

        response = requests.session().put('https://api.vtmgo.be' + url, headers=headers, proxies=self._proxies)

        self._kodi.log('Got response: {response}', LOG_DEBUG, response=response.text)

        if response.status_code == 404:
            raise UnavailableException()

        if response.status_code not in [200, 204]:
            raise Exception('Error %s.' % response.status_code)

        return response.text

    def _post_url(self, url):
        """ Makes a POST request for the specified URL.
        :type url: str
        :rtype str
        """
        headers = self._HEADERS
        token = self._auth.get_token()
        if token:
            headers['x-dpp-jwt'] = token

        profile = self._auth.get_profile()
        if profile:
            headers['x-dpp-profile'] = profile

        self._kodi.log('Sending POST {url}...', LOG_INFO, url=url)

        response = requests.session().post('https://api.vtmgo.be' + url, headers=headers, proxies=self._proxies)

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
        headers = self._HEADERS
        token = self._auth.get_token()
        if token:
            headers['x-dpp-jwt'] = token

        profile = self._auth.get_profile()
        if profile:
            headers['x-dpp-profile'] = profile

        self._kodi.log('Sending DELETE {url}...', LOG_INFO, url=url)

        response = requests.session().delete('https://api.vtmgo.be' + url, headers=headers, proxies=self._proxies)

        self._kodi.log('Got response: {response}', LOG_DEBUG, response=response.text)

        if response.status_code == 404:
            raise UnavailableException()

        if response.status_code not in [200, 204]:
            raise Exception('Error %s.' % response.status_code)

        return response.text
