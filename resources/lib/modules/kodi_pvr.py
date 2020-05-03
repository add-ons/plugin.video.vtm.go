# -*- coding: utf-8 -*-
""" Kodi PVR Integration module """

from __future__ import absolute_import, division, unicode_literals

import json
import socket
from datetime import timedelta

from resources.lib.modules import CHANNELS
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoepg import VtmGoEpg


class KodiPvr:
    """ Code related to the Kodi PVR integration """

    def __init__(self, kodi):
        """ Initialise object
        :type kodi: resources.lib.kodiwrapper.KodiWrapper
        """
        self._kodi = kodi
        self._vtm_go = VtmGo(self._kodi)
        self._vtm_go_epg = VtmGoEpg(self._kodi)

    @staticmethod
    def reply(host, port):
        """ Send the output of the wrapped function to socket. """

        def decorator(func):
            """ Decorator """

            def inner(*arg, **kwargs):
                """ Execute function """
                # Open connection so the remote end knows we are doing something
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, port))

                try:
                    # Execute function
                    result = func(*arg, **kwargs)

                    # Send result
                    s.send(json.dumps(result))

                finally:
                    # Close our connection
                    s.close()

            return inner

        return decorator

    def get_channels(self):
        """ Report channel data """
        channels = []

        # Fetch channels from API
        channel_infos = self._vtm_go.get_live_channels()

        for i, key in enumerate(CHANNELS):  # pylint: disable=unused-variable
            channel = CHANNELS[key]

            logo = 'special://home/addons/{addon}/resources/logos/{logo}.png'.format(addon=self._kodi.get_addon_id(), logo=channel.get('logo'))

            # Find this channel in the list
            channel_info = next((c for c in channel_infos if c.key == key), None)

            if channel_info:
                channels.append(dict(
                    id=channel.get('epg'),
                    name=channel.get('label'),
                    logo=logo,
                    stream=self._kodi.url_for('play', category='channels', item=channel_info.channel_id),
                ))

        return dict(version=1, streams=channels)

    def get_epg(self):
        """ Report EPG data """
        epg = dict()

        # Fetch epg for today
        # TODO: yesterday, next days
        epg_infos = self._vtm_go_epg.get_epgs()

        for channel in epg_infos:
            key = channel.key
            if key not in epg.keys():
                epg[key] = []

            epg[key].extend([
                dict(
                    start=broadcast.time.isoformat(),
                    stop=(broadcast.time + timedelta(seconds=broadcast.duration)).isoformat(),
                    title=broadcast.title,
                    description=broadcast.description,
                    image=broadcast.image)
                for broadcast in channel.broadcasts
            ])

        return dict(version=1, epg=epg)
