# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals
import logging

from xbmc import log, LOGDEBUG, LOGERROR, LOGFATAL, LOGINFO, LOGNONE, LOGNOTICE, LOGWARNING
from xbmcaddon import Addon
from resources.lib.kodiutils import from_unicode, to_unicode, get_global_setting, get_setting

levels = {
    logging.CRITICAL: LOGFATAL,
    logging.ERROR: LOGERROR,
    logging.WARNING: LOGWARNING,
    logging.INFO: LOGINFO,
    logging.DEBUG: LOGDEBUG,
    logging.NOTSET: LOGNONE,
}

log_levels = dict(
    Quiet=0,
    Info=1,
    Verbose=2,
    Debug=3,
)

xbmc_log_levels = {
    logging.NOTSET: 0,  # Quiet
    logging.CRITICAL: 0,  # Quiet
    logging.ERROR: 0,  # Info
    logging.WARNING: 1,  # Info
    logging.INFO: 2,  # Verbose
    logging.DEBUG: 3,  # Debug
}


class KodiLogHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)
        addon_id = to_unicode(Addon().getAddonInfo('id'))
        prefix = '[%s] ' % addon_id
        formatter = logging.Formatter(prefix + '%(name)s: %(message)s')
        self.setFormatter(formatter)
        self._max_log_level = log_levels.get(get_setting('max_log_level', 'Debug'), 3)
        self._debug_logging = get_global_setting('debug.showloginfo')  # Returns a boolean

    def emit(self, record):
        log_level = levels.get(record.levelno)
        cur_log_level = xbmc_log_levels.get(record.levelno, 0)
        if not self._debug_logging and 1 < cur_log_level <= self._max_log_level:
            # If Debug Logging is not enabled, Kodi filters everything up to NOTICE out
            log_level = LOGNOTICE
        log(from_unicode(self.format(record)), log_level)

    def flush(self):
        pass


def config():
    logger = logging.getLogger()
    logger.addHandler(KodiLogHandler())
    logger.setLevel(logging.DEBUG)
