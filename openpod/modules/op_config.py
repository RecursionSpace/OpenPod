''' Configuration loader for OpenPod '''

import json

SYSTEM_FILE = '/opt/OpenPod/system.json'


def get(key, default=None):
    '''
    Get a value from the system configuration file.
    '''
    try:
        with open(SYSTEM_FILE, 'r', encoding="UTF-8") as system_file:
            system = json.load(system_file)
    except FileNotFoundError:
        system = {}

    return system.get(key, default)
