''' Tests for rec_api.py '''

import sys
import unittest

from io import StringIO
from unittest.mock import patch

from modules import rec_api

sys.path.insert(0, "0_1_0/")


class TestAPI(unittest.TestCase):
    '''Collection of tests for the api module'''

    def test_pull_data_dump(self):
        '''Test the pull_data_dump function'''

        system_json = StringIO("""{
                "serial": "536780dfe639468e8e23fc568006950d",
                "timezone": "America/New_York",
                "CurrentVersion": "0_0_0",
                "HUBid": 40,
                "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
                "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
            }""")

        testdata2 = StringIO("""{
                "serial": "536780dfe639468e8e23fc568006950d",
                "timezone": "America/New_York",
                "CurrentVersion": "0_0_0",
                "HUBid": 40,
                "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
                "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
            }""")

        testdata3 = StringIO("""{
                "serial": "536780dfe639468e8e23fc568006950d",
                "timezone": "America/New_York",
                "CurrentVersion": "0_0_0",
                "HUBid": 40,
                "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
                "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
            }""")

        testdata4 = StringIO("""{
                "serial": "536780dfe639468e8e23fc568006950d",
                "timezone": "America/New_York",
                "CurrentVersion": "0_0_0",
                "HUBid": 40,
                "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
                "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
            }""")

        testdata5 = StringIO("""{
                "serial": "536780dfe639468e8e23fc568006950d",
                "timezone": "America/New_York",
                "CurrentVersion": "0_0_0",
                "HUBid": 40,
                "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
                "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
            }""")

        testreturn = [{
                "cardNumber": "3132323637373936",
                "access_group": 7,
                "phone_number": "2403426671",
                "address": "123 America Ln",
                "city": "USA City",
                "state": "PA",
                "zip_code": " 1234567",
                "username": "GenericMember2",
                "first_name": "Gener",
                "last_name": "Mem",
                "email": "member@email.com",
                "restricted_nodes": []
            }, {
                "cardNumber": "33",
                "access_group": 5,
                "phone_number": "2403426671",
                "address": "",
                "city": "",
                "state": "",
                "zip_code": "",
                "username": "GenericMember3",
                "first_name": "Generic",
                "last_name": "Member3",
                "email": "generic@email.com",
                "restricted_nodes": ["123", "shdfhethetbe"]
            }]

        with patch('modules.rec_api.open') as mock_open:
            mock_open.side_effect  = [system_json, testdata2, testdata3, testdata4, testdata5]

            with patch("modules.rec_api.requests.get") as mocked_requests:
                mocked_requests.return_value.json.return_value = testreturn
                rec_api.pull_data_dump()
                mock_open.assert_called()
                mocked_requests.assert_called()

if __name__ == '__main__':
    unittest.main()
