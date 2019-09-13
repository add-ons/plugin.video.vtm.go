# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
''' This file implements the Kodi xbmcgui module, either using stubs or alternative functionality '''

# pylint: disable=unused-argument,too-many-arguments

from __future__ import absolute_import, division, print_function, unicode_literals
from xbmcextra import kodi_to_ansi


class Dialog:
    ''' A reimplementation of the xbmcgui Dialog class '''

    def __init__(self):
        ''' A stub constructor for the xbmcgui Dialog class '''

    @staticmethod
    def notification(heading, message, icon=None, time=None, sound=None):
        ''' A working implementation for the xbmcgui Dialog class notification() method '''
        heading = kodi_to_ansi(heading)
        message = kodi_to_ansi(message)
        print('\033[37;100mNOTIFICATION:\033[35;0m [%s] \033[35;0m%s\033[39;0m' % (heading, message))

    @staticmethod
    def ok(heading, line1, line2=None, line3=None):
        ''' A stub implementation for the xbmcgui Dialog class ok() method '''
        heading = kodi_to_ansi(heading)
        line1 = kodi_to_ansi(line1)
        print('\033[37;100mOK:\033[35;0m [%s] \033[35;0m%s\033[39;0m' % (heading, line1))

    @staticmethod
    def info(listitem):
        ''' A stub implementation for the xbmcgui Dialog class info() method '''


class ListItem:
    ''' A reimplementation of the xbmcgui ListItem class '''

    def __init__(self, label='', label2='', iconImage='', thumbnailImage='', path='', offscreen=False):
        ''' A stub constructor for the xbmcgui ListItem class '''
        self.label = kodi_to_ansi(label)
        self.label2 = kodi_to_ansi(label2)
        self.path = path

    @staticmethod
    def addContextMenuItems(items, replaceItems=False):
        ''' A stub implementation for the xbmcgui ListItem class addContextMenuItems() method '''
        return

    @staticmethod
    def addStreamInfo(stream_type, stream_values):
        ''' A stub implementation for the xbmcgui LitItem class addStreamInfo() method '''
        return

    @staticmethod
    def setArt(key):
        ''' A stub implementation for the xbmcgui ListItem class setArt() method '''
        return

    @staticmethod
    def setContentLookup(enable):
        ''' A stub implementation for the xbmcgui ListItem class setContentLookup() method '''
        return

    @staticmethod
    def setInfo(type, infoLabels):  # pylint: disable=redefined-builtin
        ''' A stub implementation for the xbmcgui ListItem class setInfo() method '''
        return

    @staticmethod
    def setMimeType(mimetype):
        ''' A stub implementation for the xbmcgui ListItem class setMimeType() method '''
        return

    def setPath(self, path):
        ''' A stub implementation for the xbmcgui ListItem class setPath() method '''
        self.path = path

    @staticmethod
    def setProperty(key, value):
        ''' A stub implementation for the xbmcgui ListItem class setProperty() method '''
        return

    @staticmethod
    def setSubtitles(subtitleFiles):
        ''' A stub implementation for the xbmcgui ListItem class setSubtitles() method '''
        return
