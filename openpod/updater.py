#!/usr/bin/env python3
"""
Recursion.Space
hub_updater.py

Call the function 'update_hub' to pull the latest update.
"""

# Triggered by the user from the web interface to update the current version.

import re
import sys
import json
import zipfile
import subprocess

import urllib.request
import requests

import settings

from modules.rec_log import exception_log


def current_hub_version():
    '''
    Reades the curent version number from the system file.
    '''
    with open('system.json', 'r', encoding="utf-8") as system_file:
        system_data = json.load(system_file)

    return system_data['CurrentVersion']


def update_version_name():
    '''
    Fetches the new version number available from the server.
    '''
    with open('system.json', 'r', encoding="utf-8") as system_file:
        system_data = json.load(system_file)

    request_response = requests.get(
        f'{settings.RecursionURL}/updatehub/',
        headers={'Authorization': f"Token {system_data['Token']}"},
        timeout=10
    )
    response_data = request_response.headers['content-disposition']
    return re.findall("filename=(.+)", response_data)[0]


def download_update():
    '''
    This will request the file and download it.
    - Fiest gets the name of the file for the update.

    https://stackoverflow.com/questions/45247983/urllib-urlretrieve-with-custom-header
    '''
    with open('system.json', 'r+', encoding="utf-8") as system_file:
        system_data = json.load(system_file)

    fname = update_version_name()
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', f"Token {system_data['Token']}")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(f'{settings.RecursionURL}/updatehub/', fname)

    # exception_log.info("Update version pulled: %s", re.findall(r"(.+?)(\.[^.]*$|$)", fname)[0][0])
    return re.findall(r"(.+?)(\.[^.]*$|$)", fname)[0][0]


def unzip_update():
    '''
    Extracts the contents of the zip file.
    Removed the .zip file.
    '''
    new_version = download_update()

    with zipfile.ZipFile(f'{new_version}.zip', 'r') as zip_ref:
        zip_ref.extractall(f'{new_version}/')

    subprocess.call(['rm', f'{new_version}.zip'])  # Cleaning up downloaded file.

    return new_version


def update_hub():
    '''
    Main code called to update the hub.
    '''
    try:
        exception_log.info("Update Started")
        new_version = unzip_update()

    except RuntimeError as err:
        exception_log.error("Unable to pull update with error: %s", err)
        new_version = current_hub_version()  # If unable to update, just run the current version.

    finally:
        with open("system.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            data.update({"CurrentVersion": new_version})
            file.seek(0)
            json.dump(data, file)
            file.truncate()

    # Relaunch with new program if update was sucessful.
    try:
        # Kill process that should be triggered to re-open by bash script.
        subprocess.call(['pkill', '-f', 'hub.py'])
        subprocess.call(['pkill', '-f', 'HUB_Launcher.py'])
    except RuntimeError as err:
        exception_log.error("Could not kill program, trying to launch new version. Error: %s", err)

        launch_location = f'/opt/RecursionHub/{new_version}/HUB_Launcher.py'
        with subprocess.Popen(['nohup', 'python3', '-u', f'{launch_location}', '&'])as script:
            print(script)

    finally:
        sys.exit()
