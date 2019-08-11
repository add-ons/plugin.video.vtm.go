# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import logging

import xbmc
import xbmcplugin
from xbmcaddon import Addon
from xbmcgui import Dialog, ListItem

import routing
from resources.lib import kodilogging
from resources.lib import vtmgostream
from resources.lib.kodiutils import get_cond_visibility, get_global_setting, get_setting, notification, show_ok_dialog, show_settings, get_setting_as_bool, set_setting
from resources.lib.vtmgo import VtmGo, Content

ADDON = Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()


@plugin.route('/')
def show_index():
    kids = _get_kids_mode()

    listitem = ListItem('A-Z', offscreen=True)
    listitem.setArt({'icon': 'DefaultMovieTitle.png'})
    listitem.setInfo('video', {
        'plot': 'Alphabetically sorted list of programs',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog, category='all', kids=kids), listitem, True)

    listitem = ListItem('Catalogue', offscreen=True)
    listitem.setArt({'icon': 'DefaultGenre.png'})
    listitem.setInfo('video', {
        'plot': 'TV Shows and Movies listed by category',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog, kids=kids), listitem, True)

    listitem = ListItem('Live TV', offscreen=True)
    listitem.setArt({'icon': 'DefaultAddonPVRClient.png'})
    listitem.setInfo('video', {
        'plot': 'Watch channels live via Internet',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_livetv, kids=kids), listitem, True)

    # Only provide YouTube option when plugin.video.youtube is available
    if xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)') != 0:
        listitem = ListItem('YouTube', offscreen=True)
        listitem.setArt({'icon': 'DefaultTags.png'})
        listitem.setInfo('video', {
            'plot': 'Watch YouTube content',
        })
        xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_youtube, kids=kids), listitem, True)

    listitem = ListItem('Search', offscreen=True)
    listitem.setArt({'icon': 'DefaultAddonsSearch.png'})
    listitem.setInfo('video', {
        'plot': 'Search the VTM GO catalogue',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_search, kids=kids), listitem, True)

    if get_setting_as_bool('kids_mode_switching') and not kids:
        listitem = ListItem('Kids Zone', offscreen=True)
        listitem.setArt({'icon': 'DefaultUser.png'})
        listitem.setInfo('video', {
            'plot': 'Go to the Kids Zone',
        })
        xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_index, kids=True), listitem, True)

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/check-credentials')
def check_credentials():
    from resources.lib import vtmgoauth
    auth = vtmgoauth.VtmGoAuth(username=get_setting('email'), password=get_setting('password'))

    try:
        auth.login()
        show_ok_dialog(message='Credentials are correct!')
    except Exception:  # FIXME: This ought to be more specific
        show_ok_dialog(message='Your credentials are not valid!')
        raise

    show_settings()


@plugin.route('/livetv')
def show_livetv():
    kids = _get_kids_mode()
    try:
        _vtmGo = VtmGo(kids=kids)
        channels = _vtmGo.get_live()
    except Exception as ex:
        notification(message=str(ex))
        raise

    for channel in channels:
        listitem = ListItem(channel.name, offscreen=True)

        # Try to use the white icons for thumbnails (used for icons as well)
        if get_cond_visibility('System.HasAddon(resource.images.studios.white)') == 1:
            thumb = 'resource://resource.images.studios.white/{studio}.png'.format(studio=channel.name)
        else:
            thumb = channel.logo

        # Try to use the coloured icons for fanart
        if get_cond_visibility('System.HasAddon(resource.images.studios.coloured)') == 1:
            fanart = 'resource://resource.images.studios.coloured/{studio}.png'.format(studio=channel.name)
        elif get_cond_visibility('System.HasAddon(resource.images.studios.white)') == 1:
            fanart = 'resource://resource.images.studios.white/{studio}.png'.format(studio=channel.name)
        else:
            fanart = channel.logo

        listitem.setInfo('video', {
            'plot': _format_plot(channel),
            'playcount': 0,
            'studio': channel.name,
            'mediatype': channel.mediatype,
        })
        listitem.setArt({
            'icon': channel.logo,
            'fanart': fanart,
            'thumb': thumb,
        })
        listitem.setProperty('IsPlayable', 'true')

        xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_livetv, channel=channel.id) + '?.pvr', listitem)

    # Sort live channels by default like in VTM GO.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/catalog')
@plugin.route('/catalog/<category>')
def show_catalog(category=None):
    kids = _get_kids_mode()
    if category is None:
        # Show all categories
        try:
            _vtmGo = VtmGo(kids=kids)
            categories = _vtmGo.get_categories()
        except Exception as ex:
            notification(message=str(ex))
            raise

        for cat in categories:
            listitem = ListItem(cat.title, offscreen=True)
            listitem.setInfo('video', {
                'plot': '[B]%s[/B]' % cat.title,
            })
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog, category=cat.id, kids=kids), listitem, True)

        # Sort categories by default like in VTM GO.
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)

    else:
        # Show the items of a category
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
                'mediatype': item.mediatype,
            })
            listitem.setProperty('IsPlayable', 'true')

            if item.type == Content.CONTENT_TYPE_MOVIE:
                xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_movie, movie=item.id), listitem)

            elif item.type == Content.CONTENT_TYPE_PROGRAM:
                xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=item.id, kids=kids), listitem, True)

        if category == 'films':
            xbmcplugin.setContent(plugin.handle, 'movies')
        else:
            xbmcplugin.setContent(plugin.handle, 'tvshows')

        # Sort items by label, but don't put folders at the top.
        # Used for A-Z listing or when movies and episodes are mixed.
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/movie/<movie>')
def show_movie(movie):
    kids = _get_kids_mode()
    try:
        _vtmGo = VtmGo(kids=kids)
        movie_obj = _vtmGo.get_movie(movie)
    except Exception as ex:
        notification(message=str(ex))
        raise

    listitem = ListItem(movie_obj.name, offscreen=True)
    listitem.setPath(plugin.url_for(play_movie, movie=movie))
    listitem.setArt({
        'thumb': movie_obj.cover,
        'fanart': movie_obj.cover,
    })
    listitem.setInfo('video', {
        'title': movie_obj.name,
        'plot': _format_plot(movie_obj),
        'duration': movie_obj.duration,
        'year': movie_obj.year,
        'mediatype': movie_obj.mediatype,
        'aired': movie_obj.aired,
    })
    listitem.addStreamInfo('video', {
        'duration': movie_obj.duration,
    })
    listitem.setProperty('IsPlayable', 'true')
    listitem.setContentLookup(False)

    Dialog().info(listitem)


@plugin.route('/program/<program>')
@plugin.route('/program/<program>/<season>')
def show_program(program, season=None):
    kids = _get_kids_mode()
    try:
        _vtmGo = VtmGo(kids=kids)
        program_obj = _vtmGo.get_program(program)
    except Exception as ex:
        notification(message=str(ex))
        raise

    seasons = program_obj.seasons.values()

    # If more than one season and no season provided, give a season-overview
    if season is None and len(seasons) > 1:

        # Add an '* All seasons' entry when configured in Kodi
        if get_global_setting('videolibrary.showallitems') is True:
            listitem = ListItem('* All seasons', offscreen=True)
            listitem.setArt({
                'thumb': program_obj.cover,
                'fanart': program_obj.cover,
            })
            listitem.setInfo('video', {
                'tvshowtitle': program_obj.name,
                'title': 'All seasons',
                'subtitle': program_obj.description,
                'plot': _format_plot(program_obj),
                'set': program_obj.name,
            })
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=program, season='all', kids=kids), listitem, True)

        for s in program_obj.seasons.values():
            listitem = ListItem('Season %d' % s.number, offscreen=True)
            listitem.setArt({
                'thumb': s.cover,
                'fanart': program_obj.cover,
            })
            listitem.setInfo('video', {
                'tvshowtitle': program_obj.name,
                'title': 'Season %d' % s.number,
                'subtitle': program_obj.description,
                'plot': _format_plot(program_obj),
                'set': program_obj.name,
                'season': season,
            })
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=program, season=s.number), listitem, True)
        xbmcplugin.setContent(plugin.handle, 'tvshows')

        # Sort by label. Some programs return seasons unordered.
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(plugin.handle)
        return

    if season != 'all' and season is not None:
        # Use the season that was selected
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
                'subtitle': program_obj.description,
                'plot': _format_plot(episode),
                'duration': episode.duration,
                'season': episode.season,
                'episode': episode.number,
                'mediatype': episode.mediatype,
                'set': program_obj.name,
                'studio': episode.channel,
                'aired': episode.aired,
            })
            listitem.addStreamInfo('video', {
                'duration': episode.duration,
            })
            listitem.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_episode, episode=episode.id), listitem)

    xbmcplugin.setContent(plugin.handle, 'episodes')

    # Sort by episode number by default. Takes seasons into account.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DURATION)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/youtube')
def show_youtube():
    kids = _get_kids_mode()
    from resources.lib import YOUTUBE
    for entry in YOUTUBE:
        # Skip non-kids channels when we are in kids mode.
        if kids and entry.get('kids') is False:
            continue

        # Try to use the white icons for thumbnails (used for icons as well)
        if get_cond_visibility('System.HasAddon(resource.images.studios.white)') == 1:
            thumb = 'resource://resource.images.studios.white/{studio}.png'.format(**entry)
        else:
            thumb = 'DefaultTags.png'

        # Try to use the coloured icons for fanart
        if get_cond_visibility('System.HasAddon(resource.images.studios.coloured)') == 1:
            fanart = 'resource://resource.images.studios.coloured/{studio}.png'.format(**entry)
        elif get_cond_visibility('System.HasAddon(resource.images.studios.white)') == 1:
            fanart = 'resource://resource.images.studios.white/{studio}.png'.format(**entry)
        else:
            fanart = 'DefaultTags.png'

        listitem = ListItem(entry.get('label'), offscreen=True)
        listitem.setInfo('video', {
            'plot': 'Watch [B]%(label)s[/B] on YouTube' % entry,
            'studio': entry.get('studio'),
            'mediatype': 'video',
        })
        listitem.setArt({
            'icon': 'DefaultTags.png',
            'fanart': fanart,
            'thumb': thumb,
        })
        xbmcplugin.addDirectoryItem(plugin.handle, entry.get('path'), listitem, True)

    # Sort by default like in our dict.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/search')
def show_search():
    kids = _get_kids_mode()

    # Ask for query
    keyboard = xbmc.Keyboard('', 'Search')
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
    for item in items:
        listitem = ListItem(item.title, offscreen=True)

        if item.type == Content.CONTENT_TYPE_MOVIE:
            listitem.setInfo('video', {
                'mediatype': 'movie',
            })
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_movie, movie=item.id), listitem)

        elif item.type == Content.CONTENT_TYPE_PROGRAM:
            listitem.setInfo('video', {
                'mediatype': None,  # This shows a folder icon
            })
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=item.id, kids=kids), listitem, True)

    xbmcplugin.setContent(plugin.handle, 'tvshows')

    # Sort like we get our results back.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/play/livetv/<channel>')
def play_livetv(channel):
    _stream('channels', channel)


@plugin.route('/play/movie/<movie>')
def play_movie(movie):
    _stream('movies', movie)


@plugin.route('/play/episode/<episode>')
def play_episode(episode):
    _stream('episodes', episode)


def _format_plot(obj):
    plot = ''

    # Add program name to plot
    if hasattr(obj, 'name') or (hasattr(obj, 'legal') and obj.legal):
        if hasattr(obj, 'name'):
            plot += '[B]{name}[/B] '.format(name=obj.name)
        if hasattr(obj, 'legal') and obj.legal:
            plot += '[COLOR gray]'
            for icon in obj.legal:
                plot += '[%s]' % icon
            plot += '[/COLOR]'
        plot += '\n'

    if hasattr(obj, 'geoblocked') and obj.geoblocked:
        plot += '[COLOR red]Geo-blocked[/COLOR]\n'

    if hasattr(obj, 'remaining') and obj.remaining is not None:
        if obj.remaining == 0:
            plot += '[COLOR blue]Available until midnight[/COLOR]\n'
        elif obj.remaining == 1:
            plot += '[COLOR blue]One day remaining[/COLOR]\n'
        elif obj.remaining / 365 > 5:
            pass  # If it is available for more than 5 years, do not show
        elif obj.remaining / 365 > 2:
            plot += '[COLOR blue]{years} years remaining[/COLOR]\n'.format(years=int(obj.remaining / 365))
        elif obj.remaining / 30.5 > 3:
            plot += '[COLOR blue]{months} months remaining[/COLOR]\n'.format(months=int(obj.remaining / 30.5))
        else:
            plot += '[COLOR blue]{days} days remaining[/COLOR]\n'.format(days=obj.remaining)

    if plot:
        plot += '\n'

    if hasattr(obj, 'description'):
        plot += obj.description

    if hasattr(obj, 'epg'):
        if obj.epg:
            plot += '[COLOR yellow][B]Now:[/B] %s - %s\n' % (
                obj.epg[0].start.strftime('%H:%M'),
                obj.epg[0].end.strftime('%H:%M'),
            )
            plot += '» %s[/COLOR]\n' % obj.epg[0].title

        if len(obj.epg) > 1:
            plot += '[B]Next:[/B] %s - %s\n' % (
                obj.epg[1].start.strftime('%H:%M'),
                obj.epg[1].end.strftime('%H:%M'),
            )
            plot += '» %s\n' % obj.epg[1].title

    return plot


def _stream(strtype, strid):
    # Get url
    _vtmgostream = vtmgostream.VtmGoStream()
    resolved_stream = _vtmgostream.get_stream(strtype, strid)
    if resolved_stream is None:  # If no stream is available (i.e. geo-blocked)
        return

    # Create listitem
    listitem = ListItem(path=resolved_stream.url, offscreen=True)

    # Add video info
    listitem.setInfo('video', {
        'title': resolved_stream.title,
        'tvshowtitle': resolved_stream.program,
        'duration': resolved_stream.duration,
    })
    listitem.addStreamInfo('video', {
        'duration': resolved_stream.duration,
    })

    # Add subtitle info
    listitem.setSubtitles(resolved_stream.subtitles)
    listitem.addStreamInfo('subtitle', {
        'language': 'nl',
    })

    listitem.setProperty('IsPlayable', 'true')
    listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    listitem.setMimeType('application/dash+xml')
    listitem.setContentLookup(False)

    if strtype == 'channels':
        listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
    try:
        from inputstreamhelper import Helper
    except ImportError:
        show_ok_dialog(message='Please reboot Kodi')
        return
    is_helper = Helper('mpd', drm='com.widevine.alpha')
    if is_helper.check_inputstream():
        listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.adaptive.license_key',
                             _vtmgostream.create_license_key(resolved_stream.license_url, key_headers={
                                 'User-Agent': 'ANVSDK Android/5.0.39 (Linux; Android 6.0.1; Nexus 5)',
                             }))

        xbmcplugin.setResolvedUrl(plugin.handle, True, listitem)


def _get_kids_mode():

    if get_setting_as_bool('kids_zone_forced'):
        return True

    # kids will contain a string of 'True' or 'False'
    kids = plugin.args.get('kids')
    if kids:
        return True if kids[0] == 'True' else False
    return False


def run(params):
    plugin.run(params)
