# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
from xbmcextra import global_settings, import_language

LOGFATAL = 'Fatal'
LOGERROR = 'Error'
LOGWARNING = 'Warning'
LOGNOTICE = 'Notice'
LOGINFO = 'Info'
LOGDEBUG = 'Debug'
LOGNONE = ''

GLOBAL_SETTINGS = global_settings()
PO = import_language(language=GLOBAL_SETTINGS.get('locale.language'))


class Keyboard:
    ''' A stub implementation of the xbmc Keyboard class '''

    def __init__(self, line='', heading=''):
        ''' A stub constructor for the xbmc Keyboard class '''

    def doModal(self, autoclose=0):
        ''' A stub implementation for the xbmc Keyboard class doModal() method '''

    def isConfirmed(self):
        ''' A stub implementation for the xbmc Keyboard class isConfirmed() method '''
        return True

    def getText(self):
        ''' A stub implementation for the xbmc Keyboard class getText() method '''
        return 'unittest'


def executeJSONRPC(jsonrpccommand):
    ''' A reimplementation of the xbmc executeJSONRPC() function '''
    command = json.loads(jsonrpccommand)
    if command.get('method') == 'Settings.GetSettingValue':
        key = command.get('params').get('setting')
        return '{"id":1,"jsonrpc":"2.0","result":{"value":"%s"}}' % GLOBAL_SETTINGS.get(key)
    return 'executeJSONRPC'


def getCondVisibility(string):  # pylint: disable=unused-argument
    ''' A reimplementation of the xbmc getCondVisibility() function '''
    if string == 'system.platform.android':
        return False
    return True


def log(msg, level):
    ''' A reimplementation of the xbmc log() function '''
    print('[32;1m%s: [32;0m%s[0;39m' % (level, msg))
