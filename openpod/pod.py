'''
Recursion.Space
Email: jmerrell@recursion.space
Phone: 240-342-6671
'''

import sys
import os.path  # Allows modules to access from directory above.
import threading
from time import sleep
import config
import requests
from pubsub import pub

import pod_config
from modules import op_config, op_gpio, op_ssh, rec_log, rec_mqtt, rec_xbee, rec_api, rec_lan
from modules.rec_log import exception_log, zip_send


settings = pod_config.load_config()

# --------------------------- Visualization Threads --------------------------- #
threading.Thread(target=op_gpio.led_stat_thread).start()
threading.Thread(target=op_gpio.led_io_thread).start()

op_gpio.initializing()


# ---------------------------------------------------------------------------- #
#                           Check Network Connection                           #
# ---------------------------------------------------------------------------- #
try:
    rec_lan.monitor_network()  # Monitors the network connection while the program is running.
except RuntimeError as err:
    exception_log.error(f"FATAL - Start Network Monitoring - Error: {err}")


# Not sure if the next section is required.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

Version = settings['openpod']['version']

# Inserts path to reference then starts importing modules.
sys.path.insert(0, f"./{Version}")
sys.path.insert(1, f"./{Version}/modules")
sys.path.append("..")


config.XBEE_FLAG = False


def incoming_xbee_data():
    '''
    Required functions to handle events and related status checking activities.
    '''
    config.XBEE_FLAG = True


pub.subscribe(incoming_xbee_data, 'xbee_rx')

begin_xbee = threading.Thread(target=rec_xbee.listing)
begin_xbee.start()


# Register Pod with Recursion.Space
if not op_config.get('pod_id', False):
    rec_api.register_pod()


# ------------------------------- TEMP SOLUTION ------------------------------ #
try:
    URL = f'https://{settings["url"]}/pod/obtaintoken/{settings["uuid"]}/'
    response = requests.get(URL, timeout=10)

    if response.status_code == 201:
        op_config.set_value("api_token", response.text)

except Exception as err:                                # pylint: disable=W0703
    print(err)
# ------------------------------- TEMP SOLUTION ------------------------------ #

if settings['debug']:
    rec_log.publog("debug", "*** DEBUG Enabled ***")

rec_log.publog("info", f"Version: {Version}")

rec_api.keepalive()

MQTTlisten = threading.Thread(target=rec_mqtt.mqtt_rx)
MQTTlisten.start()


# Only pull info if hub has already been paired with a facility.
try:
    if op_config.get('space', False):
        rec_log.publog("info", "Pulling any missing data.")
        rec_api.pull_data_dump()
        rec_api.update_time_zone()
        op_ssh.update_keys()
    else:
        rec_log.publog("info", "Facility connection not found, no data to pull.")
        op_gpio.unregistered()  # Slow blink ready to pair to a facility.

    zip_send()  # Send latest log files on boot.
except Exception as err:                                # pylint: disable=W0703
    rec_log.publog("error", f"Error occurred when pulling data: {err}")


# ---------------------------------------------------------------------------- #
#                              XBee Configuration                              #
# ---------------------------------------------------------------------------- #
if op_config.get('XBEE').get('OP', False) is False:
    try:
        rec_xbee.xbee_info()
    except UnboundLocalError as err:
        exception_log.error("Unable to capture XBee info - Error: %s", err)


# ---------------------------------------------------------------------------- #
#                          Logs Settings For Debugging                         #
# ---------------------------------------------------------------------------- #
try:
    public_ip, local_ip = rec_lan.get_ip()
    rec_log.snapshot(public_ip, local_ip)
except RuntimeError as err:
    exception_log.error("FATAL - Generate Snapshot - Error: %s", err)


rec_log.publog("info", "Recursion system has successfully initiated.")


def process_xbee_data():
    '''
    Triggered when there is available XBee data.
    '''
    xbee_frame_info = rec_xbee.receive()  # Reads in received XBee data.
    op_gpio.ready()  # Pod is ready.
    if xbee_frame_info[2] == 0:
        rec_xbee.transmit(xbee_frame_info[0], "30")
    elif xbee_frame_info[2] == 1:
        rec_xbee.transmit(xbee_frame_info[0], "31")
    elif xbee_frame_info[2] == 2:
        rec_xbee.transmit(xbee_frame_info[0], "32")
    elif xbee_frame_info[2] == 5:
        pass
    else:
        rec_xbee.transmit(xbee_frame_info[0], "32")


# https://stackoverflow.com/questions/10926328/efficient-and-fast-python-while-loop-while-using-sleep
# https://stackoverflow.com/questions/17553543/pyserial-non-blocking-read-loop
while True:
    if config.XBEE_FLAG:
        op_gpio.incoming_data()  # Pod is receiving XBee data.
        DataProcessing = threading.Thread(target=process_xbee_data)
        DataProcessing.start()
        sleep(.05)
        config.XBEE_FLAG = False
    sleep(.01)
