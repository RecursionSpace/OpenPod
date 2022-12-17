#!/usr/bin/env python3
"""
Recursion.Space
Email: jmerrell@recursion.space
Phone: 240-342-6671
"""

import sys
import os.path  # Allows modules to access from directory above.
import json
import threading
from time import sleep
import config
import requests
from pubsub import pub

import settings

from modules import op_gpio, rec_log, rec_mqtt, rec_xbee, rec_api, rec_lan
from modules.rec_log import exception_log, zip_send

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
    exception_log.error("FATAL - Start Network Monitoring - Error: %s", err)

finally:
    exception_log.debug("Launcher - Exiting Check Network Connection")


# Not sure if the next section is required.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

with open('/opt/RecursionHub/system.json', 'r+', encoding="utf-8") as system_file:
    systemConfig = json.load(system_file)
Version = systemConfig['CurrentVersion']

# Inserts path to refrence then starts importing modules.
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


# Register HUB with Recursion
if not systemConfig.get('HUBid', False):
    rec_api.register_hub()


# ------------------------------- TEMP SOLUTION ------------------------------ #
try:
    URL = f'{settings.RecursionURL}/obtaintoken/{systemConfig["serial"]}/'
    r = requests.get(URL, timeout=10)

    if r.status_code == 201:
        print(f"Hub Toekn: {r.text}")
        with open("/opt/RecursionHub/system.json", "r+", encoding="UTF-8") as file:
            data = json.load(file)
        data.update({"Token": f"{r.text}"})
        file.seek(0)
        json.dump(data, file)
        file.truncate()
except Exception as err:                                # pylint: disable=W0703
    print(err)
# ------------------------------- TEMP SOLUTION ------------------------------ #

if settings.DEBUG:
    rec_log.publog("debug", "*** DEBUG Enabled ***")
if settings.Pi:
    rec_log.publog("debug", "*** PI TRUE ***")
if not settings.Pi:
    rec_log.publog("debug", "*** PI FALSE ***")

rec_log.publog("info", f"Version: {Version}")

rec_api.keepalive()

MQTTlisten = threading.Thread(target=rec_mqtt.mqtt_rx)
MQTTlisten.start()


# Only pull info if hub has already been paired with a facility.
try:
    if 'facility' in systemConfig:
        rec_log.publog("info", "Pulling any missing data.")
        rec_api.pull_data_dump()
        rec_api.update_time_zone()
    else:
        rec_log.publog("info", "Facility connection not found, no data to pull.")
        op_gpio.unregistered()  # Slow blink ready to pair to a facility.

    zip_send()  # Send latest log files on boot.
except Exception as err:                                # pylint: disable=W0703
    rec_log.publog("error", f"Error occurred when pulling data: {err}")


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
