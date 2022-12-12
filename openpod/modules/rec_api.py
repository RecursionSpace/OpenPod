#!/usr/bin/env python3

'''
Handles API calls with Recursion.Space
'''

import json
import threading
import requests

import settings

from modules.rec_log import log_api, hash_data

if settings.IS_PI:
    from modules import rec_gpio
    from settings import LED_IO

# Performs all API calls to the server, functions should be used as a thread.

# ---------------------------------------------------------------------------- #
#                      Request Update For All Information                      #
# ---------------------------------------------------------------------------- #


def pull_data_dump():
    '''
    Request updated infromation from the server.
    '''
    with open('system.json', 'r+', encoding="utf-8") as file:
        system_data = json.load(file)

    # ----------------------------- Pull Member Data ----------------------------- #
    with open("/opt/RecursionHub/data/dump.json", "w", encoding="utf-8") as file:
        member_info = requests.get(f'{settings.RECURSION_API_URL}/v1/members', headers={
            'Authorization': f'Token {system_data["Token"]}'
        }, timeout=10)

        responce = member_info.json()
        json.dump(responce, file)

    # --------------------------- Pull Operator(s) Data -------------------------- #
    with open("/opt/RecursionHub/data/owners.json", "w", encoding="utf-8") as file:
        operators_info = requests.get(f'{settings.RECURSION_API_URL}/v1/operators', headers={
            'Authorization': f'Token {system_data["Token"]}'
        }, timeout=10)

        responce = operators_info.json()
        json.dump(responce, file)

    # -------------------------------- Nodes Data -------------------------------- #
    with open("/opt/RecursionHub/data/nodes.json", "w", encoding="utf-8") as file:
        nodes_info = requests.get(
            f'{settings.RECURSION_API_URL}/v1/nodes',
            headers={'Authorization': f'Token {system_data["Token"]}'},
            timeout=10
        )

        responce = nodes_info.json()
        json.dump(responce, file)

    # ----------------------------- Pull Permissions ----------------------------- #
    with open("/opt/RecursionHub/data/permissions.json", "w", encoding="utf-8") as file:
        permissions_info = requests.get(
            f'{settings.RECURSION_API_URL}/v1/permissions',
            headers={'Authorization': f'Token {system_data["Token"]}'},
            timeout=10
        )

        responce = permissions_info.json()
        json.dump(responce, file)

    return True

# ---------------------------------------------------------------------------- #
#                            Set or Update Timezone                            #
# ---------------------------------------------------------------------------- #


def update_time_zone():
    '''
    API call to set the HUB timezone with the user selected option.
    '''
    with open("system.json", "r+", encoding="utf-8") as file:
        system_data = json.load(file)
        spaces_info = requests.get(
            f'{settings.RECURSION_API_URL}/v1/spaces',
            headers={'Authorization': f'Token {system_data["Token"]}'},
            timeout=10
        )

        responce = spaces_info.json()

        system_data.update({"timezone": responce[0]["timezone"]})
        file.seek(0)
        json.dump(system_data, file)
        file.truncate()

        log_api.info("Facility time zone set to: %s", responce[0]["timezone"])


# ---------------------------------------------------------------------------- #
#                          Register Hub With Recursion                         #
# ---------------------------------------------------------------------------- #
def register_hub():  # Needs updated!
    '''
    API to register the hub.
    '''
    with open('system.json', 'r', encoding="utf-8") as system_file:
        system_config = json.load(system_file)

    url = settings.RecursionURL+'/hubs/'
    payload_tuples = {'serial': f"{system_config['serial']}"}
    output = requests.post(url, payload_tuples, auth=('OwnerA', 'Password@1'), timeout=10)
    responce = output.json()

    log_api.info("Hub registration responce: %s", responce)

    with open("/opt/RecursionHub/system.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        data.update({"HUBid": responce["id"]})
        file.seek(0)
        json.dump(data, file)
        log_api.info("Hub registered and assigned HUBid: %s", responce["id"])


# ---------------------------------------------------------------------------- #
#                         Pairs The Hub With A Facility                        #
# ---------------------------------------------------------------------------- #
def link_hub():
    '''
    Assosiate the hub with a space.
    '''
    try:
        with open("system.json", "r+", encoding="utf-8") as file:
            system_data = json.load(file)

            hubs_info = requests.get(f'{settings.RECURSION_API_URL}/v1/hubs', headers={
                'Authorization': f'Token {system_data["Token"]}'
            }, timeout=10)

            responce = hubs_info.json()

            system_data.update({"facility": responce[0]["facility"]})
            file.seek(0)
            json.dump(system_data, file)
            file.truncate()

            if settings.IS_PI:
                rec_gpio.state(LED_IO, 1)
    except OSError as err:
        log_api.error("link_hub - Unable to open file system.json - %s", err)


# ---------------------------------------------------------------------------- #
#                       Registers New Node With Recursion                      #
# ---------------------------------------------------------------------------- #
def pair_node(node_mac):
    '''
    Link a new node with the hub.
    '''
    with open('system.json', 'r+', encoding="utf-8") as system_file:
        system_config = json.load(system_file)

    post_content = [
        ('mac', node_mac),
        ('hub', system_config['HUBid']),
        ('facility', system_config['facility'])
    ]

    # ------------------------------ API /v1/nodes/ ------------------------------ #
    requests.post(
        f'{settings.RECURSION_API_URL}/v1/nodes',
        data=post_content,
        headers={'Authorization': f'Token {system_config["Token"]}'}, timeout=10
    )

    pull_data_dump()


# ---------------------------------------------------------------------------- #
#                        Keepalive With recursion.space                        #
# ---------------------------------------------------------------------------- #
def keepalive():
    '''
    Pings Recursion.Space as an indicator that the hub is wtill active.
    '''
    try:
        with open('system.json', 'r', encoding="utf-8") as system_file:
            system_data = json.load(system_file)

        if 'facility' in system_data:
            requests.get(
                f'''{settings.RecursionURL}/hub/keepalive/'''
                f'''{system_data["serial"]}/'''
                f'''{system_data["CurrentVersion"]}/'''
                f'''{hash_data()["combined"]}/''',
                headers={'Authorization': f'Token {system_data["Token"]}'},
                timeout=10
            )

        else:
            requests.get(
                f'''{settings.RecursionURL}/hub/keepalive/'''
                f'''{system_data["serial"]}/'''
                f'''{system_data["CurrentVersion"]}/''',
                headers={'Authorization': f'Token {system_data["Token"]}'},
                timeout=10
            )

    except requests.exceptions.RequestException as err:
        log_api.warning("Keepalive ConnectionError: %s", err)

    except OSError as err:
        log_api.error("Keepalive OSError: %s", err)

    finally:

        try:
            log_api.debug('Keepalive check again in 30 seconds from now.')  # DEBUG POINT
            threading.Timer(30.0, keepalive).start()

        except RuntimeError as err:
            log_api.error("Keepalive thread RuntimeError: %s", err)


# ---------------------------------------------------------------------------- #
#                             Logging To Recursion                             #
# ---------------------------------------------------------------------------- #
def access_log(card_number, action, result, node, facility):
    '''
    Access request logging to Recursion.Space
    '''
    try:
        with open('system.json', 'r+', encoding="utf-8") as system_file:
            system_config = json.load(system_file)

        payload = [
            ('cardNumber', card_number),
            ('action', action),
            ("result", result),
            ("node", node),
            ("facility", facility)
        ]

        requests.post(
            f'{settings.RecursionURL}/accesslog/',
            data=payload,
            headers={'Authorization': f'Token {system_config["Token"]}'},
            timeout=10
        )

    except RuntimeError as err:
        log_api.error("Unable to contact Recursion Server. Error: %s", err)

    except OSError as err:
        log_api.error("access_log = Unable to access file system.json - %s", err)
