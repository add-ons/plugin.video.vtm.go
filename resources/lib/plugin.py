# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import routing
import xbmcplugin
from xbmc import Keyboard, getRegion
from xbmcgui import ListItem

from resources.lib import kodilogging, GeoblockedException, UnavailableException
from resources.lib.kodiutils import (get_cond_visibility, get_max_bandwidth, get_setting,
                                     get_setting_as_bool, get_global_setting, localize,
                                     notification, show_ok_dialog, show_settings, get_addon_path)
from resources.lib.vtmgo import Content, VtmGo
from resources.lib.vtmgoauth import VtmGoAuth, InvalidLoginException
from resources.lib.vtmgoepg import VtmGoEpg
from resources.lib.vtmgostream import VtmGoStream

plugin = routing.Plugin()
logger = kodilogging.get_logger('plugin')

VtmGoAuth.username = get_setting('username')
VtmGoAuth.password = get_setting('password')
VtmGoAuth.hash = get_setting('credentials_hash')


@plugin.route('/kids')
def show_kids_index():
    show_index()


@plugin.route('/')
def show_index():
    kids = _get_kids_mode()

    listing = []
    listitem = ListItem(localize(30001), offscreen=True)  # A-Z
    listitem.setArt({'icon': 'DefaultMovieTitle.png'})
    listitem.setInfo('video', {
        'plot': localize(30002),
    })
    route_catalog_category = show_kids_catalog_category if kids else show_catalog_category
    listing.append((plugin.url_for(route_catalog_category, category='all'), listitem, True))

    listitem = ListItem(localize(30003), offscreen=True)  # Catalogue
    listitem.setArt({'icon': 'DefaultGenre.png'})
    listitem.setInfo('video', {
        'plot': localize(30004),
    })
    route_catalog = show_kids_catalog if kids else show_catalog
    listing.append((plugin.url_for(route_catalog), listitem, True))

    listitem = ListItem(localize(30005), offscreen=True)  # Live TV
    listitem.setArt({'icon': 'DefaultAddonPVRClient.png'})
    listitem.setInfo('video', {
        'plot': localize(30006),
    })
    route_livetv = show_kids_livetv if kids else show_livetv
    listing.append((plugin.url_for(route_livetv), listitem, True))

    listitem = ListItem(localize(30013), offscreen=True)  # TV Guide
    listitem.setArt({'icon': 'DefaultAddonTvInfo.png'})
    listitem.setInfo('video', {
        'plot': localize(30014),
    })
    route_tvguide = show_kids_tvguide if kids else show_tvguide
    listing.append((plugin.url_for(route_tvguide), listitem, True))

    listitem = ListItem(localize(30015), offscreen=True)  # Recommendations
    listitem.setArt({'icon': 'DefaultFavourites.png'})
    listitem.setInfo('video', {
        'plot': localize(30016),
    })
    route_recommendations = show_kids_recommendations if kids else show_recommendations
    listing.append((plugin.url_for(route_recommendations), listitem, True))

    listitem = ListItem(localize(30017), offscreen=True)  # My List
    listitem.setArt({'icon': 'DefaultMusicPlaylist.png'})
    listitem.setInfo('video', {
        'plot': localize(30018),
    })
    route_mylist = show_kids_mylist if kids else show_mylist
    listing.append((plugin.url_for(route_mylist), listitem, True))

    # Only provide YouTube option when plugin.video.youtube is available
    if get_cond_visibility('System.HasAddon(plugin.video.youtube)') != 0:
        listitem = ListItem(localize(30007), offscreen=True)  # YouTube
        listitem.setArt({'icon': 'DefaultTags.png'})
        listitem.setInfo('video', {
            'plot': localize(30008),
        })
        route_youtube = show_kids_youtube if kids else show_youtube
        listing.append((plugin.url_for(route_youtube), listitem, True))

    listitem = ListItem(localize(30009), offscreen=True)  # Search
    listitem.setArt({'icon': 'DefaultAddonsSearch.png'})
    listitem.setInfo('video', {
        'plot': localize(30010),
    })
    route_search = show_kids_search if kids else show_search
    listing.append((plugin.url_for(route_search), listitem, True))

    if get_setting_as_bool('use_kids_zone') and not kids:
        listitem = ListItem(localize(30011), offscreen=True)  # Kids Zone
        listitem.setArt({'icon': 'DefaultUser.png'})
        listitem.setInfo('video', {
            'plot': localize(30012),
        })
        listing.append((plugin.url_for(show_kids_index), listitem, True))

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(title=True))
    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/check-credentials')
def check_credentials():
    try:
        auth = VtmGoAuth()
        auth.clear_token()
        auth.get_token()
        show_ok_dialog(message=localize(30202))  # Credentials are correct!

    except InvalidLoginException:
        show_ok_dialog(message=localize(30203))  # Your credentials are not valid!
        raise

    show_settings()


@plugin.route('/kids/livetv')
def show_kids_livetv():
    show_livetv()


@plugin.route('/livetv')
def show_livetv():
    from . import CHANNEL_MAPPING

    kids = _get_kids_mode()
    try:
        _vtmGo = VtmGo(kids=kids)
        channels = _vtmGo.get_live()
    except Exception as ex:
        notification(message=str(ex))
        raise

    listing = []
    for channel in channels:
        listitem = ListItem(channel.name, offscreen=True)

        if CHANNEL_MAPPING.get(channel.name):
            # Lookup the high resolution logo based on the channel name
            icon = '{path}/resources/logos/{logo}-white.png'.format(path=get_addon_path(), logo=CHANNEL_MAPPING.get(channel.name))
            fanart = '{path}/resources/logos/{logo}.png'.format(path=get_addon_path(), logo=CHANNEL_MAPPING.get(channel.name))
        else:
            # Fallback to the default (lower resolution) logo
            icon = channel.logo
            fanart = channel.logo

        listitem.setInfo('video', {
            'plot': _format_plot(channel),
            'playcount': 0,
            'mediatype': 'video',
        })
        listitem.setArt({
            'icon': icon,
            'thumb': icon,
            'fanart': fanart,
        })
        listitem.setProperty('IsPlayable', 'true')

        listing.append((plugin.url_for(play, category='channels', item=channel.channel_id) + '?.pvr', listitem, False))

    # Sort live channels by default like in VTM GO.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30005), title=True))
    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/kids/tvguide')
def show_kids_tvguide():
    show_tvguide()


@plugin.route('/tvguide')
def show_tvguide():
    from . import CHANNELS

    kids = _get_kids_mode()

    listing = []
    for entry in CHANNELS:
        # Skip non-kids channels when we are in kids mode.
        if kids and entry.get('kids') is False:
            continue

        # Lookup the high resolution logo based on the channel name
        icon = '{path}/resources/logos/{logo}-white.png'.format(path=get_addon_path(), logo=entry.get('logo'))
        fanart = '{path}/resources/logos/{logo}.png'.format(path=get_addon_path(), logo=entry.get('logo'))

        listitem = ListItem(entry.get('label'), offscreen=True)
        listitem.setInfo('video', {
            'plot': localize(30215, channel=entry.get('label')),
            'mediatype': 'video',
        })
        listitem.setArt({
            'icon': icon,
            'thumb': icon,
            'fanart': fanart,
        })
        listing.append((plugin.url_for(show_tvguide_channel, channel=entry.get('key')), listitem, True))

    # Sort by default like in our dict.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)

    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30013), title=True))
    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/tvguide/<channel>')
def show_tvguide_channel(channel):
    listing = []

    date_format = getRegion('datelong')

    for day in VtmGoEpg.get_dates(date_format):
        if day.get('highlight'):
            title = '[B]{title}[/B]'.format(title=day.get('title'))
        else:
            title = day.get('title')

        listitem = ListItem(title, offscreen=True)
        listitem.setArt({
            'icon': 'DefaultYear.png',
        })
        listitem.setInfo('video', {
            'plot': day.get('title'),
        })
        listing.append((plugin.url_for(show_tvguide_detail, channel=channel, date=day.get('date')), listitem, True))

    xbmcplugin.setContent(plugin.handle, 'files')

    # Sort like we add it.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)

    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30013), channel))
    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/tvguide/<channel>/<date>')
def show_tvguide_detail(channel=None, date=None):
    """ Shows the programs of a specific date in the tv guide.
    :type channel: string
    :type date: string
    """
    try:
        _vtmGoEpg = VtmGoEpg()
        epg = _vtmGoEpg.get_epg(channel=channel, date=date)
    except Exception as ex:
        notification(message=str(ex))
        raise

    # The epg contains the data for all channels. We only need the data of the requested channel.
    listing = []
    for broadcast in epg.broadcasts:
        title = '{time} - {title}'.format(
            time=broadcast.time.strftime('%H:%M'),
            title=broadcast.title
        )

        listitem = ListItem(title, offscreen=True)
        listitem.setArt({
            'thumb': broadcast.image,
        })
        listitem.setInfo('video', {
            'title': title,
            'plot': broadcast.description,
            'duration': broadcast.duration,
        })
        listitem.addStreamInfo('video', {
            'duration': broadcast.duration,
        })
        listitem.setProperty('IsPlayable', 'true')
        listing.append((plugin.url_for(play_epg, channel=channel, program_type=broadcast.playable_type, epg_id=broadcast.uuid), listitem, False))

    xbmcplugin.setContent(plugin.handle, 'episodes')

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30013), channel))
    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/kids/recommendations')
def show_kids_recommendations():
    show_recommendations()


@plugin.route('/recommendations')
def show_recommendations():
    """ Show the recommendations. """
    kids = _get_kids_mode()

    listing = []
    try:
        _vtmGo = VtmGo(kids=kids)
        recommendations = _vtmGo.get_recommendations()
    except Exception as ex:
        notification(message=str(ex))
        raise

    for cat in recommendations:
        listitem = ListItem(cat.title, offscreen=True)
        listitem.setInfo('video', {
            'plot': '[B]{category}[/B]'.format(category=cat.title),
        })
        listing.append(
            (plugin.url_for(show_kids_recommendations_category if kids else show_recommendations_category, category=cat.category_id), listitem, True))

    xbmcplugin.setContent(plugin.handle, 'files')

    # Sort categories by default like in VTM GO.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30015)))

    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/kids/recommendations/<category>')
def show_kids_recommendations_category(category):
    show_recommendations_category(category)


@plugin.route('/recommendations/<category>')
def show_recommendations_category(category):
    """ Show the items in a recommendations category. """
    kids = _get_kids_mode()

    listing = []
    try:
        _vtmGo = VtmGo(kids=kids)
        recommendations = _vtmGo.get_recommendations()
    except Exception as ex:
        notification(message=str(ex))
        raise

    title = None

    for cat in recommendations:
        if cat.category_id == category:

            title = cat.title

            for item in cat.content:
                listitem = ListItem(item.title, offscreen=True)
                listitem.setArt({
                    'thumb': item.cover,
                })

                if item.video_type == Content.CONTENT_TYPE_MOVIE:
                    listitem.setInfo('video', {
                        'mediatype': 'movie',
                    })
                    listitem.setProperty('IsPlayable', 'true')
                    listing.append((plugin.url_for(play, category='movies', item=item.content_id), listitem, False))

                elif item.video_type == Content.CONTENT_TYPE_PROGRAM:
                    listitem.setInfo('video', {
                        'mediatype': None,  # This shows a folder icon
                    })
                    listing.append((plugin.url_for(show_program, program=item.content_id), listitem, True))

    xbmcplugin.setContent(plugin.handle, 'files')

    # Sort categories by default like in VTM GO.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30015), title))

    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/kids/mylist')
def show_kids_mylist():
    show_mylist()


@plugin.route('/mylist')
def show_mylist():
    """ Show the items in My List. """
    kids = _get_kids_mode()

    listing = []
    try:
        _vtmGo = VtmGo(kids=kids)
        mylist = _vtmGo.get_mylist()
    except Exception as ex:
        notification(message=str(ex))
        raise

    for item in mylist:
        listitem = ListItem(item.title, offscreen=True)
        listitem.setArt({
            'thumb': item.cover,
        })

        if item.video_type == Content.CONTENT_TYPE_MOVIE:
            listitem.setInfo('video', {
                'mediatype': 'movie',
            })
            listitem.setProperty('IsPlayable', 'true')
            listing.append((plugin.url_for(play, category='movies', item=item.content_id), listitem, False))

        elif item.video_type == Content.CONTENT_TYPE_PROGRAM:
            listitem.setInfo('video', {
                'mediatype': None,  # This shows a folder icon
            })
            listing.append((plugin.url_for(show_program, program=item.content_id), listitem, True))

    xbmcplugin.setContent(plugin.handle, 'files')

    # Sort categories by default like in VTM GO.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30017)))

    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/kids/catalog')
def show_kids_catalog():
    show_catalog()


@plugin.route('/catalog')
def show_catalog():
    """ Show the catalog. """
    kids = _get_kids_mode()

    listing = []
    try:
        _vtmGo = VtmGo(kids=kids)
        categories = _vtmGo.get_categories()
    except Exception as ex:
        notification(message=str(ex))
        raise

    for cat in categories:
        listitem = ListItem(cat.title, offscreen=True)
        listitem.setInfo('video', {
            'plot': '[B]{category}[/B]'.format(category=cat.title),
        })
        listing.append((plugin.url_for(show_kids_catalog_category if kids else show_catalog_category, category=cat.category_id), listitem, True))

    xbmcplugin.setContent(plugin.handle, 'files')

    # Sort categories by default like in VTM GO.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30003)))

    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/kids/catalog/<category>')
def show_kids_catalog_category(category):
    show_catalog_category(category)


@plugin.route('/catalog/<category>')
def show_catalog_category(category):
    """ Show a category in the catalog. """
    kids = _get_kids_mode()

    listing = []
    try:
        _vtmGo = VtmGo(kids=kids)
        items = _vtmGo.get_items(category)
    except Exception as ex:
        notification(message=str(ex))
        raise

    for item in items:
        listitem = ListItem(item.title, offscreen=True)
        listitem.setArt({
            'thumb': item.cover,
            'fanart': item.cover,
        })
        listitem.setInfo('video', {
            'title': item.title,
            'plot': item.description,
            # If it is a TV show we return None to get a folder icon
            'mediatype': 'movie' if item.video_type == Content.CONTENT_TYPE_MOVIE else None,
        })
        listitem.setProperty('IsPlayable', 'true')

        if item.video_type == Content.CONTENT_TYPE_MOVIE:
            listing.append((plugin.url_for(play, category='movies', item=item.content_id), listitem, False))

        elif item.video_type == Content.CONTENT_TYPE_PROGRAM:
            listing.append((plugin.url_for(show_program, program=item.content_id), listitem, True))

    if category == 'films':
        xbmcplugin.setContent(plugin.handle, 'movies')
    else:
        xbmcplugin.setContent(plugin.handle, 'tvshows')

    # Sort items by label, but don't put folders at the top.
    # Used for A-Z listing or when movies and episodes are mixed.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30003), category.title()))

    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/program/<program>')
def show_program(program):
    """ Show a program from the catalog. """
    kids = _get_kids_mode()
    try:
        _vtmGo = VtmGo(kids=kids)
        program_obj = _vtmGo.get_program(program)
    except Exception as ex:
        notification(message=str(ex))
        raise

    listing = []

    # Add an '* All seasons' entry when configured in Kodi
    if get_global_setting('videolibrary.showallitems') is True:
        listitem = ListItem('* %s' % localize(30204), offscreen=True)  # * All seasons
        listitem.setArt({
            'thumb': program_obj.cover,
            'fanart': program_obj.cover,
        })
        listitem.setInfo('video', {
            'tvshowtitle': program_obj.name,
            'title': localize(30204),  # All seasons
            'tagline': program_obj.description,
            'set': program_obj.name,
            'mpaa': ', '.join(program_obj.legal) if hasattr(program_obj, 'legal') and program_obj.legal else localize(30216),
        })
        listing.append((plugin.url_for(show_program_season, program=program, season='all'), listitem, True))

    for s in program_obj.seasons.values():
        listitem = ListItem(localize(30205, season=s.number), offscreen=True)  # Season X
        listitem.setArt({
            'thumb': s.cover,
            'fanart': program_obj.cover,
        })
        listitem.setInfo('video', {
            'tvshowtitle': program_obj.name,
            'title': localize(30205, season=s.number),
            'tagline': program_obj.description,
            'set': program_obj.name,
            'season': s.number,
            'mpaa': ', '.join(program_obj.legal) if hasattr(program_obj, 'legal') and program_obj.legal else localize(30216),
        })
        listing.append((plugin.url_for(show_program_season, program=program, season=s.number), listitem, True))
    xbmcplugin.setContent(plugin.handle, 'tvshows')

    # Sort by label. Some programs return seasons unordered.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setPluginCategory(plugin.handle, category=program_obj.name)
    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/program/<program>/<season>')
def show_program_season(program, season):
    """ Show a program from the catalog. """
    kids = _get_kids_mode()
    try:
        _vtmGo = VtmGo(kids=kids)
        program_obj = _vtmGo.get_program(program)
    except Exception as ex:
        notification(message=str(ex))
        raise

    listing = []

    if season == 'all':
        # Show all seasons
        seasons = program_obj.seasons.values()
    else:
        # Show the season that was selected
        seasons = [program_obj.seasons[int(season)]]

    for s in seasons:
        for episode in s.episodes.values():
            listitem = ListItem(episode.name, offscreen=True)
            listitem.setArt({
                'banner': program_obj.cover,
                'fanart': program_obj.cover,
                'thumb': episode.cover,
            })
            listitem.setInfo('video', {
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
                'mpaa': ', '.join(episode.legal) if hasattr(episode, 'legal') and episode.legal else localize(30216),
            })
            listitem.addStreamInfo('video', {
                'duration': episode.duration,
            })
            listitem.setProperty('IsPlayable', 'true')
            listing.append((plugin.url_for(play, category='episodes', item=episode.episode_id), listitem, False))

    xbmcplugin.setContent(plugin.handle, 'episodes')

    # Sort by episode number by default. Takes seasons into account.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DURATION)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.setPluginCategory(plugin.handle, category=program_obj.name)
    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/kids/youtube')
def show_kids_youtube():
    show_youtube()


@plugin.route('/youtube')
def show_youtube():
    kids = _get_kids_mode()

    listing = []

    from resources.lib import YOUTUBE
    for entry in YOUTUBE:
        # Skip non-kids channels when we are in kids mode.
        if kids and entry.get('kids') is False:
            continue

        # Lookup the high resolution logo based on the channel name
        icon = '{path}/resources/logos/{logo}-white.png'.format(path=get_addon_path(), logo=entry.get('logo'))
        fanart = '{path}/resources/logos/{logo}.png'.format(path=get_addon_path(), logo=entry.get('logo'))

        listitem = ListItem(entry.get('label'), offscreen=True)
        listitem.setInfo('video', {
            'plot': localize(30206, label=entry.get('label')),
            'studio': entry.get('studio'),
            'mediatype': 'video',
        })
        listitem.setArt({
            'icon': icon,
            'fanart': fanart,
            'thumb': icon,
        })
        listing.append((entry.get('path'), listitem, True))

    # Sort by default like in our dict.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb(localize(30007), title=True))

    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/kids/search')
def show_kids_search():
    show_search()


@plugin.route('/search')
def show_search():
    kids = _get_kids_mode()

    # Ask for query
    keyboard = Keyboard('', localize(30009))
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return
    query = keyboard.getText()

    try:
        # Do search
        _vtmGo = VtmGo(kids=kids)
        items = _vtmGo.do_search(query)
    except Exception as ex:
        notification(message=str(ex))
        raise

    # Display results
    listing = []
    for item in items:
        listitem = ListItem(item.title, offscreen=True)

        if item.video_type == Content.CONTENT_TYPE_MOVIE:
            listitem.setInfo('video', {
                'mediatype': 'movie',
            })
            listitem.setProperty('IsPlayable', 'true')
            listing.append((plugin.url_for(play, category='movies', item=item.content_id), listitem, False))

        elif item.video_type == Content.CONTENT_TYPE_PROGRAM:
            listitem.setInfo('video', {
                'mediatype': None,  # This shows a folder icon
            })
            listing.append((plugin.url_for(show_program, program=item.content_id), listitem, True))

    xbmcplugin.setContent(plugin.handle, 'tvshows')

    # Sort like we get our results back.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
    xbmcplugin.setPluginCategory(plugin.handle, category=_breadcrumb('Search: {query}').format(query=query))
    ok = xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    xbmcplugin.endOfDirectory(plugin.handle, ok)


@plugin.route('/play/epg/<channel>/<program_type>/<epg_id>')
def play_epg(channel, program_type, epg_id):
    _vtmGoEpg = VtmGoEpg()
    details = _vtmGoEpg.get_details(channel=channel, program_type=program_type, epg_id=epg_id)
    play(details.playable_type, details.playable_uuid)


@plugin.route('/play/<category>/<item>')
def play(category, item):
    """ Play the requested item. Uses setResolvedUrl(). """
    _vtmgostream = VtmGoStream()

    try:
        # Get url
        resolved_stream = _vtmgostream.get_stream(category, item)

    except GeoblockedException:
        show_ok_dialog(heading=localize(30709), message=localize(30710))  # Geo-blocked
        return

    except UnavailableException:
        show_ok_dialog(heading=localize(30711), message=localize(30712))  # Unavailable
        return

    # Create listitem
    listitem = ListItem(path=resolved_stream.url, offscreen=True)

    # Lookup metadata
    try:
        if category == 'movies':
            listitem.setInfo('video', {
                'tvshowtitle': resolved_stream.program,
                'title': resolved_stream.title,
                'duration': resolved_stream.duration,
                'mediatype': 'movie',
            })

            details = VtmGo().get_movie(item)
            listitem.setInfo('video', {
                'tagline': details.description,
                'plot': details.description,
            })
        elif category == 'episodes':
            listitem.setInfo('video', {
                'tvshowtitle': resolved_stream.program,
                'title': resolved_stream.title,
                'duration': resolved_stream.duration,
                'mediatype': 'episode',
            })

            details = VtmGo().get_episode(item)
            listitem.setInfo('video', {
                'tagline': details.description,
                'plot': details.description,
                'season': details.season,
                'episode': details.number,
            })
        elif category == 'channels':
            listitem.setInfo('video', {
                'title': resolved_stream.title,
                'tvshowtitle': resolved_stream.program,
                'mediatype': 'video'
            })

            # For live channels, we need to keep on updating the manifest
            # This might not be needed, and could be done with the Location-tag updates if inputstream.adaptive supports it
            # See https://github.com/peak3d/inputstream.adaptive/pull/298#issuecomment-524206935
            listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
        else:
            raise Exception('Unknown category %s' % category)

    except GeoblockedException:
        show_ok_dialog(heading=localize(30709), message=localize(30710))  # Geo-blocked
        return
    except UnavailableException:
        # We continue without details.
        # This seems to make it possible to play some programs what don't have metadata.
        pass

    listitem.addStreamInfo('video', {
        'duration': resolved_stream.duration,
    })

    # Add subtitle info
    subtitles_visible = get_setting('showsubtitles', 'true') == 'true'
    if subtitles_visible and resolved_stream.subtitles:
        listitem.setSubtitles(resolved_stream.subtitles)
        listitem.addStreamInfo('subtitle', {
            'language': 'nl',
        })

    listitem.setProperty('IsPlayable', 'true')
    listitem.setProperty('network.bandwidth', str(get_max_bandwidth() * 1000))
    listitem.setProperty('inputstream.adaptive.max_bandwidth', str(get_max_bandwidth() * 1000))
    listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    listitem.setMimeType('application/dash+xml')
    listitem.setContentLookup(False)

    try:
        from inputstreamhelper import Helper
    except ImportError:
        show_ok_dialog(message=localize(30708))  # Please reboot Kodi
        return

    is_helper = Helper('mpd', drm='com.widevine.alpha')
    if is_helper.check_inputstream():
        listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.adaptive.license_key', _vtmgostream.create_license_key(resolved_stream.license_url))
        xbmcplugin.setResolvedUrl(plugin.handle, True, listitem)


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
        plot += localize(30207)  # Geo-blocked

    if hasattr(obj, 'remaining') and obj.remaining is not None:
        if obj.remaining == 0:
            plot += localize(30208)  # Available until midnight
        elif obj.remaining == 1:
            plot += localize(30209)  # One more day remaining
        elif obj.remaining / 365 > 5:
            pass  # If it is available for more than 5 years, do not show
        elif obj.remaining / 365 > 2:
            plot += localize(30210, years=int(obj.remaining / 365))  # X years remaining
        elif obj.remaining / 30.5 > 3:
            plot += localize(30211, months=int(obj.remaining / 30.5))  # X months remaining
        else:
            plot += localize(20112, days=obj.remaining)  # X days remaining

    if plot:
        plot += '\n'

    if hasattr(obj, 'description'):
        plot += obj.description

    if hasattr(obj, 'epg'):
        if obj.epg:
            plot += localize(30213,  # Now
                             start=obj.epg[0].start.strftime('%H:%M'),
                             end=obj.epg[0].end.strftime('%H:%M'),
                             title=obj.epg[0].title)

        if len(obj.epg) > 1:
            plot += localize(30214,  # Next
                             start=obj.epg[1].start.strftime('%H:%M'),
                             end=obj.epg[1].end.strftime('%H:%M'),
                             title=obj.epg[1].title)

    return plot


def _get_kids_mode():
    if get_setting_as_bool('use_kids_zone') and get_setting_as_bool('force_kids_zone'):
        return True

    if plugin.path.startswith('/kids'):
        return True
    return False


def _breadcrumb(*args, **kwargs):
    # Append Kids indicatore
    if _get_kids_mode():
        args = ('KIDS',) + args

    # Add title if requested
    if kwargs.get('title', False):
        breadcrumb = 'VTM GO'
        if args:
            breadcrumb += ' / '
    else:
        breadcrumb = ''

    # Add other parts
    if args:
        breadcrumb = breadcrumb + " / ".join(args)

    return breadcrumb


def run(params):
    plugin.run(params)
