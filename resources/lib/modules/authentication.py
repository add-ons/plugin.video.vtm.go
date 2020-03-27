# -*- coding: utf-8 -*-
""" Profile module """

from __future__ import absolute_import, division, unicode_literals

import logging

from resources.lib.kodiutils import KodiUtils
from resources.lib.modules.menu import TitleItem
from resources.lib.vtmgo.vtmgo import VtmGo, ApiUpdateRequired
from resources.lib.vtmgo.vtmgoauth import InvalidLoginException, LoginErrorException

_LOGGER = logging.getLogger('authentication')


class Authentication:
    """ Code responsible for the Authentication """

    def __init__(self):
        """ Initialise object """
        self._vtm_go = VtmGo()

    def select_profile(self, key=None):
        """ Show your profiles
        :type key: str
        """
        try:
            profiles = self._vtm_go.get_profiles()
        except InvalidLoginException:
            KodiUtils.ok_dialog(message=KodiUtils.localize(30203))  # Your credentials are not valid!
            KodiUtils.open_settings()
            return

        except LoginErrorException as exc:
            KodiUtils.ok_dialog(message=KodiUtils.localize(30702, code=exc.code))  # Unknown error while logging in: {code}
            KodiUtils.open_settings()
            return

        except ApiUpdateRequired:
            KodiUtils.ok_dialog(message=KodiUtils.localize(30705))  # The VTM GO Service has been updated...
            return

        except Exception as exc:  # pylint: disable=broad-except
            KodiUtils.ok_dialog(message="%s" % exc)
            return

        # Show warning when you have no profiles
        if not profiles:
            # Your account has no profiles defined. Please login on vtm.be/vtmgo and create a Profile.
            KodiUtils.ok_dialog(message=KodiUtils.localize(30703))
            KodiUtils.end_of_directory()
            return

        # Select the first profile when you only have one
        if len(profiles) == 1:
            key = profiles[0].key

        # Save the selected profile
        if key:
            profile = [x for x in profiles if x.key == key][0]
            _LOGGER.info('Setting profile to %s', profile)
            KodiUtils.set_setting('profile', '%s:%s' % (profile.key, profile.product))
            KodiUtils.set_setting('profile_name', profile.name)

            KodiUtils.container_update(KodiUtils.url_for('show_main_menu'))
            return

        # Show profile selection when you have multiple profiles
        listing = [
            TitleItem(
                title=self._get_profile_name(p),
                path=KodiUtils.url_for('select_profile', key=p.key),
                art_dict=dict(
                    icon='DefaultUser.png'
                ),
                info_dict=dict(
                    plot=p.name,
                ),
            )
            for p in profiles
        ]

        KodiUtils.show_listing(listing, sort=['unsorted'], category=30057)  # Select Profile

    @staticmethod
    def _get_profile_name(profile):
        """ Get a descriptive string of the profile
        :type profile: resources.lib.vtmgo.vtmgo.Profile
        """
        title = profile.name

        # Convert the VTM GO Profile color to a matching Kodi color
        color_map = {
            '#64D8E3': 'skyblue',
            '#4DFF76': 'mediumspringgreen',
            '#0243FF': 'blue',
            '#831CFA': 'blueviolet',
            '#FFB24D': 'khaki',
            '#FF4DD5': 'violet',
            '#FFB002': 'gold',
            '#FF0257': 'crimson',
        }
        if color_map.get(profile.color.upper()):
            title = '[COLOR %s]%s[/COLOR]' % (color_map.get(profile.color), KodiUtils.to_unicode(title))

        # Append (Kids)
        if profile.product == 'VTM_GO_KIDS':
            title = "%s (Kids)" % title

        return title
