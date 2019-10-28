# -*- coding: utf-8 -*-
""" Library around all Kodi functions """

from __future__ import absolute_import, division, unicode_literals

from contextlib import contextmanager

import xbmc
import xbmcplugin
from xbmcaddon import Addon

SORT_METHODS = dict(
    label=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS,
    episode=xbmcplugin.SORT_METHOD_EPISODE,
    duration=xbmcplugin.SORT_METHOD_DURATION,
    unsorted=xbmcplugin.SORT_METHOD_UNSORTED,
)

LOG_DEBUG = xbmc.LOGDEBUG
LOG_INFO = xbmc.LOGINFO
LOG_NOTICE = xbmc.LOGNOTICE
LOG_WARNING = xbmc.LOGWARNING
LOG_ERROR = xbmc.LOGERROR
LOG_FATAL = xbmc.LOGFATAL


def to_unicode(text, encoding='utf-8'):
    """ Force text to unicode """
    return text.decode(encoding) if isinstance(text, bytes) else text


def from_unicode(text, encoding='utf-8'):
    """ Force unicode to text """
    import sys
    if sys.version_info.major == 2 and isinstance(text, unicode):  # noqa: F821; pylint: disable=undefined-variable
        return text.encode(encoding)
    return text


def has_socks():
    """ Test if socks is installed, and remember this information """
    if hasattr(has_socks, 'installed'):
        return has_socks.installed
    try:
        import socks  # noqa: F401; pylint: disable=unused-variable,unused-import
        has_socks.installed = True
        return True
    except ImportError:
        has_socks.installed = False
        return None  # Detect if this is the first run


class SafeDict(dict):
    """ A safe dictionary implementation that does not break down on missing keys """

    def __missing__(self, key):
        """ Replace missing keys with the original placeholder """
        return '{' + key + '}'


class TitleItem:
    """ This helper object holds all information to be used with Kodi xbmc's ListItem object """

    def __init__(self, title, path=None, art_dict=None, info_dict=None, prop_dict=None, stream_dict=None, context_menu=None, subtitles_path=None,
                 is_playable=False):
        """ The constructor for the TitleItem class
        :type title: str
        :type path: str
        :type art_dict: dict
        :type info_dict: dict
        :type prop_dict: dict
        :type stream_dict: dict
        :type context_menu: list[tuple[str, str]]
        :type subtitles_path: list[str]
        :type is_playable: bool
        """
        self.title = title
        self.path = path
        self.art_dict = art_dict
        self.info_dict = info_dict
        self.stream_dict = stream_dict
        self.prop_dict = prop_dict
        self.context_menu = context_menu
        self.subtitles_path = subtitles_path
        self.is_playable = is_playable

    def __repr__(self):
        return "%r" % self.__dict__


class KodiWrapper:
    """ A wrapper around all Kodi functionality """

    def __init__(self, addon=None):
        """ Initialize the Kodi wrapper """
        if addon:
            self.addon = addon
            self.routing = addon['routing']
            self._handle = self.routing.handle
            self._url = self.routing.base_url
        else:
            self.addon = None
            self.routing = None
            self._handle = None
            self._url = None
        self._addon = Addon()
        self._system_locale_works = None
        self._addon_name = self._addon.getAddonInfo('name')
        self._addon_id = self._addon.getAddonInfo('id')
        self._global_debug_logging = self.get_global_setting('debug.showloginfo')  # Returns a boolean
        self._debug_logging = self.get_setting_as_bool('debug_logging')
        self._cache_path = self.get_userdata_path() + 'cache/'

    def url_for(self, name, *args, **kwargs):
        """ Wrapper for routing.url_for() to lookup by name """
        kwargs = {k: v for k, v in kwargs.items() if v is not None}  # Strip out empty kwargs
        return self.routing.url_for(self.addon[name], *args, **kwargs)

    def redirect(self, url):
        """ Wrapper for routing.redirect() so it also works with urls """
        return self.routing.redirect(url.replace('plugin://' + self._addon_id, ''))

    def show_listing(self, title_items, category=None, sort='unsorted', content=None, cache=True):
        """ Show a virtual directory in Kodi """
        if content:
            # content is one of: files, songs, artists, albums, movies, tvshows, episodes, musicvideos, videos, images, games
            xbmcplugin.setContent(self._handle, content=content)

        # Jump through hoops to get a stable breadcrumbs implementation
        category_label = ''
        if category:
            if not content:
                category_label = self._addon_name + ' / '
            if self.kids_mode():
                category_label += 'KIDS / '
            if isinstance(category, int):
                category_label += self.localize(category)
            else:
                category_label += category
        elif not content:
            category_label = self._addon_name
            if self.kids_mode():
                category_label += ' / KIDS'

        xbmcplugin.setPluginCategory(handle=self._handle, category=category_label)

        # Add all sort methods to GUI (start with preferred)
        xbmcplugin.addSortMethod(handle=self._handle, sortMethod=SORT_METHODS[sort])
        for key in sorted(SORT_METHODS):
            if key != sort:
                xbmcplugin.addSortMethod(handle=self._handle, sortMethod=SORT_METHODS[key])

        # Add the listings
        listing = []
        for title_item in title_items:
            list_item = self._generate_listitem(title_item)

            is_folder = bool(not title_item.is_playable and title_item.path)
            url = title_item.path if title_item.path else None
            listing.append((url, list_item, is_folder))

        succeeded = xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self._handle, succeeded, cacheToDisc=cache)

    @staticmethod
    def _generate_listitem(title_item):
        """ Generate a ListItem from a TitleItem """
        from xbmcgui import ListItem

        # Three options:
        #  - item is a virtual directory/folder (not playable, path)
        #  - item is a playable file (playable, path)
        #  - item is non-actionable item (not playable, no path)
        is_folder = bool(not title_item.is_playable and title_item.path)
        is_playable = bool(title_item.is_playable and title_item.path)

        list_item = ListItem(label=title_item.title, path=title_item.path)

        if title_item.prop_dict:
            list_item.setProperties(title_item.prop_dict)
        list_item.setProperty(key='IsPlayable', value='true' if is_playable else 'false')

        list_item.setIsFolder(is_folder)

        if title_item.art_dict:
            list_item.setArt(title_item.art_dict)

        if title_item.info_dict:
            # type is one of: video, music, pictures, game
            list_item.setInfo(type='video', infoLabels=title_item.info_dict)

        if title_item.stream_dict:
            # type is one of: video, audio, subtitle
            list_item.addStreamInfo('video', title_item.stream_dict)

        if title_item.context_menu:
            list_item.addContextMenuItems(title_item.context_menu)

        return list_item

    def play(self, title_item, license_key=None):
        """ Play the passed TitleItem.
        :type title_item: TitleItem
        :type license_key: string
        """
        play_item = self._generate_listitem(title_item)
        play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        play_item.setProperty('inputstream.adaptive.max_bandwidth', str(self.get_max_bandwidth() * 1000))
        play_item.setProperty('network.bandwidth', str(self.get_max_bandwidth() * 1000))
        play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        play_item.setMimeType('application/dash+xml')
        play_item.setContentLookup(False)

        if license_key is not None:
            play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            play_item.setProperty('inputstream.adaptive.license_key', license_key)

        if title_item.subtitles_path:
            play_item.setSubtitles(title_item.subtitles_path)

        # To support video playback directly from RunPlugin() we need to use xbmc.Player().play instead of
        # setResolvedUrl that only works with PlayMedia() or with internal playable menu items
        xbmcplugin.setResolvedUrl(self._handle, True, listitem=play_item)

        if self.get_setting_as_bool('showsubtitles'):
            while not xbmc.Player().isPlaying() and not xbmc.Monitor().abortRequested():
                xbmc.sleep(100)
            xbmc.Player().showSubtitles(True)

    @staticmethod
    def get_search_string(heading='', message=''):
        """ Ask the user for a search string """
        search_string = None
        keyboard = xbmc.Keyboard(message, heading)
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_string = to_unicode(keyboard.getText())
        return search_string

    @staticmethod
    def show_context_menu(items):
        """ Show Kodi's context menu dialog """
        from xbmcgui import Dialog
        return Dialog().contextmenu(items)

    def show_ok_dialog(self, heading='', message=''):
        """ Show Kodi's OK dialog """
        from xbmcgui import Dialog
        if not heading:
            heading = self._addon.getAddonInfo('name')
        return Dialog().ok(heading=heading, line1=message)

    def show_notification(self, heading='', message='', icon='info', time=8000):
        """ Show a Kodi notification """
        from xbmcgui import Dialog
        if not heading:
            heading = self._addon.getAddonInfo('name')
        Dialog().notification(heading=heading, message=message, icon=icon, time=time)

    def show_multiselect(self, heading='', options=None, autoclose=0, preselect=None, use_details=False):
        """ Show a Kodi multi-select dialog """
        from xbmcgui import Dialog
        if not heading:
            heading = self._addon.getAddonInfo('name')
        return Dialog().multiselect(heading=heading, options=options, autoclose=autoclose, preselect=preselect, useDetails=use_details)

    def show_progress(self, heading='', message=''):
        """ Show a Kodi progress dialog """
        from xbmcgui import DialogProgress
        if not heading:
            heading = self._addon.getAddonInfo('name')
        progress = DialogProgress()
        progress.create(heading=heading, line1=message)
        return progress

    def show_progress_background(self, heading='', message=''):
        """ Show a Kodi progress dialog """
        from xbmcgui import DialogProgressBG
        if not heading:
            heading = self._addon.getAddonInfo('name')
        progress = DialogProgressBG()
        progress.create(heading=heading, message=message)
        return progress

    def set_locale(self):
        """ Load the proper locale for date strings """
        import locale
        locale_lang = self.get_global_setting('locale.language').split('.')[-1]
        try:
            # NOTE: This only works if the platform supports the Kodi configured locale
            locale.setlocale(locale.LC_ALL, locale_lang)
            return True
        except Exception as exc:  # pylint: disable=broad-except
            if locale_lang == 'en_gb':
                return True
            self.log("Your system does not support locale '{locale}': {error}", LOG_DEBUG, locale=locale_lang, error=exc)
            return False

    def localize(self, string_id, **kwargs):
        """ Return the translated string from the .po language files, optionally translating variables """
        if kwargs:
            import string
            return string.Formatter().vformat(self._addon.getLocalizedString(string_id), (), SafeDict(**kwargs))

        return self._addon.getLocalizedString(string_id)

    def get_setting(self, setting_id, default=None):
        """ Get an add-on setting """
        value = to_unicode(self._addon.getSetting(setting_id))
        if value == '' and default is not None:
            return default
        return value

    def get_setting_as_bool(self, setting):
        """ Get an add-on setting as a boolean value """
        return self.get_setting(setting).lower() == "true"

    def set_setting(self, setting_id, setting_value):
        """ Set an add-on setting """
        return self._addon.setSetting(setting_id, setting_value)

    def open_settings(self):
        """ Open the add-in settings window """
        self._addon.openSettings()

    @staticmethod
    def get_global_setting(setting):
        """ Get a Kodi setting """
        import json
        json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "%s"}, "id": 1}' % setting)
        return json.loads(json_result).get('result', dict()).get('value')

    def get_cache(self, key, ttl=None):
        """ Get an item from the cache
        :type key: list[str]
        :type ttl: int
        """
        import time

        fullpath = self._cache_path + '.'.join(key)

        if not self.check_if_path_exists(fullpath):
            return None

        if ttl and time.mktime(time.localtime()) - self.stat_file(fullpath).st_mtime() > ttl:
            return None

        with self.open_file(fullpath, 'r') as fdesc:
            try:
                import json
                value = json.load(fdesc)
                self.log('Fetching {file} from cache', file=fullpath)
                return value
            except (ValueError, TypeError):
                return None

    def set_cache(self, key, data):
        """ Store an item in the cache
        :type key: list[str]
        :type data: str
        """
        if not self.check_if_path_exists(self._cache_path):
            self.mkdirs(self._cache_path)

        fullpath = self._cache_path + '.'.join(key)
        with self.open_file(fullpath, 'w') as fdesc:
            import json
            self.log('Storing to cache as {file}', file=fullpath)
            json.dump(data, fdesc)

    def invalidate_cache(self, ttl=None):
        """ Clear the cache """
        if not self.check_if_path_exists(self._cache_path):
            return
        _, files = self.listdir(self._cache_path)
        import time
        now = time.mktime(time.localtime())
        for filename in files:
            fullpath = self._cache_path + filename
            if ttl and now - self.stat_file(fullpath).st_mtime() < ttl:
                continue
            self.delete_file(fullpath)

    def get_max_bandwidth(self):
        """ Get the max bandwidth based on Kodi and add-on settings """
        addon_max_bandwidth = int(self.get_setting('max_bandwidth', '0'))
        global_max_bandwidth = int(self.get_global_setting('network.bandwidth'))
        if addon_max_bandwidth != 0 and global_max_bandwidth != 0:
            return min(addon_max_bandwidth, global_max_bandwidth)
        if addon_max_bandwidth != 0:
            return addon_max_bandwidth
        if global_max_bandwidth != 0:
            return global_max_bandwidth
        return 0

    def get_proxies(self):
        """ Return a usable proxies dictionary from Kodi proxy settings """
        usehttpproxy = self.get_global_setting('network.usehttpproxy')
        if usehttpproxy is not True:
            return None

        try:
            httpproxytype = int(self.get_global_setting('network.httpproxytype'))
        except ValueError:
            httpproxytype = 0

        socks_supported = has_socks()
        if httpproxytype != 0 and not socks_supported:
            # Only open the dialog the first time (to avoid multiple popups)
            if socks_supported is None:
                self.show_ok_dialog('', self.localize(30966))  # Requires PySocks
            return None

        proxy_types = ['http', 'socks4', 'socks4a', 'socks5', 'socks5h']
        if 0 <= httpproxytype < 5:
            httpproxyscheme = proxy_types[httpproxytype]
        else:
            httpproxyscheme = 'http'

        httpproxyserver = self.get_global_setting('network.httpproxyserver')
        httpproxyport = self.get_global_setting('network.httpproxyport')
        httpproxyusername = self.get_global_setting('network.httpproxyusername')
        httpproxypassword = self.get_global_setting('network.httpproxypassword')

        if httpproxyserver and httpproxyport and httpproxyusername and httpproxypassword:
            proxy_address = '%s://%s:%s@%s:%s' % (httpproxyscheme, httpproxyusername, httpproxypassword, httpproxyserver, httpproxyport)
        elif httpproxyserver and httpproxyport and httpproxyusername:
            proxy_address = '%s://%s@%s:%s' % (httpproxyscheme, httpproxyusername, httpproxyserver, httpproxyport)
        elif httpproxyserver and httpproxyport:
            proxy_address = '%s://%s:%s' % (httpproxyscheme, httpproxyserver, httpproxyport)
        elif httpproxyserver:
            proxy_address = '%s://%s' % (httpproxyscheme, httpproxyserver)
        else:
            return None

        return dict(http=proxy_address, https=proxy_address)

    @staticmethod
    def get_cond_visibility(condition):
        """ Test a condition in XBMC """
        return xbmc.getCondVisibility(condition)

    def has_inputstream_adaptive(self):
        """ Whether InputStream Adaptive is installed and enabled in add-on settings """
        return self.get_setting('useinputstreamadaptive', 'true') == 'true' and xbmc.getCondVisibility('System.HasAddon(inputstream.adaptive)') == 1

    def credentials_filled_in(self):
        """ Whether the add-on has credentials filled in """
        return bool(self.get_setting('username') and self.get_setting('password'))

    @staticmethod
    def kodi_version():
        """ Returns major Kodi version """
        return int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])

    def can_play_drm(self):
        """ Whether this Kodi can do DRM using InputStream Adaptive """
        return self.get_setting('usedrm', 'true') == 'true' and self.get_setting('useinputstreamadaptive', 'true') == 'true' and self.supports_drm()

    def supports_drm(self):
        """ Whether this Kodi version supports DRM decryption using InputStream Adaptive """
        return self.kodi_version() > 17

    def get_userdata_path(self):
        """ Return the profile's userdata path """
        return to_unicode(xbmc.translatePath(self._addon.getAddonInfo('profile')))

    def get_addon_path(self):
        """ Return the profile's addon path """
        return to_unicode(xbmc.translatePath(self._addon.getAddonInfo('path')))

    def get_addon_info(self, key):
        """ Return addon information """
        return self._addon.getAddonInfo(key)

    @staticmethod
    def listdir(path):
        """ Return all files in a directory (using xbmcvfs)"""
        from xbmcvfs import listdir
        return listdir(path)

    def mkdir(self, path):
        """ Create a directory (using xbmcvfs) """
        from xbmcvfs import mkdir
        self.log("Create directory '{path}'.", LOG_DEBUG, path=path)
        return mkdir(path)

    def mkdirs(self, path):
        """ Create directory including parents (using xbmcvfs) """
        from xbmcvfs import mkdirs
        self.log("Recursively create directory '{path}'.", LOG_DEBUG, path=path)
        return mkdirs(path)

    @staticmethod
    def check_if_path_exists(path):
        """ Whether the path exists (using xbmcvfs)"""
        from xbmcvfs import exists
        return exists(path)

    @staticmethod
    @contextmanager
    def open_file(path, flags='r'):
        """ Open a file (using xbmcvfs) """
        from xbmcvfs import File
        fdesc = File(path, flags)
        yield fdesc
        fdesc.close()

    @staticmethod
    def stat_file(path):
        """ Return information about a file (using xbmcvfs) """
        from xbmcvfs import Stat
        return Stat(path)

    def delete_file(self, path):
        """ Remove a file (using xbmcvfs) """
        from xbmcvfs import delete
        self.log("Delete file '{path}'.", LOG_DEBUG, path=path)
        return delete(path)

    def container_refresh(self):
        """ Refresh the current container """
        self.log('Execute: Container.Refresh', LOG_DEBUG)
        xbmc.executebuiltin('Container.Refresh')

    def end_of_directory(self):
        """ Close a virtual directory, required to avoid a waiting Kodi """
        xbmcplugin.endOfDirectory(handle=self._handle, succeeded=False, updateListing=False, cacheToDisc=False)

    def log(self, message, log_level=LOG_INFO, **kwargs):
        """ Log info messages to Kodi """
        if not self._debug_logging and log_level in [LOG_DEBUG, LOG_INFO]:
            # Don't log debug and info messages when we haven't activated it.
            return
        if self._debug_logging and log_level in [LOG_DEBUG, LOG_INFO]:
            # Log debug and info messages as LOG_NOTICE if we've explicitly enabled it.
            log_level = LOG_NOTICE
        if kwargs:
            import string
            message = string.Formatter().vformat(message, (), SafeDict(**kwargs))
        message = '[{addon}] {message}'.format(addon=self._addon_id, message=message)
        xbmc.log(msg=from_unicode(message), level=log_level)

    def kids_mode(self):
        """ Returns if kids zone is active """
        if self.get_setting_as_bool('interface_force_kids_zone'):
            return True

        if self.routing and 'True' in self.routing.args.get('kids', []):
            return True

        return None
