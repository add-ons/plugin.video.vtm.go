# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from xbmc import Monitor

from resources.lib.kodiwrapper import KodiWrapper, LOG_INFO
from resources.lib.vtmgo.vtmgo import VtmGo


class BackgroundService(Monitor):

    def __init__(self):
        Monitor.__init__(self)
        self.kodi = KodiWrapper()
        self.vtm_go = VtmGo(self.kodi)

    def run(self):
        """ Background loop for maintenance tasks """
        self.kodi.log('Service started', LOG_INFO)

        while not self.waitForAbort(60):
            # TODO: cleanup old cache
            # TODO: update every 24 hours
            if self.kodi.get_setting_as_bool('update_metadata'):
                self.update_metadata()

        self.kodi.log('Service stopped', LOG_INFO)

    def onSettingsChanged(self):
        """ Callback when a setting has changed """
        self.kodi.log('IN VTM GO: Settings changed')

        # Refresh our VtmGo instance
        self.vtm_go = VtmGo(self.kodi)

    def update_metadata(self):
        pass


def run():
    BackgroundService().run()
