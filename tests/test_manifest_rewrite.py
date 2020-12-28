# -*- coding: utf-8 -*-
""" Tests for VTM GO API """

# pylint: disable=invalid-name,missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

from resources.lib.modules.proxy import Proxy

_LOGGER = logging.getLogger(__name__)


class TestManifestRewrite(unittest.TestCase):
    """ Tests for VTM GO API """

    def test_rewrite(self):
        self.maxDiff = None
        tests = [
            ('manifest_01_input.txt', 'manifest_01_output.txt'),  # Uses SegmentTemplates
            ('manifest_02_input.txt', 'manifest_02_output.txt'),  # Uses SegmentLists
            ('manifest_03_input.txt', 'manifest_03_output.txt'),  # Uses a combination of SegmentTemplates and SegmentLists
        ]

        for test_input, test_output in tests:
            with open('tests/proxy/' + test_input, 'r') as fdesc:
                manifest_input = fdesc.read()

            with open('tests/proxy/' + test_output, 'r') as fdesc:
                manifest_output = fdesc.read()

            manifest_modified = Proxy.modify_manifest(manifest_input)
            self.assertEqual(manifest_modified, manifest_output)


if __name__ == '__main__':
    unittest.main()
