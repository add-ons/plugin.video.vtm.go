# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import hashlib
import json
import random

import requests

from resources.lib import kodiutils, kodilogging
from resources.lib.kodiutils import localize, proxies

logger = kodilogging.get_logger('VtmGoAuth')


class InvalidLoginException(Exception):
    pass


class VtmGoAuth:
    username = ''
    password = ''
    hash = None

    def __init__(self):
        self._token = None
        self._name = None
        self._accountId = None

        # Calculate new hash
        calc = hashlib.md5((self.username + self.password).encode('utf-8')).hexdigest()

        # Clear tokens when hash is different
        if self.hash and self.hash != calc:
            self.clear_token()
            self.hash = None

        # Store new hash
        if not self.hash:
            kodiutils.set_setting('credentials_hash', calc)

    def clear_token(self):
        """ Remove the cached JWT. """
        logger.debug('Clearing token cache')
        self._token = None
        path = kodiutils.get_profile_path() + 'token.json'
        if kodiutils.path_exists(path):
            kodiutils.delete_file(path)

    def get_token(self):
        """ Return a JWT that can be used to authenticate the user.
        :rtype str
        """

        # Don't return a token when we have no password or username.
        if not self.username or not self.password:
            logger.info('Skipping since we have no username or password')
            return None

        # Return if we already have the token in memory.
        if self._token:
            logger.debug('Returning token from memory')
            return self._token

        # Try to load from cache
        path = kodiutils.get_profile_path() + 'token.json'
        if kodiutils.path_exists(path):
            logger.debug('Returning token from cache')
            f = kodiutils.open_file(path, 'r')
            self._token = f.read()
            f.close()

            if self._token:
                return self._token

        # Authenticate with VTM GO and store the token
        self._token = self._login()
        logger.debug('Returning token from vtm go')

        f = kodiutils.open_file(path, 'w')
        f.write(self._token)
        f.close()

        return self._token

    def _login(self):
        """ Executes a login and returns the JSON Web Token.
        :rtype str
        """
        # Create new session object. This keeps the cookies across requests.
        session = requests.sessions.session()

        # Get login form. This sets some cookies we need.
        session.get('https://login.persgroep.net/authorize', params={
            'redirect_uri': 'vtmgo://callback/oidc',
            'client_id': 'vtm-go-android',
            'response_type': 'code',
            'state': self._generate_random_id(22),
            'nonce': self._generate_random_id(22),
            'scope': 'openid profile'
        }, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36'
        }, proxies=proxies)

        # Now, send the login details. We will be redirected to vtmgo:// when we succeed. We then can extract an authorizationCode that we need to continue.
        try:
            response = session.post('https://login2.vtm.be/login/emailfirst/password?client_id=vtm-go-android', data={
                'userName': self.username,
                'password': self.password,
                'jsEnabled': 'true',
            })

            if 'Wachtwoord is niet correct' in response.text:
                raise InvalidLoginException()

            raise Exception(localize(30702))  # Unknown error while logging in

        except requests.exceptions.InvalidSchema as e:
            # We get back an url like this: vtmgo://callback/oidc?state=yyyyyyyyyyyyyyyyyyyyyy&code=xxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx
            # I found no other way to get this url then by parsing the Exception message. :(
            import re
            matches = re.search(r"code=([^']+)", str(e))
            if matches:
                code = matches.group(1)
            else:
                raise Exception(localize(30703))  # Could not extract authentication code

        # Okay, final stage. We now need to use our authorizationCode to get a valid JWT.
        response = session.post('https://api.vtmgo.be/authorize', json={
            'authorizationCode': code,
            'authorizationCodeCallbackUrl': 'vtmgo://callback/oidc',
            'clientId': 'vtm-go-android',
        }, headers={
            'x-app-version': '5',
            'x-persgroep-mobile-app': 'true',
            'x-persgroep-os': 'android',
            'x-persgroep-os-version': '23',
            'User-Agent': 'VTMGO/6.5.0 (be.vmma.vtm.zenderapp; build:11019; Android 23) okhttp/3.12.1'
        })
        tokens = json.loads(response.text)

        self._token = tokens.get('jsonWebToken')
        self._name = tokens.get('name')
        self._accountId = tokens.get('accountId')

        return self._token

    @staticmethod
    def _generate_random_id(length=32):
        """ Generate a random id of the specified length.
        :type length: int
        :rtype str
        """
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(letters) for i in range(length))
