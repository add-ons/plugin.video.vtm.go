# -*- coding: utf-8 -*-
""" Addon code """

from __future__ import absolute_import, division, unicode_literals

import routing

from resources.lib import GeoblockedException, UnavailableException
from resources.lib.kodiwrapper import KodiWrapper, TitleItem
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth, InvalidLoginException, LoginErrorException
from resources.lib.vtmgo.vtmgoepg import VtmGoEpg
from resources.lib.vtmgo.vtmgostream import VtmGoStream

routing = routing.Plugin()
kodi = KodiWrapper(globals())


@routing.route('/')
def show_index():
    """ Main menu entrypoint """
    from resources.lib.menu_main import MenuMain
    MenuMain(kodi).show_mainmenu()


@routing.route('/livetv')
def show_livetv():
    """ Shows Live TV channels """
    from resources.lib.menu_channels import MenuChannels
    MenuChannels(kodi).show_livetv()


@routing.route('/tvguide')
def show_tvguide():
    """ Shows the TV guide """
    from resources.lib.menu_channels import MenuChannels
    MenuChannels(kodi).show_tvguide()


@routing.route('/tvguide/<channel>')
def show_tvguide_channel(channel):
    """ Shows the dates in the tv guide """
    from resources.lib.menu_channels import MenuChannels
    MenuChannels(kodi).show_tvguide_channel(channel)


@routing.route('/tvguide/<channel>/<date>')
def show_tvguide_detail(channel=None, date=None):
    """ Shows the programs of a specific date in the tv guide """
    from resources.lib.menu_channels import MenuChannels
    MenuChannels(kodi).show_tvguide_detail(channel, date)


@routing.route('/catalog')
def show_catalog():
    """ Show the catalog """
    from resources.lib.menu_catalog import MenuCatalog
    MenuCatalog(kodi).show_catalog()


@routing.route('/catalog/category/<category>')
def show_catalog_category(category):
    """ Show a category in the catalog """
    from resources.lib.menu_catalog import MenuCatalog
    MenuCatalog(kodi).show_catalog_category(category)


@routing.route('/catalog/program/<program>')
def show_catalog_program(program):
    """ Show a program from the catalog """
    from resources.lib.menu_catalog import MenuCatalog
    MenuCatalog(kodi).show_catalog_program(program)


@routing.route('/program/<program>/<season>')
def show_catalog_program_season(program, season):
    """ Show a program from the catalog """
    from resources.lib.menu_catalog import MenuCatalog
    MenuCatalog(kodi).show_catalog_program_season(program, season)


@routing.route('/catalog/recommendations')
def show_recommendations():
    """ Shows the programs of a specific date in the tv guide """
    from resources.lib.menu_catalog import MenuCatalog
    MenuCatalog(kodi).show_catalog_recommendations()


@routing.route('/catalog/recommendations/<category>')
def show_recommendations_category(category):
    """ Show the items in a recommendations category """
    from resources.lib.menu_catalog import MenuCatalog
    MenuCatalog(kodi).show_catalog_recommendations_category(category)


@routing.route('/catalog/mylist')
def show_mylist():
    """ Show the items in "My List" """
    from resources.lib.menu_catalog import MenuCatalog
    MenuCatalog(kodi).show_catalog_mylist()


@routing.route('/catalog/mylist/add/<video_type>/<content_id>')
def mylist_add(video_type, content_id):
    """ Add an item to "My List" """
    vtm_go = VtmGo(kodi)
    vtm_go.add_mylist(video_type, content_id)
    kodi.end_of_directory()


@routing.route('/catalog/mylist/del/<video_type>/<content_id>')
def mylist_del(video_type, content_id):
    """ Remove an item from "My List" """
    vtm_go = VtmGo(kodi)
    vtm_go.del_mylist(video_type, content_id)
    kodi.end_of_directory()
    kodi.container_refresh()


@routing.route('/catalog/continuewatching')
def show_continuewatching():
    """ Show the items in "Continue Watching" """
    from resources.lib.menu_catalog import MenuCatalog
    MenuCatalog(kodi).show_catalog_continuewatching()


@routing.route('/program-epg/<program>')
def show_program_from_epg(program):
    """ Play a program based on the channel and information from the EPG. """
    _vtmGoEpg = VtmGoEpg(kodi)
    details = _vtmGoEpg.get_details(channel='vtm', program_type='episodes', epg_id=program)
    if not details:
        kodi.show_ok_dialog(heading=kodi.localize(30711), message=kodi.localize(30713))  # The requested video was not found in the guide.
        return

    show_catalog_program(details.program_uuid)


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
    from resources.lib.menu_search import MenuSearch
    MenuSearch(kodi).show_search(query)


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

    except LoginErrorException as e:
        kodi.show_ok_dialog(message=kodi.localize(30702, code=e.code))  # Unknown error while logging in: {code}

    kodi.open_settings()


@routing.route('/metadata/update')
def metadata_update():
    """ Update the metadata for the listings (called from settings) """
    from resources.lib.metadata import Metadata
    Metadata(kodi).update()


@routing.route('/metadata/clean')
def metadata_clean():
    """ Clear metadata (called from settings) """
    from resources.lib.metadata import Metadata
    Metadata(kodi).clean()


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


def run(params):
    """ Run the routing plugin """
    routing.run(params)
