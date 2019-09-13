# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
from resources.lib import plugin

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')
xbmcplugin = __import__('xbmcplugin')
xbmcvfs = __import__('xbmcvfs')

addon = plugin.plugin


class TestRouter(unittest.TestCase):

    def test_main_menu(self):
        addon.run(['plugin://plugin.video.vtm.go/', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_index), 'plugin://plugin.video.vtm.go/')

    def test_kids_zone(self):
        plugin.run(['plugin://plugin.video.vtm.go/', '0', 'kids=True'])
        self.assertEqual(addon.url_for(plugin.show_index, kids=True), 'plugin://plugin.video.vtm.go/?kids=True')

    # Check credentials: '/check-credentials'
#    def test_check_credentials(self):
#        plugin.run(['plugin://plugin.video.vtm.go/check-credentials', '0', ''])
#        self.assertEqual(addon.url_for(plugin.check_credentials), 'plugin://plugin.video.vtm.go/check-credentials')

    # Live TV menu: '/livetv'
    def test_livetv_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/livetv', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_livetv), 'plugin://plugin.video.vtm.go/livetv')

    # Episodes menu: '/program/<program>'
    def test_program_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_program, program='e892cf10-5100-42ce-8d59-6b5c03cc2b96'), 'plugin://plugin.video.vtm.go/program/e892cf10-5100-42ce-8d59-6b5c03cc2b96')

    # Catalogue menu: '/catalog'
    def test_catalog_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/catalog', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_catalog), 'plugin://plugin.video.vtm.go/catalog')

    # Categories programs menu: '/catalog/<category>'
    def test_catalog_category_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/catalog/films', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_catalog, category='films'), 'plugin://plugin.video.vtm.go/catalog/films')
        plugin.run(['plugin://plugin.video.vtm.go/catalog/kids', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_catalog, category='kids'), 'plugin://plugin.video.vtm.go/catalog/kids')

    # Movie menu: '/movie/<movie>'
    def test_movies(self):
        plugin.run(['plugin://plugin.video.vtm.go/movie/d1850498-941d-48cc-a558-37aaf37f4525', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_movie, movie='d1850498-941d-48cc-a558-37aaf37f4525'), 'plugin://plugin.video.vtm.go/movie/d1850498-941d-48cc-a558-37aaf37f4525')

    # YouTube menu: '/youtube'
    def test_youtube_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/youtube', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_youtube), 'plugin://plugin.video.vtm.go/youtube')

    # Search menu: '/search'
    def test_search_menu(self):
        plugin.run(['plugin://plugin.video.vtm.go/search', '0', ''])
        self.assertEqual(addon.url_for(plugin.show_search), 'plugin://plugin.video.vtm.go/search')


if __name__ == '__main__':
    unittest.main()
