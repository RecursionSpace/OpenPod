import os
import pty
import json
import logging
import unittest

from io import StringIO
from unittest.mock import patch, mock_open, Mock

import sys
sys.path.insert(0, "0_1_0/")

from modules import rec_lan, rec_api, rec_xbee, rec_log


class Testlog(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }

if __name__ == '__main__':
	unittest.main()
