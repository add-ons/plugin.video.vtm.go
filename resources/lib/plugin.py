# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import routing

from resources.lib import GeoblockedException, UnavailableException
from resources.lib.kodiwrapper import KodiWrapper, TitleItem
from resources.lib.vtmgo.vtmgo import Content, VtmGo
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth, InvalidLoginException
from resources.lib.vtmgo.vtmgoepg import VtmGoEpg
from resources.lib.vtmgo.vtmgostream import VtmGoStream

routing = routing.Plugin()
kodi = KodiWrapper(routing=routing)

VtmGoAuth.username = kodi.get_setting('username')
VtmGoAuth.password = kodi.get_setting('password')
VtmGoAuth.hash = kodi.get_setting('credentials_hash')


@routing.route('/kids')
def show_kids_index():
    show_index()


@routing.route('/')
def show_index():
    kids = kodi.kids_mode()

    listing = []
    listing.extend([
        TitleItem(title=kodi.localize(30001),  # A-Z
                  path=routing.url_for(show_catalog_category if not kids else show_kids_catalog_category, category='all'),
                  art_dict=dict(
                      icon='DefaultMovieTitle.png'
                  ),
                  info_dict=dict(
                      plot=kodi.localize(30002),


                  )),
        TitleItem(title=kodi.localize(30003),  # Catalogue
                  path=routing.url_for(show_catalog if not kids else show_kids_catalog),
                  art_dict=dict(
                      icon='DefaultGenre.png'
                  ),
                  info_dict=dict(
                      plot=kodi.localize(30004),
                  )),
        TitleItem(title=kodi.localize(30005),  # Live TV
                  path=routing.url_for(show_livetv if not kids else show_kids_livetv),
                  art_dict=dict(
                      icon='DefaultAddonPVRClient.png'
                  ),
                  info_dict=dict(
                      plot=kodi.localize(30006),
                  )),
        TitleItem(title=kodi.localize(30013),  # TV Guide
                  path=routing.url_for(show_tvguide if not kids else show_kids_tvguide),
                  art_dict={
                      'icon': 'DefaultAddonTvInfo.png'
                  },
                  info_dict={
                      'plot': kodi.localize(30014),
                  }),
        TitleItem(title=kodi.localize(30015),  # Recommendations
                  path=routing.url_for(show_recommendations if not kids else show_kids_recommendations),
                  art_dict={
                      'icon': 'DefaultFavourites.png'
                  },
                  info_dict={
                      'plot': kodi.localize(30016),
                  }),
        TitleItem(title=kodi.localize(30017),  # My List
                  path=routing.url_for(show_mylist if not kids else show_kids_mylist),
                  art_dict={
                      'icon': 'DefaultPlaylist.png'
                  },
                  info_dict={
                      'plot': kodi.localize(30018),
                  }),
    ])

    # Only provide YouTube option when plugin.video.youtube is available
    if kodi.get_cond_visibility('System.HasAddon(plugin.video.youtube)') != 0:
        listing.append(
            TitleItem(title=kodi.localize(30007),  # YouTube
                      path=routing.url_for(show_youtube if not kids else show_kids_youtube),
                      art_dict=dict(
                          icon='DefaultTags.png'
                      ),
                      info_dict=dict(
                          plot=kodi.localize(30008),
                      ))
        )

    listing.extend([
        TitleItem(title=kodi.localize(30009),  # Search
                  path=routing.url_for(show_search if not kids else show_kids_search),
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
                      path=routing.url_for(show_kids_index),
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
    try:
        auth = VtmGoAuth(kodi)
        auth.clear_token()
        auth.get_token()
        kodi.show_ok_dialog(message=kodi.localize(30202))  # Credentials are correct!

    except InvalidLoginException:
        kodi.show_ok_dialog(message=kodi.localize(30203))  # Your credentials are not valid!
        raise

    kodi.open_settings()


@routing.route('/kids/livetv')
def show_kids_livetv():
    show_livetv()


@routing.route('/livetv')
def show_livetv():
    """ Shows the channels that can play live TV. """
    try:
        _vtmGo = VtmGo(kodi)
        channels = _vtmGo.get_live_channels()
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

        listing.append(
            TitleItem(title=channel.name,
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


@routing.route('/kids/tvguide')
def show_kids_tvguide():
    show_tvguide()


@routing.route('/tvguide')
def show_tvguide():
    """ Shows the channels from the TV guide. """
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
    """ Shows the dates in the tv guide.
    :type channel: string
    """
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
                      })
        )

    kodi.show_listing(listing, 30013, content='files')


@routing.route('/tvguide/<channel>/<date>')
def show_tvguide_detail(channel=None, date=None):
    """ Shows the programs of a specific date in the tv guide.
    :type channel: string
    :type date: string
    """
    try:
        _vtmGoEpg = VtmGoEpg(kodi)
        epg = _vtmGoEpg.get_epg(channel=channel, date=date)
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for broadcast in epg.broadcasts:
        title = '{time} - {title}{live}'.format(
            time=broadcast.time.strftime('%H:%M'),
            title=broadcast.title,
            live=' [I](LIVE)[/I]' if broadcast.live else ''
        )

        if broadcast.airing:
            title = '[B]{title}[/B]'.format(title=title)

        listing.append(
            TitleItem(title=title,
                      path=routing.url_for(play_epg, channel=channel, program_type=broadcast.playable_type, epg_id=broadcast.uuid),
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
                      is_playable=True)
        )

    kodi.show_listing(listing, 30013, content='videos')


@routing.route('/kids/recommendations')
def show_kids_recommendations():
    show_recommendations()


@routing.route('/recommendations')
def show_recommendations():
    """ Show the recommendations. """
    kids = kodi.kids_mode()

    try:
        _vtmGo = VtmGo(kodi)
        recommendations = _vtmGo.get_recommendations()
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for cat in recommendations:
        listing.append(
            TitleItem(title=cat.title,
                      path=routing.url_for(show_kids_recommendations_category if kids else show_recommendations_category, category=cat.category_id),
                      info_dict={
                          'plot': '[B]{category}[/B]'.format(category=cat.title),
                      })
        )

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30015, content='files')


@routing.route('/kids/recommendations/<category>')
def show_kids_recommendations_category(category):
    show_recommendations_category(category)


@routing.route('/recommendations/<category>')
def show_recommendations_category(category):
    """ Show the items in a recommendations category. """
    try:
        _vtmGo = VtmGo(kodi)
        recommendations = _vtmGo.get_recommendations()
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for cat in recommendations:
        # Only show the requested category
        if cat.category_id != category:
            continue

        for item in cat.content:
            if item.video_type == Content.CONTENT_TYPE_MOVIE:
                listing.append(
                    TitleItem(title=item.title,
                              path=routing.url_for(play, category='movies', item=item.content_id),
                              art_dict={
                                  'icon': item.cover,
                                  'thumb': item.cover,
                              },
                              info_dict={
                                  'plot': item.title,
                                  'mediatype': 'movie',
                              },
                              stream_dict={
                                  'codec': 'h264',
                                  'height': 1080,
                                  'width': 1920,
                              },
                              is_playable=True)
                )

            elif item.video_type == Content.CONTENT_TYPE_PROGRAM:
                listing.append(
                    TitleItem(title=item.title,
                              path=routing.url_for(show_program, program=item.content_id),
                              art_dict={
                                  'icon': item.cover,
                                  'thumb': item.cover,
                              },
                              info_dict={
                                  'plot': item.title,
                              })
                )

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30015, content='files')


@routing.route('/kids/mylist')
def show_kids_mylist():
    show_mylist()


@routing.route('/mylist')
def show_mylist():
    """ Show the items in My List. """
    kids = kodi.kids_mode()

    try:
        _vtmGo = VtmGo(kodi)
        mylist = _vtmGo.get_mylist()
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for item in mylist:
        art_dict = {
            'icon': item.cover,
            'thumb': item.cover,
        }

        context_menu = [(
            kodi.localize(30051),  # Remove from My List
            'XBMC.Container.Update(%s)' %
            routing.url_for(mylist_del if not kids else kids_mylist_del,
                            video_type=item.video_type,
                            content_id=item.content_id)
        )]

        if item.video_type == Content.CONTENT_TYPE_MOVIE:
            listing.append(
                TitleItem(title=item.title,
                          path=routing.url_for(play, category='movies', item=item.content_id),
                          art_dict=art_dict,
                          info_dict={
                              'plot': item.title,
                              'mediatype': 'movie',
                          },
                          stream_dict={
                              'codec': 'h264',
                              'height': 1080,
                              'width': 1920,
                          },
                          context_menu=context_menu,
                          is_playable=True)
            )

        elif item.video_type == Content.CONTENT_TYPE_PROGRAM:
            listing.append(
                TitleItem(title=item.title,
                          path=routing.url_for(show_program, program=item.content_id),
                          art_dict=art_dict,
                          info_dict={
                              'plot': item.title,
                              'mediatype': None,
                          },
                          context_menu=context_menu)
            )

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30017, content='files')


@routing.route('/kids/mylist/add/<video_type>/<content_id>')
def kids_mylist_add(video_type, content_id):
    mylist_add(video_type, content_id)


@routing.route('/mylist/add/<video_type>/<content_id>')
def mylist_add(video_type, content_id):
    """ Add an item to My List. """
    _vtmGo = VtmGo(kodi)
    _vtmGo.add_mylist(video_type, content_id)


@routing.route('/kids/mylist/del/<video_type>/<content_id>')
def kids_mylist_del(video_type, content_id):
    mylist_del(video_type, content_id)


@routing.route('/mylist/del/<video_type>/<content_id>')
def mylist_del(video_type, content_id):
    """ Remove an item from My List. """
    _vtmGo = VtmGo(kodi)
    _vtmGo.del_mylist(video_type, content_id)


@routing.route('/kids/catalog')
def show_kids_catalog():
    show_catalog()


@routing.route('/catalog')
def show_catalog():
    """ Show the catalog. """
    kids = kodi.kids_mode()

    try:
        _vtmGo = VtmGo(kodi)
        categories = _vtmGo.get_categories()
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for cat in categories:
        listing.append(
            TitleItem(title=cat.title,
                      path=routing.url_for(show_kids_catalog_category if kids else show_catalog_category, category=cat.category_id),
                      info_dict={
                          'plot': '[B]{category}[/B]'.format(category=cat.title),
                      })
        )

    # Sort categories by default like in VTM GO.
    kodi.show_listing(listing, 30003, content='files')


@routing.route('/kids/catalog/<category>')
def show_kids_catalog_category(category):
    show_catalog_category(category)


@routing.route('/catalog/<category>')
def show_catalog_category(category):
    """ Show a category in the catalog. """
    kids = kodi.kids_mode()

    try:
        _vtmGo = VtmGo(kodi)
        items = _vtmGo.get_items(category)
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    listing = []
    for item in items:
        art_dict = {
            'thumb': item.cover,
            'fanart': item.cover,
        }

        # Add "Add to My List" here
        # We don't know if it is already on My List, so we can't give an option to remove here.
        context_menu = [(
            kodi.localize(30050),  # Add to My List
            'XBMC.Container.Update(%s)' % routing.url_for(mylist_add if not kids else kids_mylist_add,
                                                          video_type=item.video_type,
                                                          content_id=item.content_id)
        )]

        if item.video_type == Content.CONTENT_TYPE_MOVIE:
            listing.append(
                TitleItem(title=item.title,
                          path=routing.url_for(play, category='movies', item=item.content_id),
                          art_dict=art_dict,
                          info_dict={
                              'title': item.title,
                              'plot': item.description,
                              'mediatype': 'movie',
                          },
                          stream_dict={
                              'codec': 'h264',
                              'height': 1080,
                              'width': 1920,
                          },
                          context_menu=context_menu,
                          is_playable=True)
            )

        elif item.video_type == Content.CONTENT_TYPE_PROGRAM:
            listing.append(
                TitleItem(title=item.title,
                          path=routing.url_for(show_program, program=item.content_id),
                          art_dict=art_dict,
                          info_dict={
                              'title': item.title,
                              'plot': item.description,
                              'mediatype': None,
                          },
                          context_menu=context_menu)
            )

    # Sort items by label, but don't put folders at the top.
    # Used for A-Z listing or when movies and episodes are mixed.
    kodi.show_listing(listing, 30003, content='movies' if category == 'films' else 'tvshows', sort='label')


@routing.route('/program/<program>')
def show_program(program):
    """ Show a program from the catalog. """
    try:
        _vtmGo = VtmGo(kodi)
        program_obj = _vtmGo.get_program(program)
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

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
    """ Show a program from the catalog. """
    try:
        _vtmGo = VtmGo(kodi)
        program_obj = _vtmGo.get_program(program)
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    if season == 'all':
        # Show all seasons
        seasons = program_obj.seasons.values()
    else:
        # Show the season that was selected
        seasons = [program_obj.seasons[int(season)]]

    listing = []
    for s in seasons:
        for episode in s.episodes.values():
            listing.append(
                TitleItem(title=episode.name,
                          path=routing.url_for(play, category='episodes', item=episode.episode_id),
                          art_dict={
                              'banner': program_obj.cover,
                              'fanart': program_obj.cover,
                              'thumb': episode.cover,
                          },
                          info_dict={
                              'tvshowtitle': program_obj.name,
                              'title': episode.name,
                              'tagline': program_obj.description,
                              'plot': _format_plot(episode),
                              'duration': episode.duration,
                              'season': episode.season,
                              'episode': episode.number,
                              'mediatype': 'episode',
                              'set': program_obj.name,
                              'studio': episode.channel,
                              'aired': episode.aired,
                              'overlay': 2,
                              'mpaa': ', '.join(episode.legal) if hasattr(episode, 'legal') and episode.legal else kodi.localize(30216),
                          },
                          stream_dict={
                              'duration': episode.duration,
                              'codec': 'h264',
                              'height': 1080,
                              'width': 1920,
                          },
                          is_playable=True)
            )

    # Sort by episode number by default. Takes seasons into account.
    kodi.show_listing(listing, 30003, content='episodes', sort='episode')


@routing.route('/kids/youtube')
def show_kids_youtube():
    show_youtube()


@routing.route('/youtube')
def show_youtube():
    """ Shows the Youtube channel overview. """
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


@routing.route('/kids/search')
@routing.route('/kids/search/<query>')
def show_kids_search(query=None):
    show_search(query)


@routing.route('/search')
@routing.route('/search/<query>')
def show_search(query=None):
    """ Shows the search dialog. """
    kids = kodi.kids_mode()

    if not query:
        # Ask for query
        query = kodi.get_search_string(heading=kodi.localize(30009))
        if not query:
            kodi.end_of_directory()
            return

    # Do search
    try:
        _vtmGo = VtmGo(kodi)
        items = _vtmGo.do_search(query)
    except Exception as ex:
        kodi.show_notification(message=str(ex))
        raise

    # Display results
    listing = []
    for item in items:
        art_dict = {
            'thumb': item.cover,
            'fanart': item.cover,
        }

        # Add "Add to My List" here
        # We don't know if it is already on My List, so we can't give an option to remove here.
        context_menu = [(
            kodi.localize(30050),  # Add to My List
            'XBMC.Container.Update(%s)' % routing.url_for(mylist_add if not kids else kids_mylist_add,
                                                          video_type=item.video_type,
                                                          content_id=item.content_id)
        )]

        if item.video_type == Content.CONTENT_TYPE_MOVIE:
            listing.append(
                TitleItem(title=item.title,
                          path=routing.url_for(play, category='movies', item=item.content_id),
                          art_dict=art_dict,
                          info_dict={
                              'title': item.title,
                              'plot': item.description,
                              'mediatype': 'movie',
                          },
                          stream_dict={
                              'codec': 'h264',
                              'height': 1080,
                              'width': 1920,
                          },
                          context_menu=context_menu,
                          is_playable=True)
            )

        elif item.video_type == Content.CONTENT_TYPE_PROGRAM:
            listing.append(
                TitleItem(title=item.title,
                          path=routing.url_for(show_program, program=item.content_id),
                          art_dict=art_dict,
                          info_dict={
                              'title': item.title,
                              'plot': item.description,
                              'mediatype': None,
                          },
                          context_menu=context_menu)
            )

    # Sort like we get our results back.
    kodi.show_listing(listing, 30009)


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

    # Get stream information
    try:
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
    plot = ''

    # Add program name to plot
    if hasattr(obj, 'name') or (hasattr(obj, 'legal') and obj.legal):
        if hasattr(obj, 'name'):
            plot += '[B]{name}[/B]'.format(name=obj.name)
        if hasattr(obj, 'legal') and obj.legal:
            plot += '  [COLOR gray]'
            for icon in obj.legal:
                plot += '[%s]' % icon
            plot += '[/COLOR]'
        plot += '\n'

    if hasattr(obj, 'geoblocked') and obj.geoblocked:
        plot += kodi.localize(30207)  # Geo-blocked

    if hasattr(obj, 'remaining') and obj.remaining is not None:
        if obj.remaining == 0:
            plot += kodi.localize(30208)  # Available until midnight
        elif obj.remaining == 1:
            plot += kodi.localize(30209)  # One more day remaining
        elif obj.remaining / 365 > 5:
            pass  # If it is available for more than 5 years, do not show
        elif obj.remaining / 365 > 2:
            plot += kodi.localize(30210, years=int(obj.remaining / 365))  # X years remaining
        elif obj.remaining / 30.5 > 3:
            plot += kodi.localize(30211, months=int(obj.remaining / 30.5))  # X months remaining
        else:
            plot += kodi.localize(30212, days=obj.remaining)  # X days remaining

    if plot:
        plot += '\n'

    if hasattr(obj, 'description'):
        plot += obj.description

    if hasattr(obj, 'epg'):
        if obj.epg:
            plot += kodi.localize(30213,  # Now
                                  start=obj.epg[0].start.strftime('%H:%M'),
                                  end=obj.epg[0].end.strftime('%H:%M'),
                                  title=obj.epg[0].title)

        if len(obj.epg) > 1:
            plot += kodi.localize(30214,  # Next
                                  start=obj.epg[1].start.strftime('%H:%M'),
                                  end=obj.epg[1].end.strftime('%H:%M'),
                                  title=obj.epg[1].title)

    return plot


def run(params):
    routing.run(params)
