# -*- coding: utf-8 -*-
""" VTM GO Authentication API """

from __future__ import absolute_import, division, unicode_literals

import uuid
import json
import logging
import os

from requests import HTTPError

from resources.lib.vtmgo import API_ENDPOINT, Profile, util
from resources.lib.vtmgo.exceptions import NoLoginException

try:  # Python 3
    import jwt
except ImportError:  # Python 2
    # The package is named pyjwt in Kodi 18: https://github.com/lottaboost/script.module.pyjwt/pull/1
    import pyjwt as jwt

try:  # Python 3
    from urllib.parse import parse_qs, urlparse
except ImportError:  # Python 2
    from urlparse import parse_qs, urlparse

_LOGGER = logging.getLogger(__name__)


class AccountStorage:
    """ Data storage for account info """
    device_code = ''
    id_token = ''
    access_token = ''
    refresh_token = ''
    profile = ''
    product = ''

    # Credentials hash
    hash = ''

    def is_valid_token(self):
        """ Validate the JWT to see if it's still valid.

        :rtype: boolean
        """
        if not self.access_token:
            # We have no token
            return False

        try:
            # Verify our token to see if it's still valid.
            decoded_jwt = jwt.decode(self.access_token,
                                     algorithms=['HS256'],
                                     options={'verify_signature': False, 'verify_aud': False})

            # # Check issued at datetime
            # # VTM GO updated the JWT token format on 2021-05-03T12:00:00+00:00, older JWT tokens became invalid
            # update = dateutil.parser.parse('2021-05-03T12:00:00+00:00')
            # iat = datetime.fromtimestamp(decoded_jwt.get('iat'), tz=dateutil.tz.gettz('Europe/Brussels'))
            # if iat < update:
            #     _LOGGER.debug('JWT issued at %s is too old', iat.isoformat())
            #     return False

            # Check expiration time
            import dateutil.parser
            import dateutil.tz
            from datetime import datetime
            exp = datetime.fromtimestamp(decoded_jwt.get('exp'), tz=dateutil.tz.gettz('Europe/Brussels'))
            now = datetime.now(dateutil.tz.UTC)
            if exp < now:
                _LOGGER.debug('JWT is expired at %s', exp.isoformat())
                return False

        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.debug('JWT is NOT valid: %s', exc)
            return False

        _LOGGER.debug('JWT is valid')
        return True


class VtmGoAuth:
    """ VTM GO Authentication API """

    TOKEN_FILE = 'auth-tokens2.json'

    def __init__(self, token_path):
        """ Initialise object """
        self._token_path = token_path

        # Load existing account data
        self._account = AccountStorage()
        self._load_cache()

    def authorize(self):
        """ Start the authorization flow. """
        response = util.http_post('https://login2.vtm.be/device/authorize', form={
            'client_id': 'vtm-go-androidtv',
        })
        auth_info = json.loads(response.text)

        # We only need the device_code
        self._account.device_code = auth_info.get('device_code')
        self._save_cache()

        return auth_info

    def authorize_check(self):
        """ Check if the authorization has been completed. """
        if not self._account.device_code:
            raise NoLoginException

        try:
            response = util.http_post('https://login2.vtm.be/token', form={
                'device_code': self._account.device_code,
                'client_id': 'vtm-go-androidtv',
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            })
        except HTTPError as exc:
            if exc.response.status_code == 400:
                return False
            raise

        # Store these tokens
        auth_info = json.loads(response.text)
        self._account.id_token = auth_info.get('access_token')
        self._account.refresh_token = auth_info.get('refresh_token')
        self._save_cache()

        return True

    def get_tokens(self):
        """ Check if we have a token based on our device code. """
        if not self._account.id_token:
            raise NoLoginException

        # Return our current token if it is still valid.
        if self._account.is_valid_token():
            return self._account

        # Fetch an actual token we can use
        response = util.http_post('https://lfvp-api.dpgmedia.net/vtmgo/tokens', data={
            'device': {
                'id': str(uuid.uuid4()),  # TODO: should we reuse this id?
                'name': ''  # Show we announce ourselves as Kodi?
            },
            'idToken': self._account.id_token,
        })

        auth_info = json.loads(response.text)
        self._account.access_token = auth_info.get('lfvpToken')

        # We always use the main profile
        profiles = self.get_profiles()
        self._account.profile = profiles[0].key
        self._account.product = profiles[0].product

        self._save_cache()

        return self._account

    def get_profiles(self, products='VTM_GO,VTM_GO_KIDS'):
        """ Returns the available profiles """
        response = util.http_get(API_ENDPOINT + '/profiles', {'products': products}, token=self._account.access_token)
        result = json.loads(response.text)

        profiles = [
            Profile(
                key=profile.get('id'),
                product=profile.get('product'),
                name=profile.get('name'),
                gender=profile.get('gender'),
                birthdate=profile.get('birthDate'),
                color=profile.get('color', {}).get('start'),
                color2=profile.get('color', {}).get('end'),
            )
            for profile in result
        ]

        return profiles

    def logout(self):
        """ Clear the session tokens. """
        self._account.access_token = None
        self._save_cache()

    # def _android_refesh(self):
    #
    #     # We can refresh our old token so it's valid again
    #     response = util.http_post('https://lfvp-api.dpgmedia.net/vtmgo/tokens/refresh', data={
    #         'lfvpToken': self._account.access_token,
    #     })
    #
    #     # Get JWT from reply
    #     self._account.access_token = json.loads(response.text).get('lfvpToken')
    #     self._save_cache()
    #
    #     return self._account

    def _load_cache(self):
        """ Load tokens from cache """
        try:
            with open(os.path.join(self._token_path, self.TOKEN_FILE), 'r') as fdesc:
                self._account.__dict__ = json.loads(fdesc.read())  # pylint: disable=attribute-defined-outside-init
        except (IOError, TypeError, ValueError):
            _LOGGER.warning('We could not use the cache since it is invalid or non-existent.')

    def _save_cache(self):
        """ Store tokens in cache """
        if not os.path.exists(self._token_path):
            os.makedirs(self._token_path)

        with open(os.path.join(self._token_path, self.TOKEN_FILE), 'w') as fdesc:
            json.dump(self._account.__dict__, fdesc, indent=2)
