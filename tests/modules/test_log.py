''' Tests for rec_log.py '''

import sys
import logging
import unittest

#from modules import rec_lan, rec_api, rec_xbee, rec_log

sys.path.insert(0, "0_1_0/")

class Testlog(unittest.TestCase):
    ''' Tests for the log module '''

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
