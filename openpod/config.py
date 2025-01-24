""" Configuration Loader for OpenPod """

import os
import toml

CONFIG_FILE = os.environ.get("OPENPOD_CONFIG", "/opt/OpenPod/openpod.toml")

DEFAULT_CONFIG = {
    "uuid": "",
    "debug": False,
    "timezone": "UTC",
    "url": "https://recursion.space",
    "api_url": "https://api.recursion.space",
    "openpod": {
        "repo": "https://github.com/RecursionSpace/OpenPod",
        "branch": "release",
        "commit": "",
        "version": "",
    },
    "xbee": {
        "ky": "",
        "op": False,
    },
    "gpio": {
        "led_io": 23,
        "led_stat": 17,
    },
    "hardware": {
        "controller": "",
        "revision": "",
        "model": "",
        "serial": ""
    }
}


def merge_defaults(user_config: dict, default_config: dict) -> dict:
    """
    Merge the user configuration with the default configuration.
    """
    for key, default_value in default_config.items():
        if key not in user_config:
            user_config[key] = default_value
        else:
            # If both default and user are dicts, recursively merge
            if isinstance(default_value, dict) and isinstance(user_config[key], dict):
                merge_defaults(user_config[key], default_value)

    return user_config


def validate_config(config: dict) -> None:
    """
    Manually validate the presence and types of nested fields in config.
    Raises ValueError for invalid or missing fields.
    """
    if not isinstance(config.get("uuid"), str):
        raise ValueError("The 'uuid' section must be a string.")
    if not isinstance(config.get("debug"), bool):
        raise ValueError("The 'debug' section must be a boolean.")
    if not isinstance(config.get("timezone"), str):
        raise ValueError("The 'timezone' section must be a string.")
    if not isinstance(config.get("url"), str):
        raise ValueError("The 'url' section must be a string.")
    if not isinstance(config.get("api_url"), str):
        raise ValueError("The 'api_url' section must be a string.")

    openpod = config.get("openpod")
    if not isinstance(openpod, dict):
        raise ValueError("The 'openpod' section must be a dictionary.")
    if not isinstance(openpod.get("repo"), str):
        raise ValueError("The 'repo' section must be a string.")
    if not isinstance(openpod.get("branch"), str):
        raise ValueError("The 'branch' section must be a string.")
    if not isinstance(openpod.get("commit"), str):
        raise ValueError("The 'commit' section must be a string.")
    if not isinstance(openpod.get("version"), str):
        raise ValueError("The 'version' section must be a string.")

    xbee = config.get("xbee")
    if not isinstance(xbee, dict):
        raise ValueError("The 'xbee' section must be a dictionary.")
    if not isinstance(xbee.get("ky"), str):
        raise ValueError("The 'ky' section must be a string.")
    if not isinstance(xbee.get("op"), bool):
        raise ValueError("The 'op' section must be a boolean.")

    gpio = config.get("gpio")
    if not isinstance(gpio, dict):
        raise ValueError("The 'gpio' section must be a dictionary.")
    if not isinstance(gpio.get("led_io"), int):
        raise ValueError("The 'led_io' section must be an integer.")
    if not isinstance(gpio.get("led_stat"), int):
        raise ValueError("The 'led_stat' section must be an integer.")

    hardware = config.get("hardware")
    if not isinstance(hardware, dict):
        raise ValueError("The 'hardware' section must be a dictionary.")
    if not isinstance(hardware.get("controller"), str):
        raise ValueError("The 'controller' section must be a string.")
    if not isinstance(hardware.get("revision"), str):
        raise ValueError("The 'revision' section must be a string.")
    if not isinstance(hardware.get("model"), str):
        raise ValueError("The 'model' section must be a string.")
    if not isinstance(hardware.get("serial"), str):
        raise ValueError("The 'serial' section must be a string.")


def load_config() -> dict:
    """
    Load the OpenPod configuration file.
    """
    if not os.path.isfile(CONFIG_FILE):
        raise FileNotFoundError(f"Configuration file '{CONFIG_FILE}' not found.")

    with open(CONFIG_FILE, 'r', encoding='UTF-8') as config_file:
        config = toml.load(config_file)

    config = merge_defaults(config, DEFAULT_CONFIG)
    validate_config(config)

    return config
