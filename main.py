import xbmcaddon
import sys

from resources.lib import kodilogging
from resources.lib import plugin

ADDON = xbmcaddon.Addon()
kodilogging.config()

plugin.run(sys.argv)
