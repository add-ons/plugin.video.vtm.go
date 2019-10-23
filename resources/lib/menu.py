# -*- coding: utf-8 -*-
""" Menu code """

from __future__ import absolute_import, division, unicode_literals

from resources.lib.kodiwrapper import TitleItem
from resources.lib.vtmgo.vtmgo import Movie, Program, Episode, VtmGo


class Menu:
    """ Menu code """

    def __init__(self, _kodi):
        """ Initialise object """
        self._kodi = _kodi
        self.vtm_go = VtmGo(self._kodi)

    def _format_plot(self, obj):
        """ Format the plot for a item """
        plot = ''

        if hasattr(obj, 'description'):
            plot += obj.description
            plot += '\n\n'

        if hasattr(obj, 'epg'):
            if obj.epg:
                plot += self._kodi.localize(30213,  # Now
                                            start=obj.epg[0].start.strftime('%H:%M'),
                                            end=obj.epg[0].end.strftime('%H:%M'),
                                            title=obj.epg[0].title) + "\n"

            if len(obj.epg) > 1:
                plot += self._kodi.localize(30214,  # Next
                                            start=obj.epg[1].start.strftime('%H:%M'),
                                            end=obj.epg[1].end.strftime('%H:%M'),
                                            title=obj.epg[1].title) + "\n"

        # Add remaining
        if hasattr(obj, 'remaining') and obj.remaining is not None:
            if obj.remaining == 0:
                plot += '» ' + self._kodi.localize(30208) + "\n"  # Available until midnight
            elif obj.remaining == 1:
                plot += '» ' + self._kodi.localize(30209) + "\n"  # One more day remaining
            elif obj.remaining / 365 > 5:
                pass  # If it is available for more than 5 years, do not show
            elif obj.remaining / 365 > 2:
                plot += '» ' + self._kodi.localize(30210, years=int(obj.remaining / 365)) + "\n"  # X years remaining
            elif obj.remaining / 30.5 > 3:
                plot += '» ' + self._kodi.localize(30211, months=int(obj.remaining / 30.5)) + "\n"  # X months remaining
            else:
                plot += '» ' + self._kodi.localize(30212, days=obj.remaining) + "\n"  # X days remaining

        # Add geo-blocked message
        if hasattr(obj, 'geoblocked') and obj.geoblocked:
            plot += self._kodi.localize(30207)  # Geo-blocked
            plot += '\n'

        return plot.rstrip()

    def _generate_titleitem(self, item, progress=False):
        """ Generate a TitleItem based on a Movie, Program or Episode.
        :type item: Union[Movie, Program, Episode]
        :rtype TitleItem
        """
        art_dict = {
            'thumb': item.cover,
        }
        info_dict = {
            'title': item.name,
            'plot': item.description,
        }
        prop_dict = {}

        #
        # Movie
        #
        if isinstance(item, Movie):
            if item.my_list:
                context_menu = [(
                    self._kodi.localize(30051),  # Remove from My List
                    'XBMC.Container.Update(%s)' %
                    self._kodi.url_for('mylist_del', kids=self._kodi.kids_mode(), video_type=self.vtm_go.CONTENT_TYPE_MOVIE, content_id=item.movie_id)
                )]
            else:
                context_menu = [(
                    self._kodi.localize(30050),  # Add to My List
                    'XBMC.Container.Update(%s)' %
                    self._kodi.url_for('mylist_add', kids=self._kodi.kids_mode(), video_type=self.vtm_go.CONTENT_TYPE_MOVIE, content_id=item.movie_id)
                )]

            info_dict.update({
                'mediatype': 'movie',
            })

            # Get movie details from cache
            movie = self.vtm_go.get_movie(item.movie_id, only_cache=True)
            if movie:
                art_dict.update({
                    'fanart': movie.cover,
                })
                info_dict.update({
                    'plot': self._format_plot(movie),
                    'duration': movie.duration,
                    'year': movie.year,
                    'aired': movie.aired,
                    'mpaa': ', '.join(movie.legal) if hasattr(movie, 'legal') and movie.legal else self._kodi.localize(30216),
                })

            return TitleItem(title=item.name,
                             path=self._kodi.url_for('play', category='movies', item=item.movie_id),
                             art_dict=art_dict,
                             info_dict=info_dict,
                             stream_dict={
                                 'codec': 'h264',
                                 'height': 1080,
                                 'width': 1920,
                             },
                             context_menu=context_menu,
                             is_playable=True)

        #
        # Program
        #
        if isinstance(item, Program):
            if item.my_list:
                context_menu = [(
                    self._kodi.localize(30051),  # Remove from My List
                    'XBMC.Container.Update(%s)' %
                    self._kodi.url_for('mylist_del', kids=self._kodi.kids_mode(), video_type=self.vtm_go.CONTENT_TYPE_PROGRAM, content_id=item.program_id)
                )]
            else:
                context_menu = [(
                    self._kodi.localize(30050),  # Add to My List
                    'XBMC.Container.Update(%s)' %
                    self._kodi.url_for('mylist_add', kids=self._kodi.kids_mode(), video_type=self.vtm_go.CONTENT_TYPE_PROGRAM, content_id=item.program_id)
                )]

            info_dict.update({
                'mediatype': None,
            })

            # Get program details from cache
            program = self.vtm_go.get_program(item.program_id, only_cache=True)
            if program:
                art_dict.update({
                    'fanart': program.cover,
                    'banner': item.cover,
                })
                info_dict.update({
                    'title': program.name,
                    'plot': self._format_plot(program),
                    'mpaa': ', '.join(program.legal) if hasattr(program, 'legal') and program.legal else self._kodi.localize(30216),
                    'season': len(program.seasons),
                })

            return TitleItem(title=item.name,
                             path=self._kodi.url_for('show_program', program=item.program_id),
                             art_dict=art_dict,
                             info_dict=info_dict,
                             context_menu=context_menu)

        #
        # Episode
        #
        if isinstance(item, Episode):
            context_menu = [(
                self._kodi.localize(30052),  # Go to Program
                'XBMC.Container.Update(%s)' %
                self._kodi.url_for('show_program', program=item.program_id)
            )]

            info_dict.update({
                'tvshowtitle': item.program_name,
                'title': item.name,
                'plot': self._format_plot(item),
                'duration': item.duration,
                'season': item.season,
                'episode': item.number,
                'mediatype': 'episode',
                'set': item.program_name,
                'studio': item.channel,
                'aired': item.aired,
                'mpaa': ', '.join(item.legal) if hasattr(item, 'legal') and item.legal else self._kodi.localize(30216),
            })

            if progress and item.watched:
                info_dict.update({
                    'playcount': 1,
                })

            stream_dict = {
                'codec': 'h264',
                'duration': item.duration,
                'height': 1080,
                'width': 1920,
            }

            # Get program and episode details from cache
            program = self.vtm_go.get_program(item.program_id, only_cache=True)
            if program:
                episode = self.vtm_go.get_episode_from_program(program, item.episode_id)
                if episode:
                    art_dict.update({
                        'fanart': episode.cover,
                        'banner': episode.cover,
                    })
                    info_dict.update({
                        'tvshowtitle': program.name,
                        'title': episode.name,
                        'plot': self._format_plot(episode),
                        'duration': episode.duration,
                        'season': episode.season,
                        'episode': episode.number,
                        'set': program.name,
                        'studio': episode.channel,
                        'aired': episode.aired,
                        'mpaa': ', '.join(episode.legal) if hasattr(episode, 'legal') and episode.legal else self._kodi.localize(30216),
                    })

                    if progress and item.watched:
                        info_dict.update({
                            'playcount': 1,
                        })

                    stream_dict.update({
                        'duration': episode.duration,
                    })

            # Add progress info
            if progress and not item.watched and item.progress:
                prop_dict.update({
                    'ResumeTime': item.progress,
                    'TotalTime': item.progress + 1,
                })

            return TitleItem(title=info_dict['title'],
                             path=self._kodi.url_for('play', category='episodes', item=item.episode_id),
                             art_dict=art_dict,
                             info_dict=info_dict,
                             stream_dict=stream_dict,
                             prop_dict=prop_dict,
                             context_menu=context_menu,
                             is_playable=True)

        raise Exception('Unknown video_type')
