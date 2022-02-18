'''
Tests MQTT functionality.
'''
import unittest

from modules import rec_mqtt
from unittest.mock import patch, mock_open, Mock

class DummyMessage:
    def __init__(self, command):
        self.payload=command

    topic='test_hub'

class TestOnMessage(unittest.TestCase):

    def test_function_calls(self):
        with patch('modules.rec_mqtt.rec_api.link_hub') as mock_link:
            rec_mqtt.on_message('test_client', None, DummyMessage('170'))
            mock_link.assert_called()

        with patch('modules.rec_mqtt.rec_api.pull_data_dump') as mock_pull:
            rec_mqtt.on_message('test_client', None, DummyMessage('186'))
            mock_pull.assert_called()

        with patch('modules.rec_mqtt.mqtt_start_update') as mock_update:
            rec_mqtt.on_message('test_client', None, DummyMessage('202'))
            mock_update.assert_called()

        with patch('modules.rec_mqtt.rec_api.update_time_zone') as mock_timezone:
            rec_mqtt.on_message('test_client', None, DummyMessage('218'))
            mock_timezone.assert_called()

        with patch('modules.rec_mqtt.mqtt_restart_system') as mock_restart:
            rec_mqtt.on_message('test_client', None, DummyMessage('234'))
            mock_restart.assert_called()

        with patch('modules.rec_mqtt.zip_send') as mock_zip:
            rec_mqtt.on_message('test_client', None, DummyMessage('250'))
            mock_zip.assert_called()
