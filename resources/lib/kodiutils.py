# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals
import json
import logging

import xbmc
from xbmcaddon import Addon
from xbmcgui import Dialog

# read settings
ADDON = Addon()
logger = logging.getLogger(__name__)


def notification(heading=ADDON.getAddonInfo('name'), message='', time=5000, icon=ADDON.getAddonInfo('icon'), sound=True):
    ''' Show a Kodi notification '''
    Dialog().notification(heading=heading, message=message, icon=icon, time=time, sound=sound)


def show_ok_dialog(heading=ADDON.getAddonInfo('name'), message=''):
    ''' Show Kodi's OK dialog '''
    Dialog().ok(heading=heading, line1=message)


def show_settings():
    ADDON.openSettings()


def get_setting(setting):
    return ADDON.getSetting(setting).strip().decode('utf-8')


def set_setting(setting, value):
    ADDON.setSetting(setting, str(value))


def get_setting_as_bool(setting):
    return get_setting(setting).lower() == "true"


def get_setting_as_float(setting):
    try:
        return float(get_setting(setting))
    except ValueError:
        return 0


def get_setting_as_int(setting):
    try:
        return int(get_setting_as_float(setting))
    except ValueError:
        return 0


def get_string(string_id):
    return ADDON.getLocalizedString(string_id).encode('utf-8', 'ignore')


def kodi_json_request(params):
    data = json.dumps(params)
    request = xbmc.executeJSONRPC(data)

    try:
        response = json.loads(request)
    except UnicodeDecodeError:
        response = json.loads(request.decode('utf-8', 'ignore'))

    return response.get('result')


def get_global_setting(setting):
    ''' Get a Kodi setting '''
    json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "%s"}, "id": 1}' % setting)
    # TODO: Implement proper kodi stubs for testing
    try:
        return json.loads(json_result).get('result', dict()).get('value')
    except ValueError:  # e.g. when xbmc.executeJSONRPC is a stub
        return None


def get_cond_visibility(condition):
    ''' Test a condition in XBMC '''
    return xbmc.getCondVisibility(condition)


def has_socks():
    ''' Test if socks is installed, and remember this information '''
    if not hasattr(has_socks, 'installed'):
        try:
            import socks  # noqa: F401; pylint: disable=unused-variable,unused-import
            has_socks.installed = True
        except ImportError:
            has_socks.installed = False
            return None  # Detect if this is the first run
    return has_socks.installed


def get_proxies():
    ''' Return a usable proxies dictionary from Kodi proxy settings '''
    usehttpproxy = get_global_setting('network.usehttpproxy')  # noqa; pylint: disable=unreachable
    if usehttpproxy is False:
        return None

    httpproxytype = get_global_setting('network.httpproxytype')

    socks_supported = has_socks()
    if httpproxytype != 0 and not socks_supported:
        # Only open the dialog the first time (to avoid multiple popups)
        if socks_supported is None:
            show_ok_dialog('', 'Using a SOCKS proxy requires the PySocks library (script.module.pysocks) installed.')
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
