#!/usr/bin/env python3
'''
OpenPod | updater.py

Grabs the latest version of OpenPod from GitHub and updates the current version.
'''

# Triggered by the user from the web interface to update the current version.

import os
import sys
import shutil
import zipfile

import urllib.request
import requests

from modules import op_config
from modules.rec_log import exception_log


def update_pod():
    '''
    Steps through the update process.
    1) Gets the latest version info from /pod/openpod/version/
    2) Downloads the latest version zip.
    3) Extracts the zip file.
    4) Copies the files to the root directory.
    5) Cleans up.
    '''

    try:
        latest_version = requests.get(
            f"https://{op_config.get('url')}/pod/openpod/version/",
            timeout=10
        )
        latest_version = latest_version.json()

        # Download the latest version zip.
        zip_url = f"{op_config.get('OpenPod').get('repo')}/archive/{latest_version['hash']}.zip"
        urllib.request.urlretrieve(zip_url, f"{latest_version['hash']}.zip")

        # Extract the zip file.
        with zipfile.ZipFile(f"{latest_version['hash']}.zip", 'r') as zip_ref:
            zip_ref.extractall()

        # Copy the files to the root directory.
        os.makedirs(f"/opt/OpenPod/versions/{latest_version['hash']}/", exist_ok=True)
        shutil.move(
            f"OpenPod-{latest_version['hash']}/OpenPod/",
            f"/opt/OpenPod/versions/{latest_version['hash']}/"
        )

    except RuntimeError as err:
        exception_log.error("Unable to pull update with error: %s", err)

    else:
        # Update the version number in the config file.
        op_config.set('version', latest_version['version'])
        op_config.set(['OpenPod', 'commit'], latest_version['hash'])

    finally:
        # Clean Up
        if os.path.exists(f"{latest_version['hash']}.zip"):
            os.remove(f"{latest_version['hash']}.zip")

        shutil.rmtree(f"OpenPod-{latest_version['hash']}/", ignore_errors=True)

        sys.exit()  # Force OpenPod to restart.
