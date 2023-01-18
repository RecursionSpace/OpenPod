'''
openpod | modules | op_ssh.py
Configuration for SSH
'''

import os
import requests

from modules import op_config
from modules.rec_log import log_api


def update_keys():
    '''
    Requests the keys from the server and updates the local keys.
    Request URL: /v1/pod/ssh_pub_keys
    '''
    try:
        keys = requests.get(
            f'https://{op_config.get("api_url")}/v1/pod/ssh_pub_keys/{op_config.get("uuid")}',
            headers={'Authorization': f'Token {op_config.get("api_token")}'},
            timeout=10
        )
    except requests.exceptions.RequestException as error:
        log_api.error('SSH Keys Update Failed: %s', error)
        return False

    key_file_path = os.path.expanduser('~openpod/.ssh/authorized_keys')
    with open(key_file_path, 'w', encoding="UTF-8") as key_file:
        for key in keys.json():
            key_file.write(key['key'])

    log_api.info('SSH Keys Updated')
    return True
