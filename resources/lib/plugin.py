# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import logging

import xbmc
import xbmcplugin
from xbmcaddon import Addon
from xbmcgui import Dialog, ListItem

import routing
from resources.lib import kodilogging
from resources.lib import kodiutils
from resources.lib import vtmgostream
from resources.lib.vtmgo import VtmGo, Content

ADDON = Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()


@plugin.route('/')
def index():
    listitem = ListItem("A-Z", offscreen=True)
    listitem.setArt({'icon': 'DefaultMovieTitle.png'})
    listitem.setInfo('video', {
        'plot': 'Alphabetically sorted list of programs',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog, category='all'), listitem, True)

    listitem = ListItem('Catalogue', offscreen=True)
    listitem.setArt({'icon': 'DefaultGenre.png'})
    listitem.setInfo('video', {
        'plot': 'TV Shows and Movies listed by category',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog), listitem, True)

    listitem = ListItem('Live TV', offscreen=True)
    listitem.setArt({'icon': 'DefaultAddonPVRClient.png'})
    listitem.setInfo('video', {
        'plot': 'Watch channels live via Internet',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_live), listitem, True)

    # Only provide YouTube option when plugin.video.youtube is available
    if xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)') != 0:
        listitem = ListItem('YouTube', offscreen=True)
        listitem.setArt({'icon': 'DefaultTags.png'})
        listitem.setInfo('video', {
            'plot': 'Watch YouTube content',
        })
        xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_youtube), listitem, True)

    listitem = ListItem('Search', offscreen=True)
    listitem.setArt({'icon': 'DefaultAddonsSearch.png'})
    listitem.setInfo('video', {
        'plot': 'Search the VTM GO catalogue',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_search), listitem, True)

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/live')
def show_live():
    try:
        _vtmGo = VtmGo()
        channels = _vtmGo.get_live()
    except Exception as ex:
        kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
        raise

    for channel in channels:
        listitem = ListItem(channel.name, offscreen=True)
        listitem.setArt({
            'icon': channel.logo,
        })

        description = ''
        try:
            if channel.epg[0]:
                description = 'Now: %s - %s\n' % (
                    channel.epg[0].start.strftime('%H:%M'),
                    channel.epg[0].end.strftime('%H:%M')
                )
                description += channel.epg[0].title + '\n'
                description += '\n'
        except IndexError:
            pass

        try:
            if channel.epg[1]:
                description += 'Next: %s - %s\n' % (
                    channel.epg[1].start.strftime('%H:%M'),
                    channel.epg[1].end.strftime('%H:%M')
                )
                description += channel.epg[1].title + '\n'
                description += '\n'
        except IndexError:
            pass

        listitem.setInfo('video', {
            'plot': description,
            'playcount': 0,
            'studio': channel.name,
            'mediatype': channel.mediatype,
        })
        listitem.setProperty('IsPlayable', 'true')

        xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_live, channel=channel.id) + '?.pvr', listitem)

    # Sort live channels by default like in VTM GO.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/catalog')
@plugin.route('/catalog/<category>')
def show_catalog(category=None):
    if category is None:
        # Show all categories
        try:
            _vtmGo = VtmGo()
            categories = _vtmGo.get_categories()
        except Exception as ex:
            kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
            raise

        for cat in categories:
            listitem = ListItem(cat.title, offscreen=True)
            listitem.setInfo('video', {
                'plot': '[B]%s[/B]' % cat.title,
            })
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog, category=cat.id), listitem, True)

        # Sort categories by default like in VTM GO.
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)

    else:
        # Show the items of a category
        try:
            _vtmGo = VtmGo()
            items = _vtmGo.get_items(category)
        except Exception as ex:
            kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
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
                xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=item.id), listitem, True)

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
    try:
        _vtmGo = VtmGo()
        movie_obj = _vtmGo.get_movie(movie)
    except Exception as ex:
        kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
        raise

    listitem = ListItem(movie_obj.name, offscreen=True)
    listitem.setPath(plugin.url_for(play_movie, movie=movie))
    listitem.setArt({
        'thumb': movie_obj.cover,
        'fanart': movie_obj.cover,
    })
    listitem.setInfo('video', {
        'title': movie_obj.name,
        'plot': _format_remaining(movie_obj.remaining) + movie_obj.description,
        'duration': movie_obj.duration,
        'year': movie_obj.year,
        'mediatype': movie_obj.mediatype,
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
    try:
        _vtmGo = VtmGo()
        program_obj = _vtmGo.get_program(program)
    except Exception as ex:
        kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
        raise

    seasons = program_obj.seasons.values()

    # If more than one season and no season provided, give a season-overview
    if season is None and len(seasons) > 1:

        # Add an '* All seasons' entry when configured in Kodi
        if kodiutils.get_global_setting('videolibrary.showallitems') is True:
            listitem = ListItem('* All seasons', offscreen=True)
            listitem.setArt({
                'thumb': program_obj.cover,
                'fanart': program_obj.cover,
            })
            listitem.setInfo('video', {
                'tvshowtitle': program_obj.name,
                'title': 'All seasons',
                'subtitle': program_obj.description,
                'plot': '[B]%s[/B]\n%s' % (program_obj.name, program_obj.description),
                'set': program_obj.name,
            })
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=program, season='all'), listitem, True)

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
                'plot': '[B]%s[/B]\n%s' % (program_obj.name, program_obj.description),
                'set': program_obj.name,
                'season': season,
            })
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=program, season=s.number), listitem, True)
        xbmcplugin.setContent(plugin.handle, 'tvshows')

        # Sort by label. Some programs return seasons unordered.
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(plugin.handle)
        return

    elif season != 'all' and season is not None:
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
                'plot': _format_remaining(episode.remaining) + episode.description,
                'duration': episode.duration,
                'season': episode.season,
                'episode': episode.number,
                'mediatype': episode.mediatype,
                'set': program_obj.name,
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
    from resources.lib import YOUTUBE
    for entry in YOUTUBE:
        listitem = ListItem(entry.get('label'), offscreen=True)
        listitem.setInfo('video', {
            'plot': 'Watch [B]%(label)s[/B] on YouTube' % entry,
            'studio': entry.get('studio'),
            'mediatype': 'video',
        })
        xbmcplugin.addDirectoryItem(plugin.handle, entry.get('path'), listitem, True)

    # Sort by default like in our dict.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/search')
def show_search():
    # Ask for query
    keyboard = xbmc.Keyboard('', 'Search')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return
    query = keyboard.getText()

    try:
        # Do search
        _vtmGo = VtmGo()
        items = _vtmGo.do_search(query)
    except Exception as ex:
        kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
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
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=item.id), listitem, True)

    xbmcplugin.setContent(plugin.handle, 'tvshows')

    # Sort like we get our results back.
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/play/live/<channel>')
def play_live(channel):
    _stream('channels', channel)


@plugin.route('/play/movie/<movie>')
def play_movie(movie):
    _stream('movies', movie)


@plugin.route('/play/episode/<episode>')
def play_episode(episode):
    _stream('episodes', episode)


def _format_remaining(days):
    if days is None:
        return ''
    elif days == 0:
        availability = 'Available until midnight'
    elif days == 1:
        availability = '%d day remaining' % days
    else:
        availability = '%d days remaining' % days

    return '[COLOR silver]%s[/COLOR]\n\n' % availability


def _stream(strtype, strid):
    # Get url
    _vtmgostream = vtmgostream.VtmGoStream()
    resolved_stream = _vtmgostream.get_stream(strtype, strid)

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
    listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    listitem.setProperty('inputstream.adaptive.license_key',
                         _vtmgostream.create_license_key(resolved_stream.license_url, key_headers={
                             'User-Agent': 'ANVSDK Android/5.0.39 (Linux; Android 6.0.1; Nexus 5)',
                         }))

    if strtype == 'channels':
        listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')

    listitem.setMimeType('application/dash+xml')
    listitem.setContentLookup(False)

    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem)


def run(params):
    plugin.run(params)
