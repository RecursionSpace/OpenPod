#!/usr/bin/python

'''
MQTT communication manager.
'''
import os
import re
import json
import subprocess
import paho.mqtt.client as mqtt

from modules import op_config, rec_api, rec_xbee, rec_lookup
from modules.rec_log import mqtt_log, exception_log, zip_send
import updater

# The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, return_code):
    '''
    Action taken once a connection has been established.
    '''
    mqtt_log.info("MQTT connected with result code %s", str(return_code))
    mqtt_log.info("MQTT connected with userdata: %s", str(userdata))
    mqtt_log.info("MQTT connected with flags: %s", str(flags))

    with open('system.json', 'r+', encoding="UTF-8") as file:
        system_data = json.load(file)
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(f"{system_data['serial']}")


def on_message(client, userdata, message):
    '''
    Handles messages coming in via MQTT.
    170 - Pairing un-paired Hub
    186 - Pull New Data
    202 - Install System Update
    218 - Timezone Change
    234 - Reboot Hub (Soft restart)
    250  - Zip & Send Logs

    Node Command - xxxxxxxxxxxxxxxx_##
    '''
    mqtt_log.info("on_message - payload: %s %s", message.topic, str(message.payload))
    mqtt_log.info("on_message - userdata: %s", str(userdata))
    mqtt_log.info("on_message - client: %s", str(client))

    try:
        mqtt_actions = {
            170: rec_api.link_hub,
            186: rec_api.pull_data_dump,
            202: mqtt_start_update,
            218: rec_api.update_time_zone,
            234: mqtt_restart_system,
            250: zip_send,
        }

        if 0 < int(message.payload) <= 256:
            mqtt_actions[int(message.payload)]()
            return True

    except ValueError as err:
        mqtt_log.info("Not a single number command. Error: %s", err)

    try:
        # Check for node specific  action instruction if no match found.
        # This can eventually be split into a seprate topic for MQTT or use JSON formatting.
        node_mac = re.match(r'^(?:.*\')*([^_]+)', str(message.payload))     # Seperate MAC
        node_command = re.match(r'^(?:.*_)([^\']*)', str(message.payload))  # Seperate Command

        mqtt_log.info("MAC: %s --- Command: %s", node_mac.group(1), node_command.group(1))

        look_up_responce = rec_lookup.count_matching_mac(node_mac.group(1))

        mqtt_log.info("Found %s matching MACs", look_up_responce)

        if look_up_responce == 1:
            rec_xbee.transmit(node_mac.group(1), f"{node_command.group(1)}")
            return True

    except IndexError as err:
        mqtt_log.error("Unable to extract MAC with the following error: %s", err)

    mqtt_log.error("MQTT did not match action codes. Payload: %s", message.payload)

    return False


def mqtt_rx():
    '''
    Establish a connection to the Recursion.Space MQTT broker
    Define what happens when the following actions occur:
    - Connection to the MQTT broker is made.
    - A message is received.
    '''
    mqtt_log.info('Connecting to MQTT broker')

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(f"{op_config.get('url')}", 1883, 60)
    client.loop_forever()


def mqtt_start_update():
    '''
    Called by the MQTT function handler to start an update.
    '''
    mqtt_log.info("UPDATE AVAILABLE - Triggered by the user.")
    try:
        updater.update_hub()
    except RuntimeError as err:
        exception_log.error("Error while updating, atempting as subprocess. %s", err)
        update_location = f'/opt/OpenPod/{op_config.get("version")}/updater.py'
        with subprocess.Popen(['sudo', 'python3', f'{update_location}']) as script:
            print(script)


def mqtt_restart_system():
    '''
    Called by the MQTT function handler to restart the system.
    '''
    os.system('systemctl reboot -i')
