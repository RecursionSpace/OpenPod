'''
Tests for the lookup module.
'''

import sys
import unittest

from io import StringIO
from unittest.mock import patch

from modules import rec_lookup

sys.path.insert(0, "0_1_0/")


class TestLookup(unittest.TestCase):
    '''Lokup Tests'''

    def setUp(self):
        self.nodes_json = StringIO(
                    '''[
                        {
                            "id": 1,
                            "name": "Test Node",
                            "mac": "0011223344556677",
                            "tool": false,
                            "door": false,
                            "qr_toggle": false,
                            "hub": 1,
                            "facility": "7659e76b-470c-4d5f-bff4-fcc120f08848",
                            "qr_code": null
                        }
                    ]'''
                )

        self.nodes_alternative_json = StringIO(
                    '''[
                        {
                            "id": 1,
                            "name": "Test Node",
                            "mac": "0000000000000000",
                            "tool": false,
                            "door": false,
                            "qr_toggle": false,
                            "hub": 1,
                            "facility": "7659e76b-470c-4d5f-bff4-fcc120f08848",
                            "qr_code": null
                        }
                    ]'''
                )

        self.nodes_empty_json = StringIO('')

    def test_count_matching_mac(self):
        '''
        Confirms MAC conflection is counted correctly.
        '''
        count_result = rec_lookup.count_matching_mac("12345678")
        self.assertEqual(count_result, 0)

        self.assertEqual(
            rec_lookup.count_matching_mac("0011223344556677"),
            0
        )

        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.nodes_json

            count_result = rec_lookup.count_matching_mac("0011223344556677")

            mock_open.assert_called()
            self.assertEqual(count_result, 1)

        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.nodes_alternative_json

            count_result = rec_lookup.count_matching_mac("0011223344556677")

            mock_open.assert_called()
            self.assertEqual(count_result, 0)

        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.nodes_empty_json

            self.assertEqual(
                rec_lookup.count_matching_mac("0011223344556677"),
                0
            )

            mock_open.assert_called()

class TestLookUpAccessRequest(unittest.TestCase):           # pylint: disable=R0904
    '''Access Request Tests'''

    def setUp(self):
        '''
        Collection of JSON used for testing.
        '''
        self.system_json = StringIO(
            '''{
                "serial": "536780dfe639468e8e23fc568006950d",
                "timezone": "America/New_York",
                "CurrentVersion": "0_0_0",
                "HUBid": 40,
                "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
                "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
            }'''
        )

        self.nodes_json = StringIO(
                    '''[
                        {
                            "id": 1,
                            "name": "Test Node",
                            "mac": "0011223344556677",
                            "tool": false,
                            "door": false,
                            "qr_toggle": false,
                            "hub": 1,
                            "facility": "7659e76b-470c-4d5f-bff4-fcc120f08848",
                            "qr_code": null
                        }
                    ]'''
                )

        self.members_json = StringIO(
            '''[
                {
                    "cardNumber": "313233343536373839",
                    "access_group": 123,
                    "phone_number": "1234567890",
                    "address": "1331 12th ave",
                    "city": "Altoona",
                    "state": "PA",
                    "zip_code": "16601",
                    "username": "BestName",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "email@email.com",
                    "restricted_nodes": [0,9,8]
                }
            ]'''
        )

        self.owners_json = StringIO(
            '''[
                {
                    "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032",
                    "cardNumber": "30393837363534333231",
                    "phone_number": null,
                    "address": null,
                    "city": null,
                    "state": null,
                    "zip_code": null,
                    "username": "OwnerUserName",
                    "first_name": "Jim",
                    "last_name": "John",
                    "email": "email@email.com"
                }
            ]'''
        )

        self.permissions_json = StringIO(
            '''[
                {
                    "id": 1,
                    "name": "General Access",
                    "startTime": "20:20:20",
                    "endTime": "23:23:23",
                    "monday": true,
                    "tuesday": true,
                    "wednesday": true,
                    "thursday": true,
                    "friday": true,
                    "saturday": true,
                    "sunday": true,
                    "twenty_four_seven": false,
                    "default_fallback": true,
                    "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032",
                    "allowedNodes": [1, 4, 6]
                }
            ]'''
        )

        # ----------------------------------- _alt ----------------------------------- #

        self.system_json = StringIO(
            '''{
                "serial": "536780dfe639468e8e23fc568006950d",
                "timezone": "America/New_York",
                "CurrentVersion": "0_0_0",
                "HUBid": 40,
                "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
                "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
            }'''
        )

        self.nodes_json_alt = StringIO(
                    '''[
                        {
                            "id": 1,
                            "name": "Test Node",
                            "mac": "0011223344556677",
                            "tool": false,
                            "door": false,
                            "qr_toggle": false,
                            "hub": 1,
                            "facility": "7659e76b-470c-4d5f-bff4-fcc120f08848",
                            "qr_code": null
                        }
                    ]'''
                )

        self.members_json_alt = StringIO(
            '''[
                {
                    "cardNumber": "313233343536373839",
                    "access_group": 123,
                    "phone_number": "1234567890",
                    "address": "1331 12th ave",
                    "city": "Altoona",
                    "state": "PA",
                    "zip_code": "16601",
                    "username": "BestName",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "email@email.com",
                    "restricted_nodes": [0,9,8]
                }
            ]'''
        )

        self.owners_json_alt = StringIO(
            '''[
                {
                    "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032",
                    "cardNumber": "30393837363534333231",
                    "phone_number": null,
                    "address": null,
                    "city": null,
                    "state": null,
                    "zip_code": null,
                    "username": "OwnerUserName",
                    "first_name": "Jim",
                    "last_name": "John",
                    "email": "email@email.com"
                }
            ]'''
        )

        self.permissions_json_alt = StringIO(
            '''[
                {
                    "id": 1,
                    "name": "General Access",
                    "startTime": "20:20:20",
                    "endTime": "23:23:23",
                    "monday": true,
                    "tuesday": true,
                    "wednesday": true,
                    "thursday": true,
                    "friday": true,
                    "saturday": true,
                    "sunday": true,
                    "twenty_four_seven": false,
                    "default_fallback": true,
                    "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032",
                    "allowedNodes": [1, 4, 6]
                }
            ]'''
        )

    def test_files_opened(self):
        '''
        Confirms that all the files are correctly opened and read.
        '''
        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.side_effect = [
                self.system_json,
                self.nodes_json,         # Opened from conversion function.
                self.owners_json,        # Opened from owner check function.
                self.members_json,       # Opened from get_details function.
                self.permissions_json,   # Opened from get_group_details function.
            ]

            self.assertAlmostEqual(rec_lookup.access_request(313131, '0011223344556677'), 2)
            mock_open.assert_called()

    def test_mac_to_id(self):
        '''
        Confirms that the mac address is converted to the node id.
        '''
        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.nodes_json

            node_id = rec_lookup.mac_to_id('0011223344556677')
            mock_open.assert_called()
            self.assertEqual(node_id, 1)

        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.nodes_json_alt

            node_id = rec_lookup.mac_to_id('9911223344556677')
            mock_open.assert_called()
            self.assertEqual(node_id, '9911223344556677')

    def test_is_owner(self):
        '''
        Confirms that the owner check function returns the correct value.
        '''
        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.owners_json

            owner = rec_lookup.is_owner('30393837363534333231')
            mock_open.assert_called()
            self.assertTrue(owner)

        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.owners_json_alt

            owner = rec_lookup.is_owner('99393837363534333231')
            mock_open.assert_called()
            self.assertFalse(owner)

    def test_get_details(self):
        '''
        Verifies that the correct details are returned.
        '''
        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.members_json

            user = rec_lookup.get_details('313233343536373839')
            mock_open.assert_called()
            self.assertTrue(user['found'])

        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.members_json_alt

            user = rec_lookup.get_details('993233343536373839')
            mock_open.assert_called()
            self.assertFalse(user['found'])

    def test_get_group_details(self):
        '''
        Verifies that the correct details are returned.
        '''
        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.permissions_json

            group = rec_lookup.get_group_details(1)
            mock_open.assert_called()
            self.assertTrue(group['found'])

        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.return_value = self.permissions_json_alt

            group = rec_lookup.get_group_details(69)
            mock_open.assert_called()
            self.assertFalse(group['found'])

    def test_access_request_combinations(self):
        '''
        Checks that the access request function returns the correct values.
        '''
        with patch('modules.rec_lookup.open') as mock_open:
            mock_open.side_effect = [
                self.system_json,
                self.nodes_json,         # Opened from conversion function.
                self.owners_json,        # Opened from owner check function.
                self.members_json,       # Opened from get_details function.
                self.permissions_json,   # Opened from get_group_details function.
            ]

            self.assertEqual(
                rec_lookup.access_request(313131, '0011223344556677'),
                2
            )

            mock_open.assert_called()


if __name__ == '__main__':
    unittest.main()
