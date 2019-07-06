from __future__ import division

import logging

import routing
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from xbmcgui import ListItem

from resources.lib import kodilogging
from resources.lib import kodiutils
from resources.lib import vtmgostream
from resources.lib.vtmgo import VtmGo, Content

ADDON = xbmcaddon.Addon()
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

        xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_live, id=channel.id) + '?.pvr', listitem)

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/catalog')
@plugin.route('/catalog/<category>')
def show_catalog(category=None):
    if not category:
        # Show all categories
        try:
            _vtmGo = VtmGo()
            categories = _vtmGo.get_categories()
        except Exception as ex:
            kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
            raise

        for category in categories:
            listitem = ListItem(category.title, offscreen=True)
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_catalog, category=category.id), listitem, True)

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

            if item.type == Content.CONTENT_TYPE_MOVIE:
                # TODO: Doesn't seem to start the stream when I open it in an popup.
                # xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_movie, id=item.id), listitem)
                xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_movie, id=item.id), listitem)
            elif item.type == Content.CONTENT_TYPE_PROGRAM:
                xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, id=item.id), listitem, True)

    xbmcplugin.setContent(plugin.handle, 'tvshows')
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/movie/<id>')
def show_movie(id):
    try:
        _vtmGo = VtmGo()
        movie = _vtmGo.get_movie(id)
    except Exception as ex:
        kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
        raise

    listitem = ListItem(movie.name, offscreen=True)
    listitem.setPath(plugin.url_for(play_movie, id=id))
    listitem.setArt({
        'poster': movie.cover,
        'fanart': movie.cover,
    })
    listitem.setInfo('video', {
        'title': movie.name,
        'plot': movie.description,
        'duration': movie.duration,
        'year': movie.year,
    })
    listitem.setProperty('IsPlayable', 'true')
    listitem.setContentLookup(False)

    xbmcgui.Dialog().info(listitem)


@plugin.route('/program/<id>')
@plugin.route('/program/<id>/<season>')
def show_program(id, season=None):
    try:
        _vtmGo = VtmGo()
        program = _vtmGo.get_program(id)
    except Exception as ex:
        kodiutils.notification(ADDON.getAddonInfo('name'), ex.message)
        raise

    if not season:
        for season in program.seasons.values():
            listitem = ListItem('Season %d' % season.number, offscreen=True)
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, id=id, season=season.number), listitem, True)
    else:
        for episode in program.seasons[int(season)].episodes.values():
            listitem = ListItem(episode.name, offscreen=True)
            listitem.setInfo('video', {
                'title': episode.name,
                'plot': episode.description,
                'duration': episode.duration,
            })
            listitem.setArt({
                'poster': episode.cover,
                'fanart': episode.cover,
            })
            listitem.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_episode, id=episode.id), listitem)
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
            # xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_movie, id=item.id), listitem)
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(play_movie, id=item.id), listitem)
        elif item.type == Content.CONTENT_TYPE_PROGRAM:
            xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_program, id=item.id), listitem, True)

    xbmcplugin.setContent(plugin.handle, 'tvshows')
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/play/live/<id>')
def play_live(id):
    _stream('channels', id)


@plugin.route('/play/movie/<id>')
def play_movie(id):
    _stream('movies', id)


@plugin.route('/play/episode/<id>')
def play_episode(id):
    _stream('episodes', id)


def _stream(type, id):
    # Get url
    _vtmgostream = vtmgostream.VtmGoStream()
    resolved_stream = _vtmgostream.get_stream(type, id)

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

    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem)


def run(params):
    plugin.run(params)
