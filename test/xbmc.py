# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json

LOGFATAL = 'Fatal'
LOGERROR = 'Error'
LOGWARNING = 'Warning'
LOGNOTICE = 'Notice'
LOGINFO = 'Info'
LOGDEBUG = 'Debug'
LOGNONE = ''

GLOBAL_SETTINGS = {
    'network.bandwidth': 0,
}


def executeJSONRPC(jsonrpccommand):
    ''' A reimplementation of the xbmc executeJSONRPC() function '''
    command = json.loads(jsonrpccommand)
    if command.get('method') == 'Settings.GetSettingValue':
        key = command.get('params').get('setting')
        return '{"id":1,"jsonrpc":"2.0","result":{"value":"%s"}}' % GLOBAL_SETTINGS.get(key)
    return 'executeJSONRPC'


def log(msg, level):
    ''' A reimplementation of the xbmc log() function '''
    print('[32;1m%s: [32;0m%s[0m' % (level, msg))
