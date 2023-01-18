#!/usr/bin/env python3
"""
Recursion.Space
updater.py

Call the function 'update_hub' to pull the latest update.
"""

# Triggered by the user from the web interface to update the current version.

import re
import os
import sys
import zipfile
import subprocess

import urllib.request
import requests

from modules import op_config
from modules.rec_log import exception_log


def update_pod():
    '''
    Steps through the update process.
    '''
    try:
        # Get the latest version file.
        request_response = requests.get(
            f"{op_config.get('api_url')}/updatehub/",
            headers={'Authorization': f"Token {op_config.get('api_token')}"},
            timeout=10
        )

        response_data = request_response.headers['content-disposition']
        latest_version_file = re.findall("filename=(.+)", response_data)[0]

        # Download the latest version file.
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', f"Token {op_config.get('api_token')}")]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(f"{op_config.get('api_url')}/updatehub/", latest_version_file)

        new_version = re.findall(r"(.+?)(\.[^.]*$|$)", latest_version_file)[0][0]

        with zipfile.ZipFile(f'{new_version}.zip', 'r') as zip_ref:
            zip_ref.extractall(f'{new_version}/')

        # Update the version number in the config file.
        op_config.set('version', new_version)

        # Remove the zip file.
        if os.path.exists(f'{new_version}.zip'):
            os.remove(f'{new_version}.zip')

    except RuntimeError as err:
        exception_log.error("Unable to pull update with error: %s", err)

    # Relaunch with new program if update was successful.
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
