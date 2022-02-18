#!/usr/bin/env python3

'''This file is ran when setting up a new Pi.'''
#Program execution is handled by the HUB_Launcher.py within the latest version folder.

#need to setup for local time
#https://linuxize.com/post/how-to-set-or-change-timezone-on-ubuntu-18-04/

import uuid
import json
import subprocess

from os import path


instalation_log = {}


# --------------------------- Set System Time Zone --------------------------- #
try:
    subprocess.call(['sudo', 'timedatectl', 'set-timezone', 'UTC'])

    instalation_log['SysTimeZone'] = 'SUCESS - System time zone changed to UTC'
except RuntimeError as err:
    instalation_log['SysTimeZone'] = f'FAILED - {err}'


# ---------------------------- Update system time ---------------------------- #
try:
    subprocess.call(['sudo', 'apt-get', 'install', 'chrony', '-y'])
    subprocess.call(['sudo', 'chronyd', '-q'])

    instalation_log['SysTime'] = 'SUCESS - System time synchronized.'
except RuntimeError as err:
    instalation_log['SysTime'] = f'FAILED - {err}'


# --------------------- Update OS and Package Directories -------------------- #
try:
    subprocess.call(['sudo', 'apt-get', 'update', '-y'])

    instalation_log['SysUpdate'] = 'SUCESS - Sytem has now been updated.'
except RuntimeError as err:
    instalation_log['SysUpdate'] = f'FAILED - {err}'


try:
    subprocess.call(['sudo', 'apt-get', 'upgrade', '-y'])

    instalation_log['SysUpgrade'] = 'SUCESS - Sytem has now been upgrded.'
except RuntimeError as err:
    instalation_log['SysUpgrade'] = f'FAILED - {err}'


# -------------------------------- Install PIP ------------------------------- #
try:
    subprocess.call(['sudo', 'apt-get', 'install', 'python3-pip', '-y'])

    instalation_log['GetPip'] = 'SUCESS - pip now installed.'
except RuntimeError as err:
    instalation_log['GetPip'] = f'FAILED - {err}'


# ------------- Creates execution location at /opt/OpenPod/ ------------- #
try:
    subprocess.call(['mkdir', '/opt/OpenPod'])

    instalation_log['MakeDirectory'] = 'SUCESS - OpenPod directory created.'
except RuntimeError as err:
    instalation_log['MakeDirectory'] = f'FAILED - {err}'


# ----------------------- Creates the system.json file ----------------------- #
try:
    subprocess.call(['sudo', 'touch', '/opt/OpenPod/system.json'])

    data = {
        "serial"    :    f"{uuid.uuid4().hex}",    #Self assigned aidentification number.
        "timezone"    :    "UTC",
        "XBEE_KY"    :    f"{uuid.uuid4().hex}",    #Network key be assigned to the nodes.
        "XBEE_OP"    :    False,                            #False -> XBee not configured.
        "CurrentVersion"    :    "0_1_0",                    #Program fallback.
        }

    with open('/opt/OpenPod/system.json', 'w', encoding="utf-8") as outfile:
        json.dump(data, outfile)

    instalation_log['system.json'] = 'SUCESS - Suscessfulyl created system json file.'
except RuntimeError as err:
    instalation_log['system.json'] = f'FAILED - {err}'


# ---------------------------------------------------------------------------- #
#                           Install Bash Requirements                          #
# ---------------------------------------------------------------------------- #

# ------- jq - parse json bash https://stedolan.github.io/jq/download/ ------- #
try:
    subprocess.call(['sudo', 'apt-get', 'install', 'jq', '-y'])

    instalation_log['BashReq_jq'] = 'SUCESS - jq now installed.'
except RuntimeError as err:
    instalation_log['BashReq_jq'] = f'FAILED - {err}'


# -------------------- unzip to manage zipfiles from bash -------------------- #
try:
    subprocess.call(['sudo', 'apt-get', 'install', 'unzip', '-y'])

    instalation_log['BashReq_unzip'] = 'SUCESS - unzip now installed.'
except RuntimeError as err:
    instalation_log['BashReq_unzip'] = f'FAILED - {err}'


# ----------------- ifconfig to check network adapter status ----------------- #
#Depreciated use https://askubuntu.com/questions/1031640/ifconfig-missing-after-ubuntu-18-04-install
try:
    subprocess.call(['sudo', 'apt-get', 'install', 'net-tools', '-y'])

    instalation_log['Install_net-tools'] = 'SUCESS - Installed net-tools.'
except RuntimeError as err:
    instalation_log['pip_requiremetns'] = f'FAILED - Could not install net-tools.{err}'


# ------------------ pip requiremetns from requirements.txt ------------------ #
try:
    subprocess.call([
        'sudo',
        'pip3',
        'install',
        '--no-input',
        '-U',
        '-r',
        'requirements.txt',
        '--no-cache-dir',
        '--no-dependencies'
        ])

    instalation_log['pip_requiremetns'] = 'SUCESS - Installed all pip requirements.'
except RuntimeError as err:
    instalation_log['pip_requiremetns'] = f'FAILED - {err}'


# ---------------------- Create Folders and Directories ---------------------- #
try:
    subprocess.call(['mkdir', '/opt/OpenPod/logs'])
    subprocess.call(['mkdir', '/opt/OpenPod/data'])
    subprocess.call(['touch', '/opt/OpenPod/logs/RecursionLog.log'])
    subprocess.call(['touch', '/opt/OpenPod/logs/System.Snapshot'])

    instalation_log['folders_directories'] = 'SUCESS - Log folder and files prepared'
except RuntimeError as err:
    instalation_log['folders_directories'] = f'FAILED - {err}'


# ------------------------- Create Data Storage Files ------------------------ #
try:
    if path.exists("/opt/OpenPod/data/dump.json") is False:
        subprocess.call(['sudo', 'touch', '/opt/OpenPod/data/dump.json'])
    if path.exists("/opt/OpenPod/data/nodes.json") is False:
        subprocess.call(['sudo', 'touch', '/opt/OpenPod/data/nodes.json'])
    if path.exists("/opt/OpenPod/data/owners.json") is False:
        subprocess.call(['sudo', 'touch', '/opt/OpenPod/data/owners.json'])
    if path.exists("/opt/OpenPod/data/permissions.json") is False:
        subprocess.call(['sudo', 'touch', '/opt/OpenPod/data/permissions.json'])

    instalation_log['storage_files'] = 'SUCESS - Suscessfulyl created data files.'
except RuntimeError as err:
    instalation_log['storage_files'] = f'FAILED - {err}'


# ------------------ Move boot.sh to /opt/OpenPod/ ------------------ #
try:
    subprocess.call(['sudo', 'cp', 'boot.sh', '/opt/OpenPod/HUB_Boot.sh'])

    instalation_log['move_boot.sh'] = 'SUCESS - boot.sh file is not in the /opt/ directory.'
except RuntimeError as err:
    instalation_log['move_boot.sh'] = f'FAILED - {err}'


# ----------------------------- Copy 0_1_0 Folder ---------------------------- #
try:
    subprocess.call(['sudo', 'cp', '-r', '0_1_0', '/opt/OpenPod/0_1_0'])

    instalation_log['copy0_1_0'] = 'SUCESS - 0_1_0/ copied into the /opt/ directory.'
except RuntimeError as err:
    instalation_log['copy0_1_0'] = f'FAILED - {err}'


# --------------------------- Set file permissions --------------------------- #
try:
    subprocess.call(['sudo', 'chmod', '+x', '/opt/OpenPod/HUB_Boot.sh'])

    instalation_log['chmod'] = 'SUCESS - Permissions for HUB_Boot.sh updated.'
except RuntimeError as err:
    instalation_log['chmod'] = f'FAILED - {err}'


# ----------------------------- Configure crontab ---------------------------- #
try:
    from crontab import CronTab # Needs to be here since it is installed by the requirements file.
    cron = CronTab(user='root')
    job = cron.new(command='(cd /opt/OpenPod && sudo ./HUB_Boot.sh &)')
    job.every_reboot()
    cron.write()

    instalation_log['configure_python-crontab'] = 'SUCCESS - Crontab sucessfully created.'
except ImportError as err:
    instalation_log['configure_python-crontab'] = f'FAILED - {err}'
except RuntimeError as err:
    instalation_log['configure_python-crontab'] = f'FAILED - {err}'

for log_item, result in instalation_log.items():
    print(f"{log_item} -> {result}")
print("Recursion HUB Installation Program Complete. Restart System.")
