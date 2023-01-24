#!/usr/bin/env python3

'''
Handles API calls with Recursion.Space
Performs all API calls to the server, functions should be used as a thread.
'''

import json
import threading
import requests

from modules import op_config, op_gpio
from modules.rec_log import log_api, hash_data


# ---------------------------------------------------------------------------- #
#                      Request Update For All Information                      #
# ---------------------------------------------------------------------------- #
def pull_data_dump():
    '''
    Request updated information from the server.
    '''
    # ----------------------------- Pull Member Data ----------------------------- #
    with open("/opt/OpenPod/data/dump.json", "w", encoding="utf-8") as file:
        member_info = requests.get(f'https://{op_config.get("api_url")}/v1/members', headers={
            'Authorization': f'Token {op_config.get("api_token")}'
        }, timeout=10)

        response = member_info.json()
        json.dump(response, file)

    # --------------------------- Pull Operator(s) Data -------------------------- #
    with open("/opt/OpenPod/data/owners.json", "w", encoding="utf-8") as file:
        operators_info = requests.get(f'https://{op_config.get("api_url")}/v1/operators', headers={
            'Authorization': f'Token {op_config.get("api_token")}'
        }, timeout=10)

        response = operators_info.json()
        json.dump(response, file)

    # -------------------------------- Nodes Data -------------------------------- #
    with open("/opt/OpenPod/data/nodes.json", "w", encoding="utf-8") as file:
        nodes_info = requests.get(
            f'https://{op_config.get("api_url")}/v1/nodes',
            headers={'Authorization': f'Token {op_config.get("api_token")}'},
            timeout=10
        )

        response = nodes_info.json()
        json.dump(response, file)

    # ----------------------------- Pull Permissions ----------------------------- #
    with open("/opt/OpenPod/data/permissions.json", "w", encoding="utf-8") as file:
        permissions_info = requests.get(
            f'https://{op_config.get("api_url")}/v1/permissions',
            headers={'Authorization': f'Token {op_config.get("api_token")}'},
            timeout=10
        )

        response = permissions_info.json()
        json.dump(response, file)

    return True


# ---------------------------------------------------------------------------- #
#                            Set or Update Timezone                            #
# ---------------------------------------------------------------------------- #
def update_time_zone():
    '''
    API call to set the HUB timezone with the user selected option.
    '''
    spaces_info = requests.get(
        f'https://{op_config.get("api_url")}/v1/spaces',
        headers={'Authorization': f'Token {op_config.get("api_token")}'},
        timeout=10
    )

    response = spaces_info.json()[0]

    op_config.set_value("timezone", response["timezone"])
    log_api.info("Facility time zone set to: %s", response["timezone"])


# ---------------------------------------------------------------------------- #
#                          Register Hub With Recursion                         #
# ---------------------------------------------------------------------------- #
def register_pod():  # Needs updated!
    '''
    API to register the pod.
    '''
    url = f'https://{op_config.get("url")}/hubs/'
    payload_tuples = {
        'uuid': f"{op_config.get('uuid')}",
        'serial': f"{op_config.get('serial')}"
    }
    output = requests.post(url, payload_tuples, auth=('OwnerA', 'Password@1'), timeout=10)
    response = output.json()

    log_api.info(f"Pod registration response: {response}")

    op_config.set_value("pod_id", response["id"])
    log_api.info(f'Pod registered and assigned pod_id: {response["id"]}')


# ---------------------------------------------------------------------------- #
#                         Pairs The Hub With A Facility                        #
# ---------------------------------------------------------------------------- #
def link_hub():
    '''
    Associate the Pod with a space.
    '''
    try:
        hubs_info = requests.get(
            f'https://{op_config.get("api_url")}/v1/hubs',
            headers={'Authorization': f'Token {op_config.get("api_token")}'},
            timeout=10
        )

        response = hubs_info.json()

        op_config.set_value("space", response[0]["facility"])

        op_gpio.ready()

    except OSError as err:
        log_api.error("link_hub - Unable to open file system.json - %s", err)


# ---------------------------------------------------------------------------- #
#                       Registers New Node With Recursion                      #
# ---------------------------------------------------------------------------- #
def pair_node(node_mac):
    '''
    Link a new node with the hub.
    '''
    post_content = [
        ('mac', node_mac),
        ('hub', op_config.get('pod_id')),
        ('facility', op_config.get("space"))
    ]

    # ------------------------------ API /v1/nodes/ ------------------------------ #
    requests.post(
        f'https://{op_config.get("api_url")}/v1/nodes',
        data=post_content,
        headers={'Authorization': f'Token {op_config.get("api_token")}'}, timeout=10
    )

    pull_data_dump()


# ---------------------------------------------------------------------------- #
#                        Keepalive With recursion.space                        #
# ---------------------------------------------------------------------------- #
def keepalive():
    '''
    Pings Recursion.Space as an indicator that the hub is still active.
    '''
    try:
        if op_config.get("space", False):
            requests.get(
                f'''https://{op_config.get("url")}/hub/keepalive/'''
                f'''{op_config.get("serial")}/'''
                f'''{op_config.get("version")}/'''
                f'''{hash_data()["combined"]}/''',
                headers={'Authorization': f'Token {op_config.get("api_token")}'},
                timeout=10
            )

        else:
            requests.get(
                f'''https://{op_config.get("url")}/hub/keepalive/'''
                f'''{op_config.get("serial")}/'''
                f'''{op_config.get("version")}/''',
                headers={'Authorization': f'Token {op_config.get("api_token")}'},
                timeout=10
            )

    except requests.exceptions.RequestException as err:
        log_api.warning("Keepalive ConnectionError: %s", err)

    except OSError as err:
        log_api.error("Keepalive OSError: %s", err)

    finally:
        log_api.debug('Heartbeat check again in 30 seconds from now.')  # DEBUG POINT
        heartbeat_thread = threading.Timer(30.0, keepalive)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()


# ---------------------------------------------------------------------------- #
#                             Logging To Recursion                             #
# ---------------------------------------------------------------------------- #
def access_log(card_number, action, result, node, facility):
    '''
    Access request logging to Recursion.Space
    '''
    try:
        payload = [
            ('cardNumber', card_number),
            ('action', action),
            ("result", result),
            ("node", node),
            ("facility", facility)
        ]

        requests.post(
            f'https://{op_config.get("url")}/accesslog/',
            data=payload,
            headers={'Authorization': f'Token {op_config.get("api_token")}'},
            timeout=10
        )

    except RuntimeError as err:
        log_api.error("Unable to contact Recursion Server. Error: %s", err)

    except OSError as err:
        log_api.error("access_log = Unable to access file system.json - %s", err)
