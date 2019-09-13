# -*- coding: utf-8 -*-

# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, unicode_literals

YOUTUBE = [
    dict(
        label='VTM',
        studio='VTM',
        # VTM: https://www.youtube.com/user/VTMvideo
        path='plugin://plugin.video.youtube/user/VTMvideo/',
        kids=False,
    ),
    dict(
        label='VTM Nieuws',
        studio='VTM',
        # VTM Nieuws: https://www.youtube.com/channel/UCm1v16r82bhI5jwur14dK9w
        path='plugin://plugin.video.youtube/channel/UCm1v16r82bhI5jwur14dK9w/',
        kids=False,
    ),
    dict(
        label='VTM Koken',
        studio='VTM',
        # VTM Koken: https://www.youtube.com/user/VTMKOKENvideokanaal
        path='plugin://plugin.video.youtube/user/VTMKOKENvideokanaal/',
        kids=False,
    ),
    dict(
        label='VTM KIDS',
        studio='VTM KIDS',
        # VTM KIDS: https://www.youtube.com/channel/UCJgZKD2qpa7mY2BtIgpNR2Q
        path='plugin://plugin.video.youtube/channel/UCJgZKD2qpa7mY2BtIgpNR2Q/',
        kids=True,
    ),
    dict(
        label='Q2',
        studio='Q2',
        # Q2: https://www.youtube.com/user/2BEvideokanaal
        path='plugin://plugin.video.youtube/user/2BEvideokanaal/',
        kids=False,
    ),
    dict(
        label='Vitaya',
        studio='Vitaya',
        # Vitaya: https://www.youtube.com/user/VITAYAvideokanaal
        path='plugin://plugin.video.youtube/user/VITAYAvideokanaal/',
        kids=False,
    ),
    dict(
        label='QMusic',
        studio='QMusic',
        # Q-Music: https://www.youtube.com/user/qmusic
        path='plugin://plugin.video.youtube/user/qmusic/',
        kids=False,
    ),
]

CHANNELS = [
    dict(
        label='VTM',
        studio='VTM',
        key='vtm',
        kids=False,
    ),
    dict(
        label='Q2',
        studio='Q2',
        key='q2',
        kids=False,
    ),
    dict(
        label='Vitaya',
        studio='Vitaya',
        key='vitaya',
        kids=False,
    ),
    dict(
        label='CAZ',
        studio='CAZ',
        key='caz',
        kids=False,
    ),
    dict(
        label='VTM KIDS',
        studio='VTM KIDS',
        key='vtm-kids',
        kids=True,
    ),
    dict(
        label='VTM KIDS Jr',
        studio='VTM KIDS Jr',
        key='vtm-kids-jr',
        kids=True,
    ),
    dict(
        label='QMusic',
        studio='QMusic',
        key='qmusic',
        kids=False,
    ),
]
