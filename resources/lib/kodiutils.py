# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals
import xbmc
from xbmcaddon import Addon
from xbmcgui import Dialog

ADDON = Addon()


class SafeDict(dict):
    ''' A safe dictionary implementation that does not break down on missing keys '''
    def __missing__(self, key):
        ''' Replace missing keys with the original placeholder '''
        return '{' + key + '}'


def to_unicode(text, encoding='utf-8'):
    ''' Force text to unicode '''
    return text.decode(encoding) if isinstance(text, bytes) else text


def from_unicode(text, encoding='utf-8'):
    ''' Force unicode to text '''
    import sys
    if sys.version_info.major == 2 and isinstance(text, unicode):  # noqa: F821; pylint: disable=undefined-variable
        return text.encode(encoding)
    return text


def has_socks():
    ''' Test if socks is installed, and remember this information '''
    if hasattr(has_socks, 'installed'):
        return has_socks.installed
    try:
        import socks  # noqa: F401; pylint: disable=unused-variable,unused-import
        has_socks.installed = True
        return True
    except ImportError:
        has_socks.installed = False
        return None  # Detect if this is the first run


def notification(heading=ADDON.getAddonInfo('name'), message='', time=5000, icon=ADDON.getAddonInfo('icon'), sound=True):
    ''' Show a Kodi notification '''
    Dialog().notification(heading=heading, message=message, icon=icon, time=time, sound=sound)


def show_ok_dialog(heading=ADDON.getAddonInfo('name'), message=''):
    ''' Show Kodi's OK dialog '''
    Dialog().ok(heading=heading, line1=message)


def show_settings():
    ADDON.openSettings()


def localize(string_id, **kwargs):
    ''' Return the translated string from the .po language files, optionally translating variables '''
    if kwargs:
        import string
        return string.Formatter().vformat(ADDON.getLocalizedString(string_id), (), SafeDict(**kwargs))
    return ADDON.getLocalizedString(string_id)


def get_setting(setting_id, default=None):
    ''' Get an add-on setting '''
    value = to_unicode(ADDON.getSetting(setting_id))
    if value == '' and default is not None:
        return default
    return value


def get_setting_as_bool(setting):
    return get_setting(setting).lower() == "true"


def set_setting(setting_id, setting_value):
    ''' Set an add-on setting '''
    return ADDON.setSetting(setting_id, setting_value)


def get_global_setting(setting):
    ''' Get a Kodi setting '''
    import json
    json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "%s"}, "id": 1}' % setting)
    return json.loads(json_result).get('result', dict()).get('value')


def get_max_bandwidth():
    ''' Get the max bandwidth based on Kodi and VTM GO add-on settings '''
    vtmgo_max_bandwidth = int(get_setting('max_bandwidth', '0'))
    global_max_bandwidth = int(get_global_setting('network.bandwidth'))
    if vtmgo_max_bandwidth != 0 and global_max_bandwidth != 0:
        return min(vtmgo_max_bandwidth, global_max_bandwidth)
    if vtmgo_max_bandwidth != 0:
        return vtmgo_max_bandwidth
    if global_max_bandwidth != 0:
        return global_max_bandwidth
    return 0


def get_proxies():
    ''' Return a usable proxies dictionary from Kodi proxy settings '''
    usehttpproxy = get_global_setting('network.usehttpproxy')  # noqa; pylint: disable=unreachable
    if usehttpproxy is False:
        return None

    try:
        httpproxytype = int(get_global_setting('network.httpproxytype'))
    except ValueError:
        httpproxytype = 0

    socks_supported = has_socks()
    if httpproxytype != 0 and not socks_supported:
        # Only open the dialog the first time (to avoid multiple popups)
        if socks_supported is None:
            show_ok_dialog('', localize(30200))  # Needs PySocks library
        return None

    proxy_types = ['http', 'socks4', 'socks4a', 'socks5', 'socks5h']
    if 0 <= httpproxytype < 5:
        httpproxyscheme = proxy_types[httpproxytype]
    else:
        httpproxyscheme = 'http'

    httpproxyserver = get_global_setting('network.httpproxyserver')
    httpproxyport = get_global_setting('network.httpproxyport')
    httpproxyusername = get_global_setting('network.httpproxyusername')
    httpproxypassword = get_global_setting('network.httpproxypassword')

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


proxies = get_proxies()


def get_cond_visibility(condition):
    ''' Test a condition in XBMC '''
    return xbmc.getCondVisibility(condition)
