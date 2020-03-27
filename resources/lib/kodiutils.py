# -*- coding: utf-8 -*-
"""All functionality that requires Kodi imports"""

from __future__ import absolute_import, division, unicode_literals

import logging
from contextlib import contextmanager

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

SORT_METHODS = dict(
    unsorted=xbmcplugin.SORT_METHOD_UNSORTED,
    label=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS,
    title=xbmcplugin.SORT_METHOD_TITLE,
    episode=xbmcplugin.SORT_METHOD_EPISODE,
    duration=xbmcplugin.SORT_METHOD_DURATION,
    year=xbmcplugin.SORT_METHOD_VIDEO_YEAR,
    date=xbmcplugin.SORT_METHOD_DATE,
)
DEFAULT_SORT_METHODS = [
    'unsorted', 'label'
]

_LOGGER = logging.getLogger('kodiutils')


class SafeDict(dict):
    """A safe dictionary implementation that does not break down on missing keys"""

    def __missing__(self, key):
        """Replace missing keys with the original placeholder"""
        return '{' + key + '}'


class KodiUtils:
    """A helper class with wrappers for Kodi functions"""

    ADDON = xbmcaddon.Addon()
    HANDLE = -1  # The handle used for the Python invocation

    @classmethod
    def to_unicode(cls, text, encoding='utf-8', errors='strict'):
        """Force text to unicode"""
        if isinstance(text, bytes):
            return text.decode(encoding, errors=errors)
        return text

    @classmethod
    def from_unicode(cls, text, encoding='utf-8', errors='strict'):
        """Force unicode to text"""
        import sys
        if sys.version_info.major == 2 and isinstance(text, unicode):  # noqa: F821; pylint: disable=undefined-variable
            return text.encode(encoding, errors)
        return text

    @classmethod
    def addon_icon(cls):
        """Cache and return add-on icon"""
        return cls.get_addon_info('icon')

    @classmethod
    def addon_id(cls):
        """Cache and return add-on ID"""
        return cls.get_addon_info('id')

    @classmethod
    def addon_fanart(cls):
        """Cache and return add-on fanart"""
        return cls.get_addon_info('fanart')

    @classmethod
    def addon_name(cls):
        """Cache and return add-on name"""
        return cls.get_addon_info('name')

    @classmethod
    def addon_path(cls):
        """Cache and return add-on path"""
        return cls.get_addon_info('path')

    @classmethod
    def addon_profile(cls):
        """Cache and return add-on profile"""
        return cls.to_unicode(xbmc.translatePath(cls.ADDON.getAddonInfo('profile')))

    @classmethod
    def url_for(cls, name, *args, **kwargs):
        """Wrapper for routing.url_for() to lookup by name"""
        import resources.lib.addon as addon
        return addon.routing.url_for(getattr(addon, name), *args, **kwargs)

    @classmethod
    def show_listing(cls, title_items, category=None, sort=None, content=None, cache=True):
        """ Show a virtual directory in Kodi """

        if content:
            # content is one of: files, songs, artists, albums, movies, tvshows, episodes, musicvideos, videos, images, games
            xbmcplugin.setContent(cls.HANDLE, content=content)

        # Jump through hoops to get a stable breadcrumbs implementation
        category_label = ''
        if category:
            if not content:
                category_label = cls.addon_name() + ' / '
            if isinstance(category, int):
                category_label += cls.localize(category)
            else:
                category_label += category
        elif not content:
            category_label = cls.addon_name()

        xbmcplugin.setPluginCategory(handle=cls.HANDLE, category=category_label)

        # Add all sort methods to GUI (start with preferred)
        if sort is None:
            sort = DEFAULT_SORT_METHODS
        elif not isinstance(sort, list):
            sort = [sort] + DEFAULT_SORT_METHODS

        for key in sort:
            xbmcplugin.addSortMethod(handle=cls.HANDLE, sortMethod=SORT_METHODS[key])

        # Add the listings
        listing = []
        for title_item in title_items:
            # Three options:
            #  - item is a virtual directory/folder (not playable, path)
            #  - item is a playable file (playable, path)
            #  - item is non-actionable item (not playable, no path)
            is_folder = bool(not title_item.is_playable and title_item.path)
            is_playable = bool(title_item.is_playable and title_item.path)

            list_item = xbmcgui.ListItem(label=title_item.title, path=title_item.path)

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

            is_folder = bool(not title_item.is_playable and title_item.path)
            url = title_item.path if title_item.path else None
            listing.append((url, list_item, is_folder))

        succeeded = xbmcplugin.addDirectoryItems(cls.HANDLE, listing, len(listing))
        xbmcplugin.endOfDirectory(cls.HANDLE, succeeded, cacheToDisc=cache)

    @classmethod
    def play(cls, stream, title=None, art_dict=None, info_dict=None, prop_dict=None, stream_dict=None, license_key=None):
        """ Play the passed TitleItem.
        :type stream: string
        :type title: string
        :type art_dict: dict
        :type info_dict: dict
        :type prop_dict: dict
        :type stream_dict: dict
        :type license_key: string
        """

        play_item = xbmcgui.ListItem(label=title, path=stream)
        if art_dict:
            play_item.setArt(art_dict)
        if info_dict:
            play_item.setInfo(type='video', infoLabels=info_dict)
        if prop_dict:
            play_item.setProperties(prop_dict)
        if stream_dict:
            play_item.addStreamInfo('video', stream_dict)

        play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        play_item.setProperty('inputstream.adaptive.max_bandwidth', str(cls.get_max_bandwidth() * 1000))
        play_item.setProperty('network.bandwidth', str(cls.get_max_bandwidth() * 1000))
        play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        play_item.setMimeType('application/dash+xml')
        play_item.setContentLookup(False)

        if license_key is not None:
            play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            play_item.setProperty('inputstream.adaptive.license_key', license_key)

        # Note: Adding the subtitle directly on the ListItem could cause sync issues, therefore
        # we add the subtitles trough the Player after playback has started.
        # See https://github.com/add-ons/plugin.video.vtm.go/issues/148
        # This is probably a Kodi or inputstream.adaptive issue

        # if title_item.subtitles_path:
        #     play_item.setSubtitles(title_item.subtitles_path)

        # To support video playback directly from RunPlugin() we need to use xbmc.Player().play instead of
        # setResolvedUrl that only works with PlayMedia() or with internal playable menu items
        xbmcplugin.setResolvedUrl(cls.HANDLE, True, listitem=play_item)

    @classmethod
    def get_search_string(cls, heading='', message=''):
        """ Ask the user for a search string """
        search_string = None
        keyboard = xbmc.Keyboard(message, heading)
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_string = cls.to_unicode(keyboard.getText())
        return search_string

    @classmethod
    def context_menu(cls, items):
        """ Show Kodi's context menu dialog """
        return xbmcgui.Dialog().contextmenu(items)

    @classmethod
    def ok_dialog(cls, heading='', message=''):
        """Show Kodi's OK dialog"""
        if not heading:
            heading = cls.addon_name()
        return xbmcgui.Dialog().ok(heading=heading, line1=message)

    @classmethod
    def yesno_dialog(cls, heading='', message='', nolabel=None, yeslabel=None):
        """Show Kodi's OK dialog"""
        if not heading:
            heading = cls.addon_name()
        return xbmcgui.Dialog().yesno(heading=heading, line1=message, nolabel=nolabel, yeslabel=yeslabel)

    @classmethod
    def notification(cls, heading='', message='', icon='info', time=4000):
        """Show a Kodi notification"""
        if not heading:
            heading = cls.addon_name()
        if not icon:
            icon = cls.addon_icon()
        xbmcgui.Dialog().notification(heading=heading, message=message, icon=icon, time=time)

    @classmethod
    def multiselect(cls, heading='', options=None, autoclose=0, preselect=None, use_details=False):
        """Show a Kodi multi-select dialog"""
        if not heading:
            heading = cls.addon_name()
        return xbmcgui.Dialog().multiselect(heading=heading, options=options, autoclose=autoclose, preselect=preselect, useDetails=use_details)

    @classmethod
    def progress(cls, heading='', message=''):
        """ Show a Kodi progress dialog """
        if not heading:
            heading = cls.ADDON.getAddonInfo('name')
        dialog_progress = xbmcgui.DialogProgress()
        dialog_progress.create(heading=heading, line1=message)
        return dialog_progress

    @classmethod
    def set_locale(cls):
        """Load the proper locale for date strings, only once"""
        if hasattr(cls, '_set_locale_cached'):
            return getattr(cls, '_set_locale_cached')
        from locale import Error, LC_ALL, setlocale
        locale_lang = cls.get_global_setting('locale.language').split('.')[-1]
        locale_lang = locale_lang[:-2] + locale_lang[-2:].upper()
        # NOTE: setlocale() only works if the platform supports the Kodi configured locale
        try:
            setlocale(LC_ALL, locale_lang)
        except (Error, ValueError) as exc:
            if locale_lang != 'en_GB':
                _LOGGER.debug("Your system does not support locale '%s': %s", locale_lang, exc)
                cls._set_locale_cached = False
                return False
        cls._set_locale_cached = True
        return True

    @classmethod
    def localize(cls, string_id, **kwargs):
        """Return the translated string from the .po language files, optionally translating variables"""
        if kwargs:
            from string import Formatter
            return Formatter().vformat(cls.ADDON.getLocalizedString(string_id), (), SafeDict(**kwargs))
        return cls.ADDON.getLocalizedString(string_id)

    @classmethod
    def get_setting(cls, key, default=None):
        """Get an add-on setting as string"""
        try:
            value = cls.to_unicode(cls.ADDON.getSetting(key))
        except RuntimeError:  # Occurs when the add-on is disabled
            return default
        if value == '' and default is not None:
            return default
        return value

    @classmethod
    def get_setting_bool(cls, key, default=None):
        """Get an add-on setting as boolean"""
        try:
            return cls.ADDON.getSettingBool(key)
        except (AttributeError, TypeError):  # On Krypton or older, or when not a boolean
            value = cls.get_setting(key, default)
            if value not in ('false', 'true'):
                return default
            return bool(value == 'true')
        except RuntimeError:  # Occurs when the add-on is disabled
            return default

    @classmethod
    def get_setting_int(cls, key, default=None):
        """Get an add-on setting as integer"""
        try:
            return cls.ADDON.getSettingInt(key)
        except (AttributeError, TypeError):  # On Krypton or older, or when not an integer
            value = cls.get_setting(key, default)
            try:
                return int(value)
            except ValueError:
                return default
        except RuntimeError:  # Occurs when the add-on is disabled
            return default

    @classmethod
    def get_setting_float(cls, key, default=None):
        """Get an add-on setting"""
        try:
            return cls.ADDON.getSettingNumber(key)
        except (AttributeError, TypeError):  # On Krypton or older, or when not a float
            value = cls.get_setting(key, default)
            try:
                return float(value)
            except ValueError:
                return default
        except RuntimeError:  # Occurs when the add-on is disabled
            return default

    @classmethod
    def set_setting(cls, key, value):
        """Set an add-on setting"""
        return cls.ADDON.setSetting(key, cls.from_unicode(str(value)))

    @classmethod
    def set_setting_bool(cls, key, value):
        """Set an add-on setting as boolean"""
        try:
            return cls.ADDON.setSettingBool(key, value)
        except (AttributeError, TypeError):  # On Krypton or older, or when not a boolean
            if value in ['false', 'true']:
                return cls.set_setting(key, value)
            if value:
                return cls.set_setting(key, 'true')
            return cls.set_setting(key, 'false')

    @classmethod
    def set_setting_int(cls, key, value):
        """Set an add-on setting as integer"""
        try:
            return cls.ADDON.setSettingInt(key, value)
        except (AttributeError, TypeError):  # On Krypton or older, or when not an integer
            return cls.set_setting(key, value)

    @classmethod
    def set_setting_float(cls, key, value):
        """Set an add-on setting"""
        try:
            return cls.ADDON.setSettingNumber(key, value)
        except (AttributeError, TypeError):  # On Krypton or older, or when not a float
            return cls.set_setting(key, value)

    @classmethod
    def open_settings(cls):
        """Open the add-in settings window, shows Credentials"""
        cls.ADDON.openSettings()

    @classmethod
    def get_global_setting(cls, key):
        """Get a Kodi setting"""
        result = cls.jsonrpc(method='Settings.GetSettingValue', params=dict(setting=key))
        return result.get('result', {}).get('value')

    @classmethod
    def set_global_setting(cls, key, value):
        """Set a Kodi setting"""
        return cls.jsonrpc(method='Settings.SetSettingValue', params=dict(setting=key, value=value))

    @classmethod
    def get_cond_visibility(cls, condition):
        """Test a condition in XBMC"""
        return xbmc.getCondVisibility(condition)

    @classmethod
    def has_addon(cls, name):
        """Checks if add-on is installed"""
        return xbmc.getCondVisibility('System.HasAddon(%s)' % name) == 1

    @classmethod
    def kodi_version(cls):
        """Returns major Kodi version"""
        return int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])

    @classmethod
    def get_tokens_path(cls):
        """Cache and return the userdata tokens path"""
        if not hasattr(cls, 'get_tokens_path_cached'):
            cls.get_tokens_path_cached = cls.addon_profile() + 'tokens/'
        return getattr(cls, 'get_tokens_path_cached')

    @classmethod
    def get_cache_path(cls):
        """Cache and return the userdata cache path"""
        if not hasattr(cls, 'get_cache_path_cached'):
            cls.get_cache_path_cached = cls.addon_profile() + 'cache/'
        return getattr(cls, 'get_cache_path_cached')

    @classmethod
    def get_addon_info(cls, key):
        """Return addon information"""
        return cls.to_unicode(cls.ADDON.getAddonInfo(key))

    @classmethod
    def listdir(cls, path):
        """Return all files in a directory (using xbmcvfs)"""
        return xbmcvfs.listdir(path)

    @classmethod
    def mkdir(cls, path):
        """Create a directory (using xbmcvfs)"""
        _LOGGER.debug("Create directory '%s'.", path)
        return xbmcvfs.mkdir(path)

    @classmethod
    def mkdirs(cls, path):
        """Create directory including parents (using xbmcvfs)"""
        _LOGGER.debug("Recursively create directory '%s'.", path)
        return xbmcvfs.mkdirs(path)

    @classmethod
    def exists(cls, path):
        """Whether the path exists (using xbmcvfs)"""
        return xbmcvfs.exists(path)

    @classmethod
    @contextmanager
    def open_file(cls, path, flags='r'):
        """Open a file (using xbmcvfs)"""
        fdesc = xbmcvfs.File(path, flags)
        yield fdesc
        fdesc.close()

    @classmethod
    def stat_file(cls, path):
        """Return information about a file (using xbmcvfs)"""
        return xbmcvfs.Stat(path)

    @classmethod
    def delete(cls, path):
        """Remove a file (using xbmcvfs)"""
        _LOGGER.debug("Delete file '%s'.", path)
        return xbmcvfs.delete(path)

    @classmethod
    def container_refresh(cls, url=None):
        """Refresh the current container or (re)load a container by URL"""
        if url:
            _LOGGER.debug('Execute: Container.Refresh(%s)', url)
            xbmc.executebuiltin('Container.Refresh({url})'.format(url=url))
        else:
            _LOGGER.debug('Execute: Container.Refresh')
            xbmc.executebuiltin('Container.Refresh')

    @classmethod
    def container_update(cls, url):
        """Update the current container while respecting the path history."""
        if url:
            _LOGGER.debug('Execute: Container.Update(%s)', url)
            xbmc.executebuiltin('Container.Update({url})'.format(url=url))
        else:
            # URL is a mandatory argument for Container.Update, use Container.Refresh instead
            cls.container_refresh()

    @classmethod
    def end_of_directory(cls):
        """Close a virtual directory, required to avoid a waiting Kodi"""
        xbmcplugin.endOfDirectory(handle=cls.HANDLE, succeeded=False, updateListing=False, cacheToDisc=False)

    @classmethod
    def jsonrpc(cls, *args, **kwargs):
        """Perform JSONRPC calls"""
        from json import dumps, loads

        # We do not accept both args and kwargs
        if args and kwargs:
            _LOGGER.error('Wrong use of jsonrpc()')
            return None

        # Process a list of actions
        if args:
            for (idx, cmd) in enumerate(args):
                if cmd.get('id') is None:
                    cmd.update(id=idx)
                if cmd.get('jsonrpc') is None:
                    cmd.update(jsonrpc='2.0')
            return loads(xbmc.executeJSONRPC(dumps(args)))

        # Process a single action
        if kwargs.get('id') is None:
            kwargs.update(id=0)
        if kwargs.get('jsonrpc') is None:
            kwargs.update(jsonrpc='2.0')
        return loads(xbmc.executeJSONRPC(dumps(kwargs)))

    @classmethod
    def notify(cls, sender, message, data):
        """ Send a notification to Kodi using JSON RPC """
        result = cls.jsonrpc(method='JSONRPC.NotifyAll', params=dict(
            sender=sender,
            message=message,
            data=data,
        ))
        if result.get('result') != 'OK':
            _LOGGER.error('Failed to send notification: %s', result.get('error').get('message'))
            return False
        return True

    @classmethod
    def get_cache(cls, key, ttl=None):
        """ Get an item from the cache """
        import time
        path = cls.get_cache_path()
        filename = '.'.join(key)
        fullpath = path + filename

        if not cls.exists(fullpath):
            return None

        if ttl and time.mktime(time.localtime()) - cls.stat_file(fullpath).st_mtime() > ttl:
            return None

        with cls.open_file(fullpath, 'r') as fdesc:
            try:
                _LOGGER.debug('Fetching %s from cache', filename)
                import json
                value = json.load(fdesc)
                return value
            except (ValueError, TypeError):
                return None

    @classmethod
    def set_cache(cls, key, data):
        """ Store an item in the cache """
        path = cls.get_cache_path()
        filename = '.'.join(key)
        fullpath = path + filename

        if not cls.exists(path):
            cls.mkdirs(path)

        with cls.open_file(fullpath, 'w') as fdesc:
            _LOGGER.debug('Storing to cache as %s', filename)
            import json
            json.dump(data, fdesc)

    @classmethod
    def invalidate_cache(cls, ttl=None):
        """ Clear the cache """
        path = cls.get_cache_path()
        if not cls.exists(path):
            return
        _, files = cls.listdir(path)
        import time
        now = time.mktime(time.localtime())
        for filename in files:
            fullpath = path + filename
            if ttl and now - cls.stat_file(fullpath).st_mtime() < ttl:
                continue
            cls.delete(fullpath)

    @classmethod
    def get_max_bandwidth(cls):
        """ Get the max bandwidth based on Kodi and add-on settings """
        addon_max_bandwidth = int(cls.get_setting('max_bandwidth', '0'))
        global_max_bandwidth = int(cls.get_global_setting('network.bandwidth'))
        if addon_max_bandwidth != 0 and global_max_bandwidth != 0:
            return min(addon_max_bandwidth, global_max_bandwidth)
        if addon_max_bandwidth != 0:
            return addon_max_bandwidth
        if global_max_bandwidth != 0:
            return global_max_bandwidth
        return 0

    @classmethod
    def has_socks(cls):
        """Test if socks is installed, and use a static variable to remember"""
        if hasattr(cls, 'has_socks_cached'):
            return getattr(cls, 'has_socks_cached')
        try:
            import socks  # noqa: F401; pylint: disable=unused-variable,unused-import
        except ImportError:
            cls.has_socks_cached = False
            return None  # Detect if this is the first run
        cls.has_socks_cached = True
        return True

    @classmethod
    def get_proxies(cls):
        """Return a usable proxies dictionary from Kodi proxy settings"""
        usehttpproxy = cls.get_global_setting('network.usehttpproxy')
        if usehttpproxy is not True:
            return None

        try:
            httpproxytype = int(cls.get_global_setting('network.httpproxytype'))
        except ValueError:
            httpproxytype = 0

        socks_supported = cls.has_socks()
        if httpproxytype != 0 and not socks_supported:
            # Only open the dialog the first time (to avoid multiple popups)
            if socks_supported is None:
                cls.ok_dialog('', cls.localize(30966))  # Requires PySocks
            return None

        proxy_types = ['http', 'socks4', 'socks4a', 'socks5', 'socks5h']

        proxy = dict(
            scheme=proxy_types[httpproxytype] if 0 <= httpproxytype < 5 else 'http',
            server=cls.get_global_setting('network.httpproxyserver'),
            port=cls.get_global_setting('network.httpproxyport'),
            username=cls.get_global_setting('network.httpproxyusername'),
            password=cls.get_global_setting('network.httpproxypassword'),
        )

        if proxy.get('username') and proxy.get('password') and proxy.get('server') and proxy.get('port'):
            proxy_address = '{scheme}://{username}:{password}@{server}:{port}'.format(**proxy)
        elif proxy.get('username') and proxy.get('server') and proxy.get('port'):
            proxy_address = '{scheme}://{username}@{server}:{port}'.format(**proxy)
        elif proxy.get('server') and proxy.get('port'):
            proxy_address = '{scheme}://{server}:{port}'.format(**proxy)
        elif proxy.get('server'):
            proxy_address = '{scheme}://{server}'.format(**proxy)
        else:
            return None

        return dict(http=proxy_address, https=proxy_address)
