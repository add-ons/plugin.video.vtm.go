# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals
import logging

import xbmc
from xbmcaddon import Addon
import xbmcplugin
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
    item = ListItem('Live TV', offscreen=True)
    item.setArt({'icon': 'DefaultAddonPVRClient.png'})
    item.setInfo('video', {
        'plot': 'Watch Live TV',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_live), item, True)

    item = ListItem('Catalogue', offscreen=True)
    item.setArt({'icon': 'DefaultMovies.png'})
    item.setInfo('video', {
        'plot': 'Watch TV Shows and Movies',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog), item, True)

    item = ListItem('Search', offscreen=True)
    item.setArt({'icon': 'DefaultAddonsSearch.png'})
    item.setInfo('video', {
        'plot': 'Search the Catalogue',
    })
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_search), item, True)

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
                description = 'Now: ' + channel.epg[0].start.strftime('%H:%M') + ' - ' + channel.epg[0].end.strftime('%H:%M') + '\n'
                description += channel.epg[0].title + '\n'
                description += '\n'
        except IndexError:
            pass

        try:
            if channel.epg[1]:
                description += 'Next: ' + channel.epg[1].start.strftime('%H:%M') + ' - ' + channel.epg[1].end.strftime('%H:%M') + '\n'
                description += channel.epg[1].title + '\n'
                description += '\n'
        except IndexError:
            pass

        listitem.setInfo('video', {
            'plot': description,
            'playcount': 0,
        })
        listitem.setProperty('IsPlayable', 'true')

        xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_live, channel=channel.id) + '?.pvr', listitem)

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
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
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog, category=cat.id), listitem, True)

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
                'poster': item.cover,
            })
            listitem.setInfo('video', {
                'plot': item.description,
            })
            listitem.setProperty('IsPlayable', 'true')

            if item.type == Content.CONTENT_TYPE_MOVIE:
                # TODO: Doesn't seem to start the stream when I open it in an popup.
                # xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_movie, movie=item.id), listitem)
                xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_movie, movie=item.id), listitem)
            elif item.type == Content.CONTENT_TYPE_PROGRAM:
                xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=item.id), listitem, True)

    xbmcplugin.setContent(plugin.handle, 'tvshows')
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/movie/<movie>')
def show_movie(movie):
    try:
        _vtmGo = VtmGo()
        movie_obj = _vtmGo.get_movie(movie)
    except Exception as ex:
        kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
        raise

    listitem = ListItem(movie.name, offscreen=True)
    listitem.setPath(plugin.url_for(play_movie, movie=movie))
    listitem.setArt({
        'poster': movie.cover,
        'fanart': movie.cover,
    })
    listitem.setInfo('video', {
        'title': movie_obj.name,
        'plot': movie_obj.description,
        'duration': movie_obj.duration,
        'year': movie_obj.year,
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

    if season is None:
        for s in program_obj.seasons.values():
            listitem = ListItem('Season %d' % s.number, offscreen=True)
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=program, season=s.number), listitem, True)
    else:
        for episode in program_obj.seasons[int(season)].episodes.values():
            listitem = ListItem(episode.name, offscreen=True)
            listitem.setArt({
                'poster': episode.cover,
                'fanart': episode.cover,
            })
            listitem.setInfo('video', {
                'title': episode.name,
                'plot': episode.description,
                'duration': episode.duration,
            })
            listitem.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_episode, episode=episode.id), listitem)
        xbmcplugin.setContent(plugin.handle, 'tvshows')

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
            # TODO: Doesn't seem to start the stream when I open it in an popup.
            # xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_movie, movie_id=item.id), listitem)
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_movie, movie=item.id), listitem)
        elif item.type == Content.CONTENT_TYPE_PROGRAM:
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, program=item.id), listitem, True)

    xbmcplugin.setContent(plugin.handle, 'tvshows')
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
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


def _stream(strtype, strid):
    # Get url
    _vtmgostream = vtmgostream.VtmGoStream()
    resolved_stream = _vtmgostream.get_stream(strtype, strid)

    # Create listitem
    listitem = ListItem(path=resolved_stream.url, offscreen=True)
    listitem.setInfo('video', {
        'title': resolved_stream.title,
        'tvshowtitle': resolved_stream.program,
        'duration': resolved_stream.duration,
    })
    listitem.setProperty('IsPlayable', 'true')
    listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    listitem.setProperty('inputstream.adaptive.license_key',
                         _vtmgostream.create_license_key(resolved_stream.license_url, key_headers={
                             'User-Agent': 'ANVSDK Android/5.0.39 (Linux; Android 6.0.1; Nexus 5)',
                         }))
    listitem.setMimeType('application/dash+xml')
    listitem.setContentLookup(False)
    listitem.setSubtitles(resolved_stream.subtitles)

    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem)


def run(params):
    plugin.run(params)
