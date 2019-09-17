# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals
import logging

from xbmc import log, LOGDEBUG, LOGERROR, LOGFATAL, LOGINFO, LOGNOTICE, LOGWARNING
from xbmcaddon import Addon
from resources.lib.kodiutils import from_unicode, get_global_setting, get_setting, to_unicode

LOG_LEVELS = {
    'Debug': logging.DEBUG,
    'Verbose': logging.INFO,
    'Info': logging.WARNING,
    'Quiet': logging.CRITICAL
}

XBMC_LOG_LEVELS = {
    logging.NOTSET: LOGDEBUG,  # 0
    logging.DEBUG: LOGDEBUG,  # 0
    logging.INFO: LOGINFO,  # 1
    logging.WARNING: LOGWARNING,  # 3
    logging.ERROR: LOGERROR,  # 4
    logging.CRITICAL: LOGFATAL  # 6
}


class KodiLogHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)
        addon_id = to_unicode(Addon().getAddonInfo('id'))
        formatter = logging.Formatter('[%s]' % addon_id + '[%(name)s] %(message)s')
        self.setFormatter(formatter)
        self._debug_logging = get_global_setting('debug.showloginfo')  # Returns a boolean

    def emit(self, record):
        log_level = XBMC_LOG_LEVELS.get(record.levelno)
        if not self._debug_logging and log_level < LOGNOTICE:
            # If Debug Logging is disabled, Kodi filters everything below LOGNOTICE out.
            log_level = LOGNOTICE
        log(from_unicode(self.format(record)), log_level)

    def flush(self):
        pass


def get_logger(name=None):
    logger = logging.getLogger(name)
    logger.addHandler(KodiLogHandler())
    logger.setLevel(LOG_LEVELS.get(get_setting('max_log_level', 'Info'), logging.NOTSET))
    return logger
