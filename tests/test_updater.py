'''
Tests for update.py
'''

import sys
import unittest

from io import StringIO
from unittest.mock import patch
from unit

import updater  # OpenPod Updater

sys.path.insert(0, "openpod/")


class TestUpdater(unittest.TestCase):
    '''Collection of tests.'''

    def setUp(self):

        self.system_json = {
            "serial": "536780dfe639468e8e23fc568006950d",
            "timezone": "America/New_York",
            "version": "0_0_0",
            "HUBid": 40,
            "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
            "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
        }

    def test_get_current_versions(self):
        '''
        Verify that the current versions are returned.
        '''

        with patch('updater.open') as mock_open:
            mock_open.side_effect = [self.system_json, self.system_json]
            self.assertEqual(updater.update_pod(), "0_0_0")
            mock_open.assert_called()


if __name__ == '__main__':
    unittest.main()
