# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

ADDON_INFO = {
    'id': 'plugin.video.vtm.go'
}


class Addon:
    ''' A reimplementation of the xbmcaddon Addon class '''

    @staticmethod
    def getAddonInfo(key):
        ''' A working implementation for the xbmcaddon Addon class getAddonInfo() method '''
        return ADDON_INFO.get(key)
