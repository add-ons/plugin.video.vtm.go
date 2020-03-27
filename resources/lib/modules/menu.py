# -*- coding: utf-8 -*-
""" Menu module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib.kodiutils import KodiUtils
from resources.lib.modules import CHANNELS, TitleItem
from resources.lib.modules.authentication import Authentication
from resources.lib.vtmgo.vtmgo import Movie, Program, Episode, VtmGo, CONTENT_TYPE_MOVIE, CONTENT_TYPE_PROGRAM

_LOGGER = logging.getLogger('menu')


class Menu:
    """ Menu code """

    def __init__(self, router):
        """ Initialise object """
        self._router = router  # type: callable
        self._vtm_go = VtmGo()

    def show_mainmenu(self):
        """ Show the main menu """
        listing = []
        listing.append(TitleItem(
            title=KodiUtils.localize(30001),  # A-Z
            path=self._router('show_catalog_all'),
            art_dict=dict(
                icon='DefaultMovieTitle.png',
                fanart=KodiUtils.get_addon_info('fanart'),
            ),
            info_dict=dict(
                plot=KodiUtils.localize(30002),
            ),
        ))
        listing.append(TitleItem(
            title=KodiUtils.localize(30003),  # Catalogue
            path=self._router('show_catalog'),
            art_dict=dict(
                icon='DefaultGenre.png',
                fanart=KodiUtils.get_addon_info('fanart'),
            ),
            info_dict=dict(
                plot=KodiUtils.localize(30004),
            ),
        ))
        listing.append(TitleItem(
            title=KodiUtils.localize(30007),  # TV Channels
            path=self._router('show_channels'),
            art_dict=dict(
                icon='DefaultAddonPVRClient.png',
                fanart=KodiUtils.get_addon_info('fanart'),
            ),
            info_dict=dict(
                plot=KodiUtils.localize(30008),
            ),
        ))

        if KodiUtils.get_setting_bool('interface_show_recommendations'):
            listing.append(TitleItem(
                title=KodiUtils.localize(30015),  # Recommendations
                path=self._router('show_recommendations'),
                art_dict=dict(
                    icon='DefaultFavourites.png',
                    fanart=KodiUtils.get_addon_info('fanart'),
                ),
                info_dict=dict(
                    plot=KodiUtils.localize(30016),
                ),
            ))

        if KodiUtils.get_setting_bool('interface_show_mylist') and Authentication.has_credentials():
            listing.append(TitleItem(
                title=KodiUtils.localize(30017),  # My List
                path=self._router('show_mylist'),
                art_dict=dict(
                    icon='DefaultPlaylist.png',
                    fanart=KodiUtils.get_addon_info('fanart'),
                ),
                info_dict=dict(
                    plot=KodiUtils.localize(30018),
                ),
            ))

        if KodiUtils.get_setting_bool('interface_show_continuewatching') and Authentication.has_credentials():
            listing.append(TitleItem(
                title=KodiUtils.localize(30019),  # Continue watching
                path=self._router('show_continuewatching'),
                art_dict=dict(
                    icon='DefaultInProgressShows.png',
                    fanart=KodiUtils.get_addon_info('fanart'),
                ),
                info_dict=dict(
                    plot=KodiUtils.localize(30020),
                ),
            ))

        listing.append(TitleItem(
            title=KodiUtils.localize(30009),  # Search
            path=self._router('show_search'),
            art_dict=dict(
                icon='DefaultAddonsSearch.png',
                fanart=KodiUtils.get_addon_info('fanart'),
            ),
            info_dict=dict(
                plot=KodiUtils.localize(30010),
            ),
        ))

        KodiUtils.show_listing(listing, sort=['unsorted'])

    @staticmethod
    def format_plot(obj):
        """ Format the plot for a item
        :type obj: object
        :rtype str
        """
        plot = ''

        if hasattr(obj, 'epg'):
            if obj.epg:
                plot += KodiUtils.localize(30213,  # Now
                                           start=obj.epg[0].start.strftime('%H:%M'),
                                           end=obj.epg[0].end.strftime('%H:%M'),
                                           title=obj.epg[0].title) + "\n"

            if len(obj.epg) > 1:
                plot += KodiUtils.localize(30214,  # Next
                                           start=obj.epg[1].start.strftime('%H:%M'),
                                           end=obj.epg[1].end.strftime('%H:%M'),
                                           title=obj.epg[1].title) + "\n"
            plot += '\n'

        # Add remaining
        if hasattr(obj, 'remaining') and obj.remaining is not None:
            if obj.remaining == 0:
                plot += '» ' + KodiUtils.localize(30208) + "\n"  # Available until midnight
            elif obj.remaining == 1:
                plot += '» ' + KodiUtils.localize(30209) + "\n"  # One more day remaining
            elif obj.remaining / 365 > 5:
                pass  # If it is available for more than 5 years, do not show
            elif obj.remaining / 365 > 2:
                plot += '» ' + KodiUtils.localize(30210, years=int(obj.remaining / 365)) + "\n"  # X years remaining
            elif obj.remaining / 30.5 > 3:
                plot += '» ' + KodiUtils.localize(30211, months=int(obj.remaining / 30.5)) + "\n"  # X months remaining
            else:
                plot += '» ' + KodiUtils.localize(30212, days=obj.remaining) + "\n"  # X days remaining
            plot += '\n'

        # Add geo-blocked message
        if hasattr(obj, 'geoblocked') and obj.geoblocked:
            plot += KodiUtils.localize(30207)  # Geo-blocked
            plot += '\n'

        if hasattr(obj, 'description'):
            plot += obj.description
            plot += '\n\n'

        return plot.rstrip()

    def generate_titleitem(self, item, progress=False):
        """ Generate a TitleItem based on a Movie, Program or Episode.
        :type item: Union[Movie, Program, Episode]
        :type progress: bool
        :rtype TitleItem
        """
        art_dict = {
            'thumb': item.cover,
            'cover': item.cover,
        }
        info_dict = {
            'title': item.name,
            'plot': self.format_plot(item),
            'studio': CHANNELS.get(item.channel, {}).get('studio_icon'),
            'mpaa': ', '.join(item.legal) if hasattr(item, 'legal') and item.legal else KodiUtils.localize(30216),  # All ages
        }
        prop_dict = {}

        #
        # Movie
        #
        if isinstance(item, Movie):
            if item.my_list:
                context_menu = [(
                    KodiUtils.localize(30101),  # Remove from My List
                    'Container.Update(%s)' %
                    self._router('mylist_del', video_type=CONTENT_TYPE_MOVIE, content_id=item.movie_id)
                )]
            else:
                context_menu = [(
                    KodiUtils.localize(30100),  # Add to My List
                    'Container.Update(%s)' %
                    self._router('mylist_add', video_type=CONTENT_TYPE_MOVIE, content_id=item.movie_id)
                )]

            art_dict.update({
                'fanart': item.image,
            })
            info_dict.update({
                'mediatype': 'movie',
                'duration': item.duration,
                'year': item.year,
                'aired': item.aired,
            })
            stream_dict = {
                'codec': 'h264',
                'duration': item.duration,
                'height': 1080,
                'width': 1920,
            }

            return TitleItem(
                title=item.name,
                path=self._router('play', category='movies', item=item.movie_id),
                art_dict=art_dict,
                info_dict=info_dict,
                stream_dict=stream_dict,
                context_menu=context_menu,
                is_playable=True,
            )

        #
        # Program
        #
        if isinstance(item, Program):
            if item.my_list:
                context_menu = [(
                    KodiUtils.localize(30101),  # Remove from My List
                    'Container.Update(%s)' %
                    self._router('mylist_del', video_type=CONTENT_TYPE_PROGRAM, content_id=item.program_id)
                )]
            else:
                context_menu = [(
                    KodiUtils.localize(30100),  # Add to My List
                    'Container.Update(%s)' %
                    self._router('mylist_add', video_type=CONTENT_TYPE_PROGRAM, content_id=item.program_id)
                )]

            art_dict.update({
                'fanart': item.image,
            })
            info_dict.update({
                'mediatype': None,
                'season': len(item.seasons),
            })

            return TitleItem(
                title=item.name,
                path=self._router('show_catalog_program', program=item.program_id),
                art_dict=art_dict,
                info_dict=info_dict,
                context_menu=context_menu,
            )

        #
        # Episode
        #
        if isinstance(item, Episode):
            context_menu = []
            if item.program_id:
                context_menu = [(
                    KodiUtils.localize(30102),  # Go to Program
                    'Container.Update(%s)' %
                    self._router('show_catalog_program', program=item.program_id)
                )]

            art_dict.update({
                'fanart': item.cover,
            })
            info_dict.update({
                'mediatype': 'episode',
                'tvshowtitle': item.program_name,
                'duration': item.duration,
                'season': item.season,
                'episode': item.number,
                'set': item.program_name,
                'aired': item.aired,
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

            # Add progress info
            if progress and not item.watched and item.progress:
                prop_dict.update({
                    'ResumeTime': item.progress,
                    'TotalTime': item.progress + 1,
                })

            return TitleItem(
                title=info_dict['title'],
                path=self._router('play', category='episodes', item=item.episode_id),
                art_dict=art_dict,
                info_dict=info_dict,
                stream_dict=stream_dict,
                prop_dict=prop_dict,
                context_menu=context_menu,
                is_playable=True,
            )

        raise Exception('Unknown video_type')
