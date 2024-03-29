# -*- coding: utf-8 -*-
""" Tests """

# pylint: disable=missing-docstring,no-self-use,wrong-import-order,wrong-import-position

from __future__ import absolute_import, division, unicode_literals

import os
import sys

from resources.lib import kodilogging, kodiutils
from resources.lib.vtmgo.vtmgoauth import VtmGoAuth

try:  # Python 3
    from http.client import HTTPConnection
except ImportError:  # Python 2
    from httplib import HTTPConnection

kodilogging.config()

# Add logging to urllib
HTTPConnection.debuglevel = 1

# Make UTF-8 the default encoding in Python 2
if sys.version_info[0] == 2:
    reload(sys)  # pylint: disable=undefined-variable  # noqa: F821
    sys.setdefaultencoding("utf-8")  # pylint: disable=no-member

# Set credentials based on environment data
# Use the .env file with Pipenv to make this work nicely during development
if os.environ.get('ADDON_TOKEN'):
    AUTH = VtmGoAuth(kodiutils.get_tokens_path())
    AUTH.set_token(os.environ.get('ADDON_TOKEN'))
