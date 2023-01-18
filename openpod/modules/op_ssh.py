'''
openpod | modules | op_ssh.py
Configuration for SSH
'''

import requests

from modules import op_config
from modules.rec_log import log_api


def update_keys():
    '''
    Requests the keys from the server and updates the local keys.
    Request URL: /v1/pod/ssh_pub_keys
    '''
    keys = requests.get(
        f'https://{op_config.get("api_url")}/v1/pod/ssh_pub_keys/{op_config.get("uuid")}',
        headers={'Authorization': f'{op_config.get("api_token")}'},
        timeout=10
    )

    with open('~openpod/.ssh/authorized_keys', 'w', encoding="UTF-8") as key_file:
        for key in keys.json():
            key_file.write(key['key'])

    log_api.info('SSH Keys Updated')
