# -*- coding: utf-8 -*-
""" Tests for Manifest rewrite """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib.modules.proxy import Proxy

_LOGGER = logging.getLogger(__name__)


class TestManifestRewrite(unittest.TestCase):
    """ Tests for Manifest rewrite """

    def test_rewrite(self):
        self.maxDiff = None
        tests = [
            ('manifest_01_input.xml', 'manifest_01_output.xml'),  # Uses SegmentTemplates
            ('manifest_02_input.xml', 'manifest_02_output.xml'),  # Uses SegmentLists
            ('manifest_03_input.xml', 'manifest_03_output.xml'),  # Uses a combination of SegmentTemplates and SegmentLists
        ]

        for test_input, test_output in tests:
            with open('tests/manifest_rewrite/' + test_input, 'r') as fdesc:
                manifest_input = fdesc.read()

            with open('tests/manifest_rewrite/' + test_output, 'r') as fdesc:
                manifest_output = fdesc.read()

            manifest_modified = Proxy.modify_manifest(manifest_input)
            self.assertEqual(manifest_modified, manifest_output)


if __name__ == '__main__':
    unittest.main()
