''' Unit testing for rec_lan.py '''

import sys
import unittest

from unittest.mock import patch

from modules import rec_lan

sys.path.insert(0, "openpod/")


class TestLan(unittest.TestCase):
    ''' Tests for the lan module '''

    def test_monitor_network(self):
        '''
        Confirm that the network monitor is running.
        '''
        with patch('modules.rec_lan.test_network') as mocked_test_network:
            mocked_test_network.return_value = 0

            with patch('modules.op_system.is_pi') as mocked_is_pi:
                mocked_is_pi.return_value = False

                with patch('modules.rec_lan.threading') as mocked_threading:
                    self.assertTrue(rec_lan.monitor_network())
                    mocked_threading.Timer.assert_called()

    def test_test_network(self):
        '''
        Confirms all tests are called properly.
        '''
        with patch('modules.rec_lan.networked') as mocked_networked:
            mocked_networked.return_value = False
            self.assertEqual(rec_lan.test_network(), 0)

            mocked_networked.return_value = True
            self.assertNotEqual(rec_lan.test_network(), 0)

            with patch('modules.rec_lan.internet_on') as mocked_internet_on:
                mocked_internet_on.return_value = False
                self.assertEqual(rec_lan.test_network(), 1)

                mocked_internet_on.return_value = True
                self.assertNotEqual(rec_lan.test_network(), 1)

                with patch('modules.rec_lan.recursion_connection') as mocked_recursion_connection:
                    mocked_recursion_connection.return_value = False
                    self.assertEqual(rec_lan.test_network(), 2)

                    mocked_recursion_connection.return_value = True
                    self.assertEqual(rec_lan.test_network(), 3)

        self.assertTrue(mocked_networked.called)
        self.assertTrue(mocked_internet_on.called)
        self.assertTrue(mocked_recursion_connection.called)

    def test_networked(self):
        '''
        Confirm that the network is active.
        '''
        with patch('modules.rec_lan.get_ip') as mocked_get_ip:
            mocked_get_ip.return_value = ("127.0.0.1", "127.0.0.1")
            self.assertFalse(rec_lan.networked())

            mocked_get_ip.return_value = ("192.168.1.1", "192.168.1.1")
            self.assertTrue(rec_lan.networked())

    def test_internet_on(self):
        '''
        Confirms active internet connection.
        '''
        self.assertTrue(rec_lan.internet_on())

        with patch('modules.rec_lan.requests.get') as mocked_requests:
            mocked_requests.return_value.status_code = None
            self.assertFalse(rec_lan.internet_on())

    def test_recursion_connection(self):
        '''
        Confirms that the recursion server is reachable.
        '''
        self.assertTrue(rec_lan.recursion_connection())

        with patch('modules.rec_lan.requests.get') as mocked_requests:
            mocked_requests.return_value.status_code = None
            self.assertFalse(rec_lan.internet_on())

    def test_get_ip(self):
        '''
        Verify that the ip address is obtained.
        '''
        with patch('modules.rec_lan.internet_on') as mocked_internet_on:
            mocked_internet_on.return_value = True

            with patch('modules.rec_lan.requests.get') as mocked_requests:
                mocked_requests.return_value.text = "0.0.0.0"
                public_ip, local_ip = rec_lan.get_ip()

                self.assertEqual((rec_lan.get_ip())[0], '0.0.0.0')
                self.assertEqual(public_ip, '0.0.0.0')
                self.assertNotEqual(local_ip, '127.0.0.1')

                mocked_internet_on.return_value = False
                self.assertNotEqual((rec_lan.get_ip())[0], '0.0.0.0')


if __name__ == '__main__':
    unittest.main()
