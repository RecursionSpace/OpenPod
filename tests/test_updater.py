'''
Tests for update.py
'''

import os
import builtins
import unittest

from io import StringIO
from unittest.mock import patch, mock_open, Mock

import hub_updater

import sys
sys.path.insert(0, "0_1_0/")

class TestUpdater(unittest.TestCase):
    '''Collection of tests.'''

    def test_get_current_versions(self):
        '''Verify that the current versions are returned.'''
        systemJSON = StringIO("""{
                        "serial": "536780dfe639468e8e23fc568006950d",
                        "timezone": "America/New_York",
                        "CurrentVersion": "0_0_0",
                        "HUBid": 40,
                        "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
                        "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
                    }""")

        with patch('hub_updater.open') as mock_open:
            mock_open.side_effect = [systemJSON, systemJSON]
            hub_updater.current_hub_version()
            # hub_updater.update_version_name()
            mock_open.assert_called()

if __name__ == '__main__':
	unittest.main()
