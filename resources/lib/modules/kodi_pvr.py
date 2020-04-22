# -*- coding: utf-8 -*-
""" Kodi PVR Integration module """

from __future__ import absolute_import, division, unicode_literals

import json
import os
from datetime import timedelta
from functools import wraps

from resources.lib.modules import CHANNELS
from resources.lib.vtmgo.vtmgo import VtmGo
from resources.lib.vtmgo.vtmgoepg import VtmGoEpg


def file_output(routing):
    """ File output decorator """

    def decorator(func):

        @wraps(func)
        def wrapped(*args, **kwargs):
            # Get output from routing
            output = routing.args['output'][0]
            if not output:
                raise Exception('No output file supplied')

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Write output to file
                with open(output, 'w') as f:
                    json.dump(result, f)

            except Exception as exc:
                # Remove output file in case something goes wrong
                os.unlink(output)
                raise exc

        return wrapped

    return decorator


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
    def output_to_file(filename):
        """ Write the output of the wrapped function to a file. """

        def decorator(func):
            def inner(*arg, **kwargs):
                try:
                    # Execute function
                    result = func(*arg, **kwargs)

                    # Write output to file
                    with open(filename, 'w') as fdesc:
                        json.dump(result, fdesc)

                except:  # pylint: disable=broad-except
                    try:
                        # Remove output file
                        os.unlink(filename)
                    except:  # pylint: disable=broad-except
                        pass
                    raise

            return inner

        return decorator

    def get_channels(self):
        """ Report channel data """
        channels = []

        # Fetch channels from API
        channel_infos = self._vtm_go.get_live_channels()

        for i, key in enumerate(CHANNELS):  # pylint: disable=unused-variable
            channel = CHANNELS[key]

            logo = '{path}/resources/logos/{logo}.png'.format(path=self._kodi.get_addon_path(), logo=channel.get('logo'))

            # Find this channel in the list
            channel_info = next((c for c in channel_infos if c.key == key), None)

            if channel_info:
                channels.append(dict(
                    id=channel.get('epg'),
                    name=channel.get('label'),
                    logo=logo,
                    stream=self._kodi.url_for('play', category='channels', item=channel_info.channel_id),
                ))

        return channels

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

        return epg
