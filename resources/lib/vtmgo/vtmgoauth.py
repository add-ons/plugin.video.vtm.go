# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import hashlib
import json
import random

import requests

from resources.lib.kodiwrapper import LOG_DEBUG, KodiWrapper, from_unicode, LOG_INFO  # pylint: disable=unused-import


class InvalidLoginException(Exception):
    pass


class VtmGoAuth:
    def __init__(self, kodi):
        self._kodi = kodi  # type: KodiWrapper
        self._proxies = kodi.get_proxies()

        self._token = None
        # self._name = None
        # self._accountId = None

        self.username = kodi.get_setting('username')
        self.password = kodi.get_setting('password')

        if self._credentials_changed():
            kodi.log('Clearing auth tokens due to changed credentials', LOG_INFO)
            self.clear_token()

    def _credentials_changed(self):
        """ Check if credentials have changed """
        old_hash = self._kodi.get_setting('credentials_hash')
        new_hash = ''
        if self.username or self.password:
            new_hash = hashlib.md5((self.username + self.password).encode('utf-8')).hexdigest()
        if new_hash != old_hash:
            self._kodi.set_setting('credentials_hash', new_hash)
            return True
        return False

    def clear_token(self):
        """ Remove the cached JWT. """
        self._kodi.log('Clearing token cache', LOG_DEBUG)
        self._token = None
        path = self._kodi.get_userdata_path() + 'token.json'
        if self._kodi.check_if_path_exists(path):
            self._kodi.delete_file(path)

    def get_token(self):
        """ Return a JWT that can be used to authenticate the user.
        :rtype str
        """
        # Don't return a token when we have no password or username.
        if not self.username or not self.password:
            self._kodi.log('Skipping since we have no username or password')
            return None

        # Return if we already have the token in memory.
        if self._token:
            self._kodi.log('Returning token from memory', LOG_DEBUG)
            return self._token

        # Try to load from cache
        path = self._kodi.get_userdata_path() + 'token.json'
        if self._kodi.check_if_path_exists(path):
            self._kodi.log('Returning token from cache', LOG_DEBUG)

            with self._kodi.open_file(path) as f:
                self._token = f.read()

            if self._token:
                return self._token

        # Authenticate with VTM GO and store the token
        self._token = self._login()
        self._kodi.log('Returning token from vtm go', LOG_DEBUG)

        with self._kodi.open_file(path, 'w') as f:
            f.write(from_unicode(self._token))

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
        }, proxies=self._proxies)

        # Now, send the login details. We will be redirected to vtmgo:// when we succeed. We then can extract an authorizationCode that we need to continue.
        try:
            response = session.post('https://login2.vtm.be/login/emailfirst/password?client_id=vtm-go-android', data={
                'userName': self.username,
                'password': self.password,
                'jsEnabled': 'true',
            }, proxies=self._proxies)

            if 'errorBlock-OIDC-004' in response.text:  # E-mailadres is niet gekend.
                raise InvalidLoginException()

            if 'errorBlock-OIDC-003' in response.text:  # Wachtwoord is niet correct.
                raise InvalidLoginException()

            raise Exception(self._kodi.localize(30702))  # Unknown error while logging in

        except requests.exceptions.InvalidSchema as e:
            # We get back an url like this: vtmgo://callback/oidc?state=yyyyyyyyyyyyyyyyyyyyyy&code=xxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx
            # I found no other way to get this url then by parsing the Exception message. :(
            import re
            matches = re.search(r"code=([^']+)", str(e))
            if matches:
                code = matches.group(1)
            else:
                raise Exception(self._kodi.localize(30703))  # Could not extract authentication code

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
        }, proxies=self._proxies)
        tokens = json.loads(response.text)

        self._token = tokens.get('jsonWebToken')
        # self._name = tokens.get('name')
        # self._accountId = tokens.get('accountId')

        return self._token

    @staticmethod
    def _generate_random_id(length=32):
        """ Generate a random id of the specified length.
        :type length: int
        :rtype str
        """
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(letters) for i in range(length))
