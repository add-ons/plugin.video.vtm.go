# -*- coding: utf-8 -*-
""" Addon code """
# pylint: disable=too-many-lines

from __future__ import absolute_import, division, unicode_literals

import routing

from resources.lib import GeoblockedException, UnavailableException
from resources.lib.kodiwrapper import KodiWrapper, TitleItem
from resources.lib.vtmgo.vtmgo import VtmGo, Episode, Movie, Program
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth, InvalidLoginException
from resources.lib.vtmgo.vtmgoepg import VtmGoEpg
from resources.lib.vtmgo.vtmgostream import VtmGoStream

routing = routing.Plugin()
kodi = KodiWrapper(routing=routing)
vtm_go = VtmGo(kodi)


@routing.route('/')
def show_index():
    """ Show the main menu """
    kids = kodi.kids_mode()

    listing = []
    listing.extend([
        TitleItem(title=kodi.localize(30001),  # A-Z
                  path=routing.url_for(show_catalog_category, kids=kids, category='all'),
                  art_dict=dict(
                      icon='DefaultMovieTitle.png'
                  ),
                  info_dict=dict(
                      plot=kodi.localize(30002),
                  )),
        TitleItem(title=kodi.localize(30003),  # Catalogue
                  path=routing.url_for(show_catalog, kids=kids),
                  art_dict=dict(
                      icon='DefaultGenre.png'
                  ),
                  info_dict=dict(
                      plot=kodi.localize(30004),
                  )),
        TitleItem(title=kodi.localize(30005),  # Live TV
                  path=routing.url_for(show_livetv, kids=kids),
                  art_dict=dict(
                      icon='DefaultAddonPVRClient.png'
                  ),
                  info_dict=dict(
                      plot=kodi.localize(30006),
                  )),
        TitleItem(title=kodi.localize(30013),  # TV Guide
                  path=routing.url_for(show_tvguide, kids=kids),
                  art_dict={
                      'icon': 'DefaultAddonTvInfo.png'
                  },
                  info_dict={
                      'plot': kodi.localize(30014),
                  }),
        TitleItem(title=kodi.localize(30015),  # Recommendations
                  path=routing.url_for(show_recommendations, kids=kids),
                  art_dict={
                      'icon': 'DefaultFavourites.png'
                  },
                  info_dict={
                      'plot': kodi.localize(30016),
                  }),
        TitleItem(title=kodi.localize(30017),  # My List
                  path=routing.url_for(show_mylist, kids=kids),
                  art_dict={
                      'icon': 'DefaultPlaylist.png'
                  },
                  info_dict={
                      'plot': kodi.localize(30018),
                  }),
        # TitleItem(title=kodi.localize(30019),  # Continue watching
        #           path=routing.url_for(show_continuewatching, kids=kids),
        #           art_dict={
        #               'icon': 'DefaultInProgressShows.png'
        #           },
        #           info_dict={
        #               'plot': kodi.localize(30020),
        #           }),
    ])

    # Only provide YouTube option when plugin.video.youtube is available
    if kodi.get_cond_visibility('System.HasAddon(plugin.video.youtube)') != 0:
        listing.append(
            TitleItem(title=kodi.localize(30007),  # YouTube
                      path=routing.url_for(show_youtube, kids=kids),
                      art_dict=dict(
                          icon='DefaultTags.png'
                      ),
                      info_dict=dict(
                          plot=kodi.localize(30008),
                      ))
        )

    listing.extend([
        TitleItem(title=kodi.localize(30009),  # Search
                  path=routing.url_for(show_search, kids=kids),
                  art_dict=dict(
                      icon='DefaultAddonsSearch.png'
                  ),
                  info_dict=dict(
                      plot=kodi.localize(30010),
                  )),
    ])

    if not kids:
        listing.append(
            TitleItem(title=kodi.localize(30011),  # Kids Zone
                      path=routing.url_for(show_index, kids=True),
                      art_dict=dict(
                          icon='DefaultUser.png'
                      ),
                      info_dict=dict(
                          plot=kodi.localize(30012),
                      ))
        )

    kodi.show_listing(listing)


@routing.route('/check-credentials')
def check_credentials():
    """ Check credentials (called from settings) """
    try:
        auth = VtmGoAuth(kodi)
        auth.clear_token()
        auth.get_token()
        kodi.show_ok_dialog(message=kodi.localize(30202))  # Credentials are correct!

    except InvalidLoginException:
        kodi.show_ok_dialog(message=kodi.localize(30203))  # Your credentials are not valid!

    kodi.open_settings()


@routing.route('/metadata/update')
def metadata_update(delay=10):
    """ Update the metadata for the listings (called from settings) """
    import xbmc

    progress = kodi.show_progress(message=kodi.localize(30715))

    # Fetch all items from the catalogue
    items = vtm_go.get_items('all')
    count = len(items)

    # Loop over all of them and download the metadata
    for index, item in enumerate(items):
        # Update the items
        if isinstance(item, Movie):
            if not vtm_go.get_movie(item.movie_id, only_cache=True):
                vtm_go.get_movie(item.movie_id)
                xbmc.sleep(delay)
        elif isinstance(item, Program):
            if not vtm_go.get_program(item.program_id, only_cache=True):
                vtm_go.get_program(item.program_id)
                xbmc.sleep(delay)

        # Upgrade the progress bar
        progress.update(int(((index + 1) / count) * 100), kodi.localize(30716, index=index + 1, total=count))

        # Allow to cancel this operation
        if progress.iscanceled():
            break

    # Close the progress dialog
    progress.close()

    # Update last updated
    from time import time
    kodi.set_setting('metadata_last_updated', str(int(time())))


@routing.route('/metadata/clean')
def metadata_clean():
    """ Clear metadata (called from settings) """
    kodi.invalidate_cache()
    kodi.show_ok_dialog(message=kodi.localize(30714))  # Local metadata is cleared.


@routing.route('/livetv')
def show_livetv():
    """ Shows Live TV channels """
    try:
        channels = vtm_go.get_live_channels()
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    from . import CHANNEL_MAPPING

    listing = []
    for channel in channels:
        if CHANNEL_MAPPING.get(channel.name):
            # Lookup the high resolution logo based on the channel name
            icon = '{path}/resources/logos/{logo}-white.png'.format(path=kodi.get_addon_path(), logo=CHANNEL_MAPPING.get(channel.name))
            fanart = '{path}/resources/logos/{logo}.png'.format(path=kodi.get_addon_path(), logo=CHANNEL_MAPPING.get(channel.name))
        else:
            # Fallback to the default (lower resolution) logo
            icon = channel.logo
            fanart = channel.logo

        title = channel.name
        if channel.epg:
            title += '[COLOR gray] | {title}[/COLOR]'.format(title=channel.epg[0].title)

        listing.append(
            TitleItem(title=title,
                      path=routing.url_for(play, category='channels', item=channel.channel_id) + '?.pvr',
                      art_dict={
                          'icon': icon,
                          'thumb': icon,
                          'fanart': fanart,
                      },
                      info_dict={
                          'plot': _format_plot(channel),
                          'playcount': 0,
                          'mediatype': 'video',
                      },
                      stream_dict={
                          'codec': 'h264',
                          'height': 1080,
                          'width': 1920,
                      },
                      is_playable=True),
        )

    kodi.show_listing(listing, 30005)


@routing.route('/tvguide')
def show_tvguide():
    """ Shows the TV guide """
    kids = kodi.kids_mode()

    from . import CHANNELS

    listing = []
    for entry in CHANNELS:
        # Skip non-kids channels when we are in kids mode.
        if kids and entry.get('kids') is False:
            continue

        # Lookup the high resolution logo based on the channel name
        icon = '{path}/resources/logos/{logo}-white.png'.format(path=kodi.get_addon_path(), logo=entry.get('logo'))
        fanart = '{path}/resources/logos/{logo}.png'.format(path=kodi.get_addon_path(), logo=entry.get('logo'))

        listing.append(
            TitleItem(title=entry.get('label'),
                      path=routing.url_for(show_tvguide_channel, channel=entry.get('key')),
                      art_dict={
                          'icon': icon,
                          'thumb': icon,
                          'fanart': fanart,
                      },
                      info_dict={
                          'plot': kodi.localize(30215, channel=entry.get('label')),
                      })
        )

    kodi.show_listing(listing, 30013)


@routing.route('/tvguide/<channel>')
def show_tvguide_channel(channel):
    """ Shows the dates in the tv guide """
    listing = []
    for day in VtmGoEpg(kodi).get_dates('%A %d %B %Y'):
        if day.get('highlight'):
            title = '[B]{title}[/B]'.format(title=day.get('title'))
        else:
            title = day.get('title')

        listing.append(
            TitleItem(title=title,
                      path=routing.url_for(show_tvguide_detail, channel=channel, date=day.get('date')),
                      art_dict={
                          'icon': 'DefaultYear.png',
                          'thumb': 'DefaultYear.png',
                      },
                      info_dict={
                          'plot': None,
                      })
        )

    kodi.show_listing(listing, 30013, content='files')


@routing.route('/tvguide/<channel>/<date>')
def show_tvguide_detail(channel=None, date=None):
    """ Shows the programs of a specific date in the tv guide """
    try:
        _vtmGoEpg = VtmGoEpg(kodi)
        epg = _vtmGoEpg.get_epg(channel=channel, date=date)
    except UnavailableException as ex:
        kodi.show_notification(message=str(ex))
        kodi.end_of_directory()
        return

    listing = []
    for broadcast in epg.broadcasts:
        if broadcast.playable_type == 'episodes':
            context_menu = [(
                kodi.localize(30052),  # Go to Program
                'XBMC.Container.Update(%s)' %
                routing.url_for(show_program_from_epg, program=broadcast.uuid)
            )]
        else:
            context_menu = None

        title = '{time} - {title}{live}'.format(
            time=broadcast.time.strftime('%H:%M'),
            title=broadcast.title,
            live=' [I](LIVE)[/I]' if broadcast.live else ''
        )

        if broadcast.airing:
            title = '[B]{title}[/B]'.format(title=title)

        if broadcast.title != 'Geen Uitzending':
            path = routing.url_for(play_epg, channel=channel, program_type=broadcast.playable_type, epg_id=broadcast.uuid)
            is_playable = True
        else:
            path = None
            is_playable = False
            title = '[COLOR gray]' + title + '[/COLOR]'

        listing.append(
            TitleItem(title=title,
                      path=path,
                      art_dict={
                          'icon': broadcast.image,
                          'thumb': broadcast.image,
                      },
                      info_dict={
                          'title': title,
                          'plot': broadcast.description,
                          'duration': broadcast.duration,
                          'mediatype': 'video',
                      },
                      stream_dict={
                          'duration': broadcast.duration,
                          'codec': 'h264',
                          'height': 1080,
                          'width': 1920,
                      },
                      context_menu=context_menu,
                      is_playable=is_playable)
        )

    kodi.show_listing(listing, 30013, content='episodes')


@routing.route('/recommendations')
def show_recommendations():
    """ Show the recommendations """
    try:
        recommendations = vtm_go.get_recommendations()
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for cat in recommendations:
        listing.append(
            TitleItem(title=cat.title,
                      path=routing.url_for(show_recommendations_category, kids=kodi.kids_mode(), category=cat.category_id),
                      info_dict={
                          'plot': '[B]{category}[/B]'.format(category=cat.title),
                      })
        )

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30015, content='files')


@routing.route('/recommendations/<category>')
def show_recommendations_category(category):
    """ Show the items in a recommendations category """
    try:
        recommendations = vtm_go.get_recommendations()
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for cat in recommendations:
        # Only show the requested category
        if cat.category_id != category:
            continue

        for item in cat.content:
            listing.append(_generate_titleitem(item))

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30015, content='tvshows')


@routing.route('/mylist')
def show_mylist():
    """ Show the items in "My List" """
    try:
        mylist = vtm_go.get_swimlane('my-list')
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for item in mylist:
        item.my_list = True
        listing.append(_generate_titleitem(item))

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30017, content='tvshows')


@routing.route('/mylist/add/<video_type>/<content_id>')
def mylist_add(video_type, content_id):
    """ Add an item to "My List" """
    vtm_go.add_mylist(video_type, content_id)
    kodi.end_of_directory()


@routing.route('/mylist/del/<video_type>/<content_id>')
def mylist_del(video_type, content_id):
    """ Remove an item from "My List" """
    vtm_go.del_mylist(video_type, content_id)
    kodi.end_of_directory()
    kodi.container_refresh()


@routing.route('/continuewatching')
def show_continuewatching():
    """ Show the items in "Continue Watching" """
    try:
        mylist = vtm_go.get_swimlane('continue-watching')
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for item in mylist:
        titleitem = _generate_titleitem(item, progress=True)

        # Add Program Name to title since this list contains episodes from multiple programs
        title = '%s - %s' % (titleitem.info_dict.get('tvshowtitle'), titleitem.info_dict.get('title'))
        titleitem.title = title
        titleitem.info_dict['title'] = title

        listing.append(titleitem)

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30019, content='episodes', sort='label')


@routing.route('/catalog')
def show_catalog():
    """ Show the catalog """
    try:
        categories = vtm_go.get_categories()
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for cat in categories:
        listing.append(
            TitleItem(title=cat.title,
                      path=routing.url_for(show_catalog_category, kids=kodi.kids_mode(), category=cat.category_id),
                      info_dict={
                          'plot': '[B]{category}[/B]'.format(category=cat.title),
                      })
        )

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30003, content='files')


@routing.route('/catalog/<category>')
def show_catalog_category(category):
    """ Show a category in the catalog """
    try:
        items = vtm_go.get_items(category)
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for item in items:
        listing.append(_generate_titleitem(item))

    # Sort items by label, but don't put folders at the top.
    # Used for A-Z listing or when movies and episodes are mixed.
    kodi.show_listing(listing, 30003, content='movies' if category == 'films' else 'tvshows', sort='label')


@routing.route('/program-epg/<program>')
def show_program_from_epg(program):
    """ Play a program based on the channel and information from the EPG. """
    _vtmGoEpg = VtmGoEpg(kodi)
    details = _vtmGoEpg.get_details(channel='vtm', program_type='episodes', epg_id=program)
    if not details:
        kodi.show_ok_dialog(heading=kodi.localize(30711), message=kodi.localize(30713))  # The requested video was not found in the guide.
        return

    show_program(details.program_uuid)


@routing.route('/program/<program>')
def show_program(program):
    """ Show a program from the catalog """
    try:
        program_obj = vtm_go.get_program(program)
    except UnavailableException:
        kodi.show_notification(message=kodi.localize(30717))  # This program is not available in the VTM GO catalogue.
        kodi.end_of_directory()
        return

    listing = []

    # Add an '* All seasons' entry when configured in Kodi
    if kodi.get_global_setting('videolibrary.showallitems') is True:
        listing.append(
            TitleItem(title='* %s' % kodi.localize(30204),  # * All seasons
                      path=routing.url_for(show_program_season, program=program, season='all'),
                      art_dict={
                          'thumb': program_obj.cover,
                          'fanart': program_obj.cover,
                      },
                      info_dict={
                          'tvshowtitle': program_obj.name,
                          'title': kodi.localize(30204),  # All seasons
                          'tagline': program_obj.description,
                          'set': program_obj.name,
                          'mpaa': ', '.join(program_obj.legal) if hasattr(program_obj, 'legal') and program_obj.legal else kodi.localize(30216),
                      })
        )

    # Add the seasons
    for s in program_obj.seasons.values():
        listing.append(
            TitleItem(title=kodi.localize(30205, season=s.number),  # Season X
                      path=routing.url_for(show_program_season, program=program, season=s.number),
                      art_dict={
                          'thumb': s.cover,
                          'fanart': program_obj.cover,
                      },
                      info_dict={
                          'tvshowtitle': program_obj.name,
                          'title': kodi.localize(30205, season=s.number),
                          'tagline': program_obj.description,
                          'set': program_obj.name,
                          'mpaa': ', '.join(program_obj.legal) if hasattr(program_obj, 'legal') and program_obj.legal else kodi.localize(30216),
                      })
        )

    # Sort by label. Some programs return seasons unordered.
    kodi.show_listing(listing, 30003, content='tvshows', sort='label')


@routing.route('/program/<program>/<season>')
def show_program_season(program, season):
    """ Show a program from the catalog """
    try:
        program_obj = vtm_go.get_program(program)
    except UnavailableException:
        kodi.show_notification(message=kodi.localize(30717))  # This program is not available in the VTM GO catalogue.
        kodi.end_of_directory()
        return

    if season == 'all':
        # Show all seasons
        seasons = program_obj.seasons.values()
    else:
        # Show the season that was selected
        seasons = [program_obj.seasons[int(season)]]

    listing = []
    for s in seasons:
        for episode in s.episodes.values():
            listing.append(_generate_titleitem(episode))

    # Sort by episode number by default. Takes seasons into account.
    kodi.show_listing(listing, 30003, content='episodes', sort='episode')


@routing.route('/youtube')
def show_youtube():
    """ Shows the Youtube channel overview """
    kids = kodi.kids_mode()

    listing = []
    from resources.lib import YOUTUBE
    for entry in YOUTUBE:
        # Skip non-kids channels when we are in kids mode.
        if kids and entry.get('kids') is False:
            continue

        # Lookup the high resolution logo based on the channel name
        icon = '{path}/resources/logos/{logo}-white.png'.format(path=kodi.get_addon_path(), logo=entry.get('logo'))
        fanart = '{path}/resources/logos/{logo}.png'.format(path=kodi.get_addon_path(), logo=entry.get('logo'))

        listing.append(
            TitleItem(title=entry.get('label'),
                      path=entry.get('path'),
                      art_dict={
                          'icon': icon,
                          'thumb': icon,
                          'fanart': fanart,
                      },
                      info_dict={
                          'plot': kodi.localize(30206, label=entry.get('label')),
                          'studio': entry.get('studio'),
                      })
        )

    # Sort by default like in our dict.
    kodi.show_listing(listing, 30007)


@routing.route('/search')
@routing.route('/search/<query>')
def show_search(query=None):
    """ Shows the search dialog """
    if not query:
        # Ask for query
        query = kodi.get_search_string(heading=kodi.localize(30009))
        if not query:
            kodi.end_of_directory()
            return

    # Do search
    try:
        items = vtm_go.do_search(query)
    except Exception as ex:  # pylint: disable=broad-except
        kodi.show_notification(message=str(ex))
        kodi.end_of_directory()
        return

    # Display results
    listing = []
    for item in items:
        listing.append(_generate_titleitem(item))

    # Sort like we get our results back.
    kodi.show_listing(listing, 30009, content='tvshows')


def _generate_titleitem(item, progress=False):
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
                kodi.localize(30051),  # Remove from My List
                'XBMC.Container.Update(%s)' %
                routing.url_for(mylist_del, kids=kodi.kids_mode(), video_type=vtm_go.CONTENT_TYPE_MOVIE, content_id=item.movie_id)
            )]
        else:
            context_menu = [(
                kodi.localize(30050),  # Add to My List
                'XBMC.Container.Update(%s)' %
                routing.url_for(mylist_add, kids=kodi.kids_mode(), video_type=vtm_go.CONTENT_TYPE_MOVIE, content_id=item.movie_id)
            )]

        info_dict.update({
            'mediatype': 'movie',
        })

        # Get movie details from cache
        movie = vtm_go.get_movie(item.movie_id, only_cache=True)
        if movie:
            art_dict.update({
                'fanart': movie.cover,
            })
            info_dict.update({
                'plot': _format_plot(movie),
                'duration': movie.duration,
                'year': movie.year,
                'aired': movie.aired,
                'mpaa': ', '.join(movie.legal) if hasattr(movie, 'legal') and movie.legal else kodi.localize(30216),
            })

        return TitleItem(title=item.name,
                         path=routing.url_for(play, category='movies', item=item.movie_id),
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
                kodi.localize(30051),  # Remove from My List
                'XBMC.Container.Update(%s)' %
                routing.url_for(mylist_del, kids=kodi.kids_mode(), video_type=vtm_go.CONTENT_TYPE_PROGRAM, content_id=item.program_id)
            )]
        else:
            context_menu = [(
                kodi.localize(30050),  # Add to My List
                'XBMC.Container.Update(%s)' %
                routing.url_for(mylist_add, kids=kodi.kids_mode(), video_type=vtm_go.CONTENT_TYPE_PROGRAM, content_id=item.program_id)
            )]

        info_dict.update({
            'mediatype': None,
        })

        # Get program details from cache
        program = vtm_go.get_program(item.program_id, only_cache=True)
        if program:
            art_dict.update({
                'fanart': program.cover,
                'banner': item.cover,
            })
            info_dict.update({
                'title': program.name,
                'plot': _format_plot(program),
                'mpaa': ', '.join(program.legal) if hasattr(program, 'legal') and program.legal else kodi.localize(30216),
                'season': len(program.seasons),
            })

        return TitleItem(title=item.name,
                         path=routing.url_for(show_program, program=item.program_id),
                         art_dict=art_dict,
                         info_dict=info_dict,
                         context_menu=context_menu)

    #
    # Episode
    #
    if isinstance(item, Episode):
        context_menu = [(
            kodi.localize(30052),  # Go to Program
            'XBMC.Container.Update(%s)' %
            routing.url_for(show_program, program=item.program_id)
        )]

        info_dict.update({
            'tvshowtitle': item.program_name,
            'title': item.name,
            'plot': _format_plot(item),
            'duration': item.duration,
            'season': item.season,
            'episode': item.number,
            'mediatype': 'episode',
            'set': item.program_name,
            'studio': item.channel,
            'aired': item.aired,
            'mpaa': ', '.join(item.legal) if hasattr(item, 'legal') and item.legal else kodi.localize(30216),
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
        program = vtm_go.get_program(item.program_id, only_cache=True)
        if program:
            episode = vtm_go.get_episode_from_program(program, item.episode_id)
            if episode:
                art_dict.update({
                    'fanart': episode.cover,
                    'banner': episode.cover,
                })
                info_dict.update({
                    'tvshowtitle': program.name,
                    'title': episode.name,
                    'plot': _format_plot(episode),
                    'duration': episode.duration,
                    'season': episode.season,
                    'episode': episode.number,
                    'set': program.name,
                    'studio': episode.channel,
                    'aired': episode.aired,
                    'mpaa': ', '.join(episode.legal) if hasattr(episode, 'legal') and episode.legal else kodi.localize(30216),
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
                         path=routing.url_for(play, category='episodes', item=item.episode_id),
                         art_dict=art_dict,
                         info_dict=info_dict,
                         stream_dict=stream_dict,
                         prop_dict=prop_dict,
                         context_menu=context_menu,
                         is_playable=True)

    raise Exception('Unknown video_type')


@routing.route('/play/epg/<channel>/<timestamp>')
def play_epg_datetime(channel, timestamp):
    """ Play a program based on the channel and the timestamp when it was aired. """
    _vtmGoEpg = VtmGoEpg(kodi)
    broadcast = _vtmGoEpg.get_broadcast(channel, timestamp)
    if not broadcast:
        kodi.show_ok_dialog(heading=kodi.localize(30711), message=kodi.localize(30713))  # The requested video was not found in the guide.
        return

    play_epg(channel, broadcast.playable_type, broadcast.uuid)


@routing.route('/play/epg/<channel>/<program_type>/<epg_id>')
def play_epg(channel, program_type, epg_id):
    """ Play a program based on the channel and information from the EPG. """
    _vtmGoEpg = VtmGoEpg(kodi)
    details = _vtmGoEpg.get_details(channel=channel, program_type=program_type, epg_id=epg_id)
    if not details:
        kodi.show_ok_dialog(heading=kodi.localize(30711), message=kodi.localize(30713))  # The requested video was not found in the guide.
        return

    play(details.playable_type, details.playable_uuid)


@routing.route('/play/<category>/<item>')
def play(category, item):
    """ Play the requested item. Uses setResolvedUrl(). """
    _vtmgostream = VtmGoStream(kodi)

    # Check if inputstreamhelper is correctly installed
    try:
        from inputstreamhelper import Helper
        is_helper = Helper('mpd', drm='com.widevine.alpha')
        if not is_helper.check_inputstream():
            # inputstreamhelper has already shown an error
            return

    except ImportError:
        kodi.show_ok_dialog(message=kodi.localize(30708))  # Please reboot Kodi
        return

    try:
        # Get stream information
        resolved_stream = _vtmgostream.get_stream(category, item)

    except GeoblockedException:
        kodi.show_ok_dialog(heading=kodi.localize(30709), message=kodi.localize(30710))  # Geo-blocked
        return

    except UnavailableException:
        kodi.show_ok_dialog(heading=kodi.localize(30711), message=kodi.localize(30712))  # Unavailable
        return

    info_dict = {
        'tvshowtitle': resolved_stream.program,
        'title': resolved_stream.title,
        'duration': resolved_stream.duration,
    }

    prop_dict = {}

    stream_dict = {
        'duration': resolved_stream.duration,
    }

    # Lookup metadata
    try:
        if category == 'movies':
            info_dict.update({'mediatype': 'movie'})

            # Get details
            details = VtmGo(kodi).get_movie(item)
            info_dict.update({
                'plot': details.description,
                'year': details.year,
            })

        elif category == 'episodes':
            info_dict.update({'mediatype': 'episode'})

            # Get details
            details = VtmGo(kodi).get_episode(item)
            info_dict.update({
                'plot': details.description,
                'season': details.season,
                'episode': details.number,
            })

        elif category == 'channels':
            info_dict.update({'mediatype': 'video'})

            # For live channels, we need to keep on updating the manifest
            # This might not be needed, and could be done with the Location-tag updates if inputstream.adaptive supports it
            # See https://github.com/peak3d/inputstream.adaptive/pull/298#issuecomment-524206935
            prop_dict.update({
                'inputstream.adaptive.manifest_update_parameter': 'full',
            })

        else:
            raise Exception('Unknown category %s' % category)

    except GeoblockedException:
        kodi.show_ok_dialog(heading=kodi.localize(30709), message=kodi.localize(30710))  # Geo-blocked
        return

    except UnavailableException:
        # We continue without details.
        # This seems to make it possible to play some programs what don't have metadata.
        pass

    # Play this item
    kodi.play(
        TitleItem(
            title=resolved_stream.title,
            path=resolved_stream.url,
            subtitles_path=resolved_stream.subtitles,
            art_dict={},
            info_dict=info_dict,
            prop_dict=prop_dict,
            stream_dict=stream_dict,
            is_playable=True,
        ),
        license_key=_vtmgostream.create_license_key(resolved_stream.license_url))


def _format_plot(obj):
    """ Format the plot for a item """
    plot = ''

    if hasattr(obj, 'description'):
        plot += obj.description
        plot += '\n\n'

    if hasattr(obj, 'epg'):
        if obj.epg:
            plot += kodi.localize(30213,  # Now
                                  start=obj.epg[0].start.strftime('%H:%M'),
                                  end=obj.epg[0].end.strftime('%H:%M'),
                                  title=obj.epg[0].title) + "\n"

        if len(obj.epg) > 1:
            plot += kodi.localize(30214,  # Next
                                  start=obj.epg[1].start.strftime('%H:%M'),
                                  end=obj.epg[1].end.strftime('%H:%M'),
                                  title=obj.epg[1].title) + "\n"

    # Add remaining
    if hasattr(obj, 'remaining') and obj.remaining is not None:
        if obj.remaining == 0:
            plot += '» ' + kodi.localize(30208) + "\n"  # Available until midnight
        elif obj.remaining == 1:
            plot += '» ' + kodi.localize(30209) + "\n"  # One more day remaining
        elif obj.remaining / 365 > 5:
            pass  # If it is available for more than 5 years, do not show
        elif obj.remaining / 365 > 2:
            plot += '» ' + kodi.localize(30210, years=int(obj.remaining / 365)) + "\n"  # X years remaining
        elif obj.remaining / 30.5 > 3:
            plot += '» ' + kodi.localize(30211, months=int(obj.remaining / 30.5)) + "\n"  # X months remaining
        else:
            plot += '» ' + kodi.localize(30212, days=obj.remaining) + "\n"  # X days remaining

    # Add geo-blocked message
    if hasattr(obj, 'geoblocked') and obj.geoblocked:
        plot += kodi.localize(30207)  # Geo-blocked
        plot += '\n'

    return plot.rstrip()


def run(params):
    """ Run the routing plugin """
    routing.run(params)
