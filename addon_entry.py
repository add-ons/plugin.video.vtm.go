# -*- coding: utf-8 -*-
""" Addon entry point """

from __future__ import absolute_import, division, unicode_literals

import sys

from xbmcaddon import Addon

from resources.lib.kodiutils import KodiUtils

# Reinitialise ADDON every invocation to fix an issue that settings are not fresh.
KodiUtils.ADDON = Addon()

# Store the handle since w need it when we want to execute Kodi functions.
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    KodiUtils.HANDLE = int(sys.argv[1])

if __name__ == '__main__':
    from resources.lib import addon  # pylint: disable=ungrouped-imports

    addon.run(sys.argv)
