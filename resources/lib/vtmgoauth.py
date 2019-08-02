# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import json
import logging
import random
import re

import requests
from requests.exceptions import InvalidSchema
from xbmcaddon import Addon

from resources.lib.kodiutils import proxies

ADDON = Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))


class VtmGoAuth:
    def __init__(self, username, password):
        self._username = username
        self._password = password

        self._token = None
        self._name = None
        self._accountId = None

    def login(self):
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
                'userName': self._username,
                'password': self._password,
                'jsEnabled': 'true',
            })

            if 'Wachtwoord is niet correct' in response.text:
                raise Exception('Invalid login details')

            raise Exception('Unknown error while logging in')

        except InvalidSchema as e:
            # We get back an url like this: vtmgo://callback/oidc?state=yyyyyyyyyyyyyyyyyyyyyy&code=xxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx
            # I found no other way to get this url then by parsing the Exception message. :(
            matches = re.search(r"code=([^']+)", e.message)
            if matches:
                code = matches.group(1)
            else:
                raise Exception('Could not extract authentication code')

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

        self._token = tokens['jsonWebToken']
        self._name = tokens['name']
        self._accountId = tokens['accountId']

        return self._token

    def _generate_random_id(self, length=32):
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(letters) for i in range(length))
