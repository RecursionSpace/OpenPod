#!/usr/bin/env python3
'''
Recursion System - Logging Module
The infrastructure for all logging and debugging data collection.
'''

import os.path
import time
import json
import hashlib
import logging
from zipfile import ZipFile
import requests
import simplejson as json
# https://stackoverflow.com/questions/21663800/python-make-a-list-generator-json-serializable

from modules import op_config

import settings

try:
    from pip._internal.operations import freeze
except ImportError:
    from pip.operations import freeze

# ---------------------------------------------------------------------------- #
#                          General Log Configurations                          #
# ---------------------------------------------------------------------------- #
standard_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%y-%m-%d %H:%M:%S')
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)  # Sets default level to INFO for all logs

console = logging.StreamHandler()
console.setFormatter(standard_format)

# ---------------------------------------------------------------------------- #
#                          Specific Log Configurations                         #
# ---------------------------------------------------------------------------- #

# ------------------------------- Exception Log ------------------------------ #
exception_log = logging.getLogger('exception_log')

if settings.DEBUG:
    exception_log.setLevel(logging.DEBUG)

try:
    exception_log_file = logging.FileHandler('/opt/OpenPod/logs/exception.log', mode='a')
except FileNotFoundError:
    exception_log_file = logging.FileHandler('tests/exception.log', mode='a')  # CI Testing

exception_log_file.setFormatter(standard_format)
exception_log.addHandler(exception_log_file)
exception_log.addHandler(console)

# -------------------------- Recursion.Space API Log ------------------------- #
log_api = logging.getLogger('log_api')

if settings.DEBUG:
    log_api.setLevel(logging.DEBUG)

try:
    log_api_file = logging.FileHandler('/opt/OpenPod/logs/api.log', mode='a')
except FileNotFoundError:
    log_api_file = logging.FileHandler('tests/api.log', mode='a')  # CI Testing

log_api_file.setFormatter(standard_format)
log_api.addHandler(log_api_file)
log_api.addHandler(console)

# -------------------------------- Network Log ------------------------------- #
network_log = logging.getLogger('network_log')

if settings.DEBUG:
    network_log.setLevel(logging.DEBUG)

try:
    network_log_file = logging.FileHandler('/opt/OpenPod/logs/network.log', mode='a')
except FileNotFoundError:
    network_log_file = logging.FileHandler('tests/network.log', mode='a')  # CI Testing

network_log_file.setFormatter(standard_format)
network_log.addHandler(network_log_file)
network_log.addHandler(console)

# --------------------------------- XBee Log --------------------------------- #
log_xbee = logging.getLogger('log_xbee')

if settings.DEBUG:
    log_xbee.setLevel(logging.DEBUG)

try:
    xbee_log_file = logging.FileHandler('/opt/OpenPod/logs/xbee.log', mode='a')
except FileNotFoundError:
    xbee_log_file = logging.FileHandler('tests/xbee.log', mode='a')  # CI Testing

xbee_log_file.setFormatter(standard_format)
log_xbee.addHandler(xbee_log_file)
log_xbee.addHandler(console)

# --------------------------------- MQTT Log --------------------------------- #
mqtt_log = logging.getLogger('mqtt_log')

if settings.DEBUG:
    mqtt_log.setLevel(logging.DEBUG)

try:
    mqtt_log_file = logging.FileHandler('/opt/OpenPod/logs/mqtt.log', mode='a')
except FileNotFoundError:
    mqtt_log_file = logging.FileHandler('tests/mqtt.log', mode='a')  # CI Testing

mqtt_log_file.setFormatter(standard_format)
mqtt_log.addHandler(mqtt_log_file)
mqtt_log.addHandler(console)


# Logging configurations, use logfile for critial events, use transaction as print alternative
# Console handler decides what information to also "print" based on logging level
logfile = logging.getLogger('standardlog')

try:
    fileHandler = logging.FileHandler('/opt/OpenPod/logs/RecursionLog.log', mode='a')
except FileNotFoundError:
    fileHandler = logging.FileHandler('tests/RecursionLog.log', mode='a')  # For CI

fileHandler.setFormatter(standard_format)

if settings.DEBUG:
    logfile.setLevel(logging.DEBUG)
else:
    logfile.setLevel(logging.INFO)

logfile.addHandler(fileHandler)
logfile.addHandler(console)
transaction = logging.getLogger('transaction')

try:
    fileH = logging.FileHandler('/opt/OpenPod/logs/TransactionLog.log', mode='a')
except FileNotFoundError:
    fileH = logging.FileHandler('tests/TransactionLog.log', mode='a')  # For CI

fileH.setFormatter(standard_format)
transaction.setLevel(logging.DEBUG)
transaction.addHandler(console)
transaction.addHandler(fileH)


def publog(level, note):
    '''
    Sets the log level.
    '''
    if level == "error":
        logfile.error(note)

    if level == "info":
        logfile.info(note)

    if level == "warning":
        logfile.warning(note)

    if level == "debug":
        logfile.debug(note)


def transaction_log(level, note):
    '''
    Sets log level for the transaction_log.
    '''
    if level == "info":
        transaction.info(note)

    if level == "debug":
        transaction.debug(note)


# ------ Captures wide range of system settings for debugging purposes. ------ #
def snapshot(public_ip, local_ip):
    '''
    Create a JSON summary of system settings and status.
    '''
    system_data = {}

    with open('/opt/OpenPod/system.json', 'r', encoding="UTF-8") as system_file:
        system_json_file = json.load(system_file)

        system_data["system_json"] = system_json_file

        system_data["PI"] = f"{settings.IS_PI}"

        system_data['ip'] = {}

        system_data['ip']["local"] = local_ip

        system_data['ip']["public"] = public_ip

        if 'space' in system_json_file:
            system_data["DataHash"] = hash_data()

        system_data['pip'] = freeze.freeze()

    with open('/opt/OpenPod/logs/System.Snapshot', 'w', encoding="UTF-8") as snapshot_file:
        snapshot_file.seek(0)
        json.dump(system_data, snapshot_file, iterable_as_array=True)
        snapshot_file.truncate()

    dump_diagnostics()

# ---------------------------------------------------------------------------- #
#                               Send Diagnostics                               #
# ---------------------------------------------------------------------------- #


def dump_diagnostics():
    '''
    Send the summary of setting to Recursion.Space
    '''
    with open('/opt/OpenPod/logs/System.Snapshot', 'r', encoding="UTF-8") as snapshot_file:
        if op_config.get('api_token', False):
            payload = json.load(snapshot_file)

            try:
                requests.put(f'https://{op_config.get("url")}/v1/diagnostics/',
                             json={"snapshot": payload},
                             headers={'Authorization': f"Token {op_config.get('api_token')}"},
                             timeout=10
                             )

            except requests.exceptions.RequestException as err:
                exception_log.error('Unable to submit diagnostics. Error: %s', err)

# --------------------------- Zip & Send Log Files --------------------------- #


def zip_send():
    '''
    Zip all log files together and send to Recursion.Space
    '''
    try:
        zip_file = f'/opt/OpenPod/logs/{op_config.get("serial")}_logs.zip'

        with ZipFile(zip_file, 'w') as zip_logs:
            zip_logs.write('/opt/OpenPod/logs/System.Snapshot', 'system_snapshot.txt')
            zip_logs.write('/opt/OpenPod/logs/network.log', 'network.log')
            zip_logs.write('/opt/OpenPod/logs/xbee.log', 'xbee.log')
            zip_logs.write('/opt/OpenPod/logs/mqtt.log', 'mqtt.log')
            zip_logs.write('/opt/OpenPod/logs/exception.log', 'exception.log')
            zip_logs.write('/opt/OpenPod/logs/RecursionLog.log', 'RecursionLog.log')
            zip_logs.write('/opt/OpenPod/logs/TransactionLog.log', 'TransactionLog.log')

            zip_logs.close()

        while not os.path.exists(zip_file):
            time.sleep(1)

        if os.path.isfile(zip_file):

            with open(zip_file, 'rb') as zip_file_logs:
                requests.post(
                    f'https://{op_config.get("url")}/files/upload/external/hublogs/',
                    files={"file": zip_file_logs},
                    headers={'Authorization': f'Token {op_config.get("api_token")}'},
                    timeout=10
                )

        else:
            raise ValueError(f"{zip_file} isn't a file!")

    except ValueError as err:
        exception_log.error("zip_send ValueError: %s", err)

    except TypeError as err:
        exception_log.error("zip_send TypeError: %s", err)


# ---------------------------------------------------------------------------- #
#                               Hash Stored Data                               #
# ---------------------------------------------------------------------------- #
def hash_data():
    '''
    Produce a hash of the available data to compare with the data on Recursion.Space
    '''
    try:
        with open("/opt/OpenPod/data/dump.json", "rb") as dump_file:
            dump_hash = hashlib.md5(
                dump_file.read()
            ).hexdigest()

        with open("/opt/OpenPod/data/nodes.json", "rb") as nodes_file:
            nodes_hash = hashlib.md5(
                nodes_file.read()
            ).hexdigest()

        with open("/opt/OpenPod/data/owners.json", "rb") as owners_file:
            owners_hash = hashlib.md5(
                owners_file.read()
            ).hexdigest()

        with open("/opt/OpenPod/data/permissions.json", "rb") as perm_file:
            permissions_hash = hashlib.md5(
                perm_file.read()
            ).hexdigest()

        combined_hash = hashlib.md5(
            f"{dump_hash}, {nodes_hash}, {owners_hash}, {permissions_hash}".encode())

        return {
            'combined': combined_hash.hexdigest(),
            'dumpHash': dump_hash,
            'nodesHash': nodes_hash,
            'ownersHash': owners_hash,
            'permissionsHash': permissions_hash
        }

    except FileNotFoundError as err:
        exception_log.error("Unable to hash dta with error: %s", err)
        return err
