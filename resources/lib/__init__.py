# -*- coding: utf-8 -*-
""" Static data for this addon """

from __future__ import absolute_import, division, unicode_literals

YOUTUBE = [
    dict(
        label='VTM',
        logo='vtm',
        # VTM: https://www.youtube.com/user/VTMvideo
        path='plugin://plugin.video.youtube/user/VTMvideo/',
        kids=False,
    ),
    dict(
        label='VTM Nieuws',
        logo='vtm',
        # VTM Nieuws: https://www.youtube.com/channel/UCm1v16r82bhI5jwur14dK9w
        path='plugin://plugin.video.youtube/channel/UCm1v16r82bhI5jwur14dK9w/',
        kids=False,
    ),
    dict(
        label='VTM Koken',
        logo='vtm',
        # VTM Koken: https://www.youtube.com/user/VTMKOKENvideokanaal
        path='plugin://plugin.video.youtube/user/VTMKOKENvideokanaal/',
        kids=False,
    ),
    dict(
        label='VTM KIDS',
        logo='vtmkids',
        # VTM KIDS: https://www.youtube.com/channel/UCJgZKD2qpa7mY2BtIgpNR2Q
        path='plugin://plugin.video.youtube/channel/UCJgZKD2qpa7mY2BtIgpNR2Q/',
        kids=True,
    ),
    dict(
        label='Q2',
        logo='q2',
        # Q2: https://www.youtube.com/user/2BEvideokanaal
        path='plugin://plugin.video.youtube/user/2BEvideokanaal/',
        kids=False,
    ),
    dict(
        label='Vitaya',
        logo='vitaya',
        # Vitaya: https://www.youtube.com/user/VITAYAvideokanaal
        path='plugin://plugin.video.youtube/user/VITAYAvideokanaal/',
        kids=False,
    ),
    dict(
        label='QMusic',
        logo='qmusic',
        # Q-Music: https://www.youtube.com/user/qmusic
        path='plugin://plugin.video.youtube/user/qmusic/',
        kids=False,
    ),
]

CHANNEL_MAPPING = {
    'VTM': 'vtm',
    'CAZ': 'caz',
    'Q2': 'q2',
    'QMusic': 'qmusic',
    'Vitaya': 'vitaya',
    'VTM Kids': 'vtmkids',
    'VTM Kids Jr': 'vtmkidsjr',
}

CHANNELS = [
    dict(
        label='VTM',
        logo='vtm',
        key='vtm',
        kids=False,
    ),
    dict(
        label='Q2',
        logo='q2',
        key='q2',
        kids=False,
    ),
    dict(
        label='Vitaya',
        logo='vitaya',
        key='vitaya',
        kids=False,
    ),
    dict(
        label='CAZ',
        logo='caz',
        key='caz',
        kids=False,
    ),
    dict(
        label='VTM KIDS',
        logo='vtmkids',
        key='vtm-kids',
        kids=True,
    ),
    dict(
        label='VTM KIDS Jr',
        logo='vtmkidsjr',
        key='vtm-kids-jr',
        kids=True,
    ),
    dict(
        label='QMusic',
        logo='qmusic',
        key='qmusic',
        kids=False,
    ),
]


class GeoblockedException(Exception):
    """ Is thrown when a geoblocked item is played. """


class UnavailableException(Exception):
    """ Is thrown when an unavailable item is played. """
