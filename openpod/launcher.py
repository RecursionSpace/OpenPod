#!/usr/bin/env python3
"""
- Initiates the LED visuals

- Installs new requirements as part of an update
(if needed, might want to have a seprate process for this)

- Checks for connection to server,
- If no connection is found then LED indication is set.
- Pulls configuration files from server.
- Launches main program
"""
import sys
import json
import threading
import subprocess

# ---------------------------------------------------------------------------- #
#                              Check Requirements                              #
# ---------------------------------------------------------------------------- #
try:
    import config                                           # pylint: disable=W0611
except ImportError :
    subprocess.call(['sudo', 'pip3', 'install', 'config'])



from modules import rec_lan, rec_log
from modules.rec_log import exception_log

from settings import LED_STAT
import settings

if settings.Pi:
    try:
        from modules import rec_xbee                      # pylint: disable=C0412
    except ModuleNotFoundError as err:
        exception_log.error("%s", err)

    try:
        from modules import rec_gpio
    except ModuleNotFoundError as err:
        exception_log.error("%s", err)


# ---------------------------------------------------------------------------- #
#                             Program Start Visual                             #
# ---------------------------------------------------------------------------- #
if settings.Pi:
    led_stat_thread = threading.Thread(target = rec_gpio.led_stat_thread)
    led_stat_thread.start()

    rec_gpio.state(LED_STAT, 1, 0)


# ---------------------------------------------------------------------------- #
#                           Check Network Connection                           #
# ---------------------------------------------------------------------------- #
try:
    rec_lan.monitor_network()    #Monitors the network connection while the program is running.

except RuntimeError as err:
    exception_log.error("FATAL - Start Network Monitoring - Error: %s", err)

finally:
    exception_log.debug("Launcher - Exiting Check Network Connection")

# ---------------------------------------------------------------------------- #
#                         Update version in system.json                        #
# ---------------------------------------------------------------------------- #
#Only updates if called by bash script and environmental variable was passed in.
if len(sys.argv) > 1:
    with open("system.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        data.update( {"CurrentVersion":sys.argv[1]} )
        file.seek(0)
        json.dump(data, file)
        file.truncate()


# ---------------------------------------------------------------------------- #
#                          Logs Settings For Debugging                         #
# ---------------------------------------------------------------------------- #
try:
    public, local = rec_lan.get_ip()
    rec_log.snapshot(public, local)

except RuntimeError as err:
    exception_log.error("FAITIAL - Generate Snapshot - Error: %s", err)

finally:
    exception_log.debug("Launcher - Exiting Settings for Debugging")

# ---------------------------------------------------------------------------- #
#                              XBee Configuration                              #
# ---------------------------------------------------------------------------- #
if settings.Pi:
    with open('system.json', 'r', encoding="utf-8") as file:
        system_data = json.load(file)

    if system_data.get('XBEE_OP', False) is False:
        try:
            rec_xbee.xbee_info()
        except UnboundLocalError as err:
            exception_log.error("Unable to capture XBee info - Error: %s", err)

# ---------------------------------------------------------------------------- #
#                               Main HUB Program                               #
# ---------------------------------------------------------------------------- #
try:
    import pod                                              # pylint: disable=W0611

except RuntimeError as err:
    exception_log.error("Could not start hub.py with error: %s", err)

    # Performs Seppuku to triger bash script and perform update pull (student).
    subprocess.call(['pkill', '-f', 'hub.py'])

    # Performs Seppuku to triger bash script and perform update pull
    # (can't kill the master before the student).
    subprocess.call(['pkill', '-f', 'HUB_Launcher.py'])
