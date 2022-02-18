# import os
# import pty
# import json
# import logging
# import unittest

# from io import StringIO
# from unittest.mock import patch, mock_open, Mock

# import sys
# sys.path.insert(0, "0_1_0/")

# from modules.rec_xbee import configure_xbee

# class TestXbee(unittest.TestCase):
#     def test_confXBee(self):
#         systemJSON = StringIO("""{
#                 "serial"	:	"536780dfe639468e8e23fc568006950d",
#                 "XBEE_KY"	:	"11111111111111111111111111111111",
#                 "timezone": "America/New_York",
#                 "CurrentVersion": "0_0_0",
#                 "HUBid": 40,
#                 "Token": "5a12ff36eed2f0647a48af62e635eb8cfd4c5979",
#                 "facility": "3b9fdc97-9649-4c80-8b48-10df647bd032"
#             }""")

#         master, slave = pty.openpty()
#         s_name = os.ttyname(slave)

#         with patch('modules.rec_xbee.open') as mock_open:
#             mock_open.side_effect = [systemJSON]

#             with patch('modules.rec_xbee.serial.Serial.write') as mock_write:
#                 configure_xbee()								#Call the function to run.
#                 mock_open.assert_called()						#TEST - systemJSON was called



# if __name__ == '__main__':
#     unittest.main()
