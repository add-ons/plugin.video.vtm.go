#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Publish a ZIP file to the Kodi repository. """

# Based on code from https://github.com/xbmc/kodi-addon-submitter

from __future__ import absolute_import, division, unicode_literals

import logging
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pprint import pformat
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import requests

_LOGGER = logging.getLogger(__name__)

GH_REPO = 'repo-plugins'
GH_USERNAME = os.getenv('GH_USERNAME')
GH_TOKEN = os.getenv('GH_TOKEN')
GH_EMAIL = os.getenv('EMAIL')


def get_addon_info(xml: str):
    """ Parse the passed addon.xml file and extract some information. """
    tree = ET.fromstring(xml)
    return {
        'id': tree.get('id'),
        'name': tree.get('name'),
        'version': tree.get('version'),
        'description': tree.find("./extension[@point='xbmc.addon.metadata']/description").text,
        'news': tree.find("./extension[@point='xbmc.addon.metadata']/news").text,
        'python': tree.find("./requires/import[@addon='xbmc.python']").get('version'),
        'source': tree.find("./extension[@point='xbmc.addon.metadata']/source").text,
    }


def user_fork_exists(repo, gh_username, gh_token):
    """ Check if the user has a fork of the repository on Github. """
    resp = requests.get(
        'https://api.github.com/repos/{}/{}'.format(
            gh_username,
            repo
        ),
        headers={'Accept': 'application/vnd.github.v3+json'},
        params={
            'type': 'all'
        },
        auth=(gh_username, gh_token)
    )
    resp_json = resp.json()
    return resp.ok and resp_json.get('fork')


def create_personal_fork(repo, gh_username, gh_token):
    """Create a personal fork for the official repo on GitHub. """
    resp = requests.post(
        'https://api.github.com/repos/xbmc/{}/forks'.format(
            repo
        ),
        headers={'Accept': 'application/vnd.github.v3+json'},
        auth=(gh_username, gh_token)
    )
    if resp.ok:
        elapsed_time = 0
        while elapsed_time < 5 * 60:
            if not user_fork_exists(repo, gh_username, gh_token):
                time.sleep(20)
                elapsed_time += 20
            else:
                return
        raise Exception("Timeout waiting for fork creation exceeded")
    raise Exception('GitHub API error: {}\n{}'.format(resp.status_code, resp.text))


def shell(*args):
    """ Execute a shell command. """
    subprocess.run(args, check=True)


def create_addon_branch(repo, branch, source, addon_info, gh_username, gh_token, gh_email):
    """ Create and addon branch in your fork of the respective addon repo. """
    cur_dir = os.getcwd()
    os.chdir('dist')

    local_branch_name = '{}@{}'.format(addon_info['id'], branch)

    if os.path.isdir(repo):
        # We already have a checked out repo locally, update this with upstream code
        os.chdir(repo)
        shell('git', 'reset', '--hard')  # Remove all local changes
        shell('git', 'remote', 'set-branches', '--add', 'upstream', branch)  # Make sure the upstream branch exists
        shell('git', 'fetch', '-f', 'upstream', branch)  # Fetch upstream
    else:
        # Clone the upstream repo
        shell('git', 'clone', '--branch', branch, '--origin', 'upstream', '--single-branch', 'git://github.com/xbmc/{}.git'.format(repo))
        os.chdir(repo)

    # Create local branch
    shell('git', 'checkout', '-B', local_branch_name, 'upstream/{}'.format(branch))

    # Remove current code
    if os.path.isdir(addon_info['id']):
        shutil.rmtree(addon_info['id'], ignore_errors=False)

    # Add new code
    shutil.copytree(source, addon_info['id'])
    shell('git', 'add', '--', addon_info['id'])
    shell('git', 'status')

    # Create a commit with the new code
    shell('git', 'config', 'user.name', gh_username)
    shell('git', 'config', 'user.email', gh_email)
    shell('git', 'commit', '-m', '[{}] {}'.format(addon_info['id'], addon_info['version']))

    # Push branch to fork
    shell('git', 'push', '-f', 'https://{}:{}@github.com/{}/{}.git'.format(gh_username, gh_token, gh_username, repo), local_branch_name)

    # Restore working directory
    os.chdir(cur_dir)


def create_pull_request(repo, branch, addon_info, gh_username, gh_token):
    """ Create a pull request in the official repo on GitHub. """

    local_branch_name = '{}@{}'.format(addon_info['id'], branch)

    # Check if pull request already exists.
    resp = requests.get(
        'https://api.github.com/repos/xbmc/{}/pulls'.format(repo),
        params={
            'head': '{}:{}'.format(gh_username, local_branch_name),
            'base': branch,
        },
        headers={'Accept': 'application/vnd.github.v3+json'},
        auth=(gh_username, gh_token)
    )

    if resp.status_code == 200 and not resp.json():
        # Create a new Pull Request
        template = """### Description

- **General**
  - Add-on name: {name}
  - Add-on ID: {id}
  - Version number: {version}
  - Kodi/repository version: {kodi_repo_branch}

- **Code location**
  - URL: {source}

{description}

### What's new

{news}

### Checklist:
- [X] My code follows the [add-on rules](http://kodi.wiki/view/Add-on_rules) and [piracy stance](http://kodi.wiki/view/Official:Forum_rules#Piracy_Policy) of this project. 
- [X] I have read the [CONTRIBUTING](https://github.com/xbmc/repo-plugins/blob/master/CONTRIBUTING.md) document
- [X] Each add-on submission should be a single commit with using the following style: [plugin.video.foo] v1.0.0
"""
        pr_body = template.format(
            name=addon_info['name'],
            id=addon_info['id'],
            version=addon_info['version'],
            kodi_repo_branch=branch,
            source=addon_info['source'],
            description=addon_info['description'],
            news=addon_info['news']
        )
        resp = requests.post(
            'https://api.github.com/repos/xbmc/{}/pulls'.format(repo),
            json={
                'title': '[{}] {}'.format(local_branch_name, addon_info['version']),
                'head': '{}:{}'.format(gh_username, local_branch_name),
                'base': branch,
                'body': pr_body,
                'maintainer_can_modify': True,
            },
            headers={'Accept': 'application/vnd.github.v3+json'},
            auth=(gh_username, gh_token)
        )
        if resp.status_code != 201:
            raise Exception('GitHub API error: {}\n{}'.format(resp.status_code, pformat(resp.json())))

    elif resp.status_code == 200 and resp.json():
        _LOGGER.info('Pull request in {} for {}:{} already exists.'.format(branch, gh_username, local_branch_name))

    else:
        raise Exception('Unexpected GitHub error: {}\n{}'.format(resp.status_code, pformat(resp.json())))


if __name__ == '__main__':
    filenames = sys.argv[1:]

    for filename in filenames:
        # Fork the repo if the user does not have a personal repo fork
        if not user_fork_exists(GH_REPO, GH_USERNAME, GH_TOKEN):
            create_personal_fork(GH_REPO, GH_USERNAME, GH_TOKEN)

        with TemporaryDirectory() as extract_dir:
            with ZipFile(filename) as z:
                # Look for addon.xml in zip and load the details
                xmlfile = next(f.filename for f in z.filelist if f.filename.endswith('addon.xml'))
                addon_info = get_addon_info(z.read(xmlfile).decode('utf-8'))
                if addon_info['python'] != '3.0.0':
                    branch = 'leia'
                else:
                    branch = 'matrix'

                # Extract the ZIP file to the extract_dir
                z.extractall(extract_dir)

            # Checkout the fork locally and create a branch with our new code from the extract_dir
            create_addon_branch(GH_REPO, branch, os.path.join(extract_dir, addon_info['id']), addon_info, GH_USERNAME, GH_TOKEN, GH_EMAIL)

        # Create pull request
        create_pull_request(GH_REPO, branch, addon_info, GH_USERNAME, GH_TOKEN)
