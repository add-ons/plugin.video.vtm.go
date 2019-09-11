# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from xbmcextra import global_settings, import_language, read_addon_xml

GLOBAL_SETTINGS = global_settings()
ADDON_INFO = read_addon_xml('addon.xml')
ADDON_ID = list(ADDON_INFO)[0]
PO = import_language(language=GLOBAL_SETTINGS.get('locale.language'))


class Addon:
    ''' A reimplementation of the xbmcaddon Addon class '''

    def __init__(self, id=ADDON_ID):  # pylint: disable=redefined-builtin
        ''' A stub constructor for the xbmcaddon Addon class '''
        self.id = id

    def getAddonInfo(self, key):
        ''' A working implementation for the xbmcaddon Addon class getAddonInfo() method '''
        STUB_INFO = dict(id=self.id, name=self.id, version='2.3.4', type='kodi.inputstream', profile='special://userdata')
        return ADDON_INFO.get(self.id, STUB_INFO).get(key)

    @staticmethod
    def getLocalizedString(msgctxt):
        ''' A working implementation for the xbmcaddon Addon class getLocalizedString() method '''
        for entry in PO:
            if entry.msgctxt == '#%s' % msgctxt:
                return entry.msgstr or entry.msgid
        return 'vrttest'
