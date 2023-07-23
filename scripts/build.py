#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Build ZIP files for all brands. """
from __future__ import absolute_import, division, unicode_literals

import os
import shutil
import xml.etree.ElementTree as ET

DIST_DIR = 'dist'


def get_files():
    """ Get a list of files that we should package. """
    # Start with all non-hidden files
    files = [f for f in os.listdir() if not f.startswith('.')]

    # Exclude files from .gitattributes
    with open('.gitattributes', 'r') as f:
        for line in f.read().splitlines():
            filename, mode = line.split(' ')
            filename = filename.strip('/')
            if mode == 'export-ignore' and filename in files:
                files.remove(filename)

    # Exclude files from .gitignore. I know, this won't do matching
    with open('.gitignore', 'r') as f:
        for filename in f.read().splitlines():
            filename = filename.strip('/')
            if filename in files:
                files.remove(filename)

    return files


def modify_xml(file, version, news, python=None):
    """ Modify an addon.xml. """
    with open(file, 'r+') as f:
        tree = ET.fromstring(f.read())

        # Update values
        tree.set('version', version)
        tree.find("./extension[@point='xbmc.addon.metadata']/news").text = news
        if python:
            tree.find("./requires/import[@addon='xbmc.python']").set('version', python)

        # Save file
        f.seek(0)
        f.truncate()
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
                ET.tostring(tree, encoding='UTF-8').decode())


if __name__ == '__main__':
    # Read base addon.xml info
    with open('addon.xml', 'r') as f:
        tree = ET.fromstring(f.read())
        addon_info = {
            'id': tree.get('id'),
            'version': tree.get('version'),
            'news': tree.find("./extension[@point='xbmc.addon.metadata']/news").text
        }

    # Make sure dist folder exists
    if not os.path.isdir(DIST_DIR):
        os.mkdir(DIST_DIR)

    # Build addon
    brand = addon_info['id']
    dest = os.path.join(DIST_DIR, brand)
    if not os.path.isdir(dest):
        os.mkdir(dest)

    # Copy files from add-on source
    for f in get_files():
        if os.path.isfile(f):
            shutil.copy(f, dest)
        else:
            shutil.copytree(f, os.path.join(dest, f))

    # Update addon.xml for matrix and create zip
    modify_xml(os.path.join(dest, 'addon.xml'), addon_info['version'] + '+matrix.1', addon_info['news'], '3.0.0')
    shutil.make_archive(os.path.join(DIST_DIR, "%s-%s+matrix.1" % (brand, addon_info['version'])), 'zip', DIST_DIR, brand)

    # Modify addon.xml for leia and create zip
    # modify_xml(os.path.join(dest, 'addon.xml'), addon_info['version'], addon_info['news'], '2.26.0')
    # shutil.make_archive(os.path.join(DIST_DIR, "%s-%s" % (brand, addon_info['version'])), 'zip', DIST_DIR, brand)
