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


def set_value(key, value):
    '''
    Set a value in the system configuration file.
    '''
    try:
        with open(SYSTEM_FILE, 'r', encoding="UTF-8") as system_file:
            system = json.load(system_file)
    except FileNotFoundError:
        system = {}

    system[key] = value

    with open(SYSTEM_FILE, 'w', encoding="UTF-8") as system_file:
        system_file.seek(0)
        json.dump(system, system_file, indent=4)
        system_file.truncate()
