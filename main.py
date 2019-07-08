# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals
import sys
from xbmcaddon import Addon
from resources.lib import kodilogging, plugin

ADDON = Addon()
kodilogging.config()
plugin.run(sys.argv)
