import sys
sys.path.insert(0, "0_1_0/")

import unittest

# import hub

# class TestHub(unittest.TestCase):
#     '''
#     General tests for the hub.py file
#     '''
#     def test_xbee_flag_set_true(self):
#         '''
#         Check if the xbee flag is set to true.
#         '''
#         global XBEE_FLAG
#         XBEE_FLAG = False
#         hub.incoming_xbee_data()
#         self.assertTrue(XBEE_FLAG)