# -*- coding: utf-8 -*-
""" Addon entry point """

from __future__ import absolute_import, division, unicode_literals
from resources.lib import kodiutils
from xbmcaddon import Addon

# Reinitialise ADDON every invocation to fix an issue that settings are not fresh.
kodiutils.ADDON = Addon()

if __name__ == '__main__':
    import sys
    from resources.lib import addon  # pylint: disable=ungrouped-imports

    addon.run(sys.argv)
