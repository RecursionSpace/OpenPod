#!/usr/bin/env python3
"""
Recursion System - rec_lookup
"""
import json
import threading

from datetime import date, datetime, timedelta
from pytimeparse.timeparse import timeparse

import pytz

from modules import rec_api

from modules.rec_log import exception_log

# --------------------------- Count Matching Nodes --------------------------- #


def count_matching_mac(rx_source):
    '''
    Checks to see if the mac address being paired has been seen before by the system.
    rx_source - MAC address of the node.

    returns - The number of nodes that match the MAC address.
    '''
    if len(rx_source) != 16:
        return 0

    match_counter = 0
    try:
        with open("/opt/OpenPod/data/nodes.json", "r", encoding="utf-8") as node_file:
            for data in json.load(node_file):
                if data['mac'] == rx_source:
                    match_counter += 1

    except json.decoder.JSONDecodeError as err:
        exception_log.error("JSON decode issue: %s", err)

    except TypeError as err:
        exception_log.error("Unable to read file with error: %s", err)

    except IOError as err:
        exception_log.error("nodes.json file not found: %s", err)

    return match_counter

# ---------------------------------------------------------------------------- #
#                            Convert MAC to Node ID                            #
# ---------------------------------------------------------------------------- #


def mac_to_id(mac_address):
    '''
    Returns the id for the node that belongs to the mac address.
    '''
    with open('/opt/OpenPod/data/nodes.json', 'r', encoding="utf-8") as nodes_file:
        nodes_dump = json.load(nodes_file)

    for node in nodes_dump:
        if node['mac'] == mac_address:
            return node['id']

    # Defaults if the nodes has not been added yet.
    return mac_address


# ---------------------------------------------------------------------------- #
#                                Check If Owner                                #
# ---------------------------------------------------------------------------- #
def is_owner(lookup_id):
    '''
    Checks if the ID matches to an owner.
    Returns True or False
    '''
    with open("/opt/OpenPod/data/owners.json", "r", encoding="utf-8") as owner_file:
        owner_file = json.load(owner_file)

    for owner in owner_file:
        if owner["cardNumber"] == lookup_id:
            return True

    return False


# ---------------------------------------------------------------------------- #
#                              Obtain User Details                             #
# ---------------------------------------------------------------------------- #
def get_details(card_id):
    '''
    Checks if user exsists, if yes, returns details.
    '''
    with open("/opt/OpenPod/data/dump.json", "r", encoding="utf-8") as member_file:
        member_file = json.load(member_file)

    for user in member_file:
        if user["cardNumber"] == card_id:
            return {
                "found": True,
                "access_group": user['access_group'],
                "restricted_nodes": user['restricted_nodes'],
            }

    return {"found": False}


# ---------------------------------------------------------------------------- #
#                             Obtain Group Details                             #
# ---------------------------------------------------------------------------- #
def get_group_details(access_group_id):
    '''
    Returns the detils of group for a user.
    access_group_id is an integer
    '''
    with open("/opt/OpenPod/data/permissions.json", "r", encoding="utf-8") as permissions_file:
        permissions_file = json.load(permissions_file)

    for group in permissions_file:
        if group['id'] == access_group_id:
            return {
                "found": True,
                "allowedNodes": group['allowedNodes'],
                "twenty_four_seven": group.get('twenty_four_seven', False),
                "startTime": group['startTime'],
                "endTime": group['endTime'],
                "monday": group['monday'],
                "tuesday": group['tuesday'],
                "wednesday": group['wednesday'],
                "thursday": group['thursday'],
                "friday": group['friday'],
                "saturday": group['saturday'],
                "sunday": group['sunday'],
            }

    return {"found": False}


# ---------------------------------------------------------------------------- #
#                                Perform Search                                #
# ---------------------------------------------------------------------------- #
def access_request(requested_id, request_node):         # pylint: disable=R0911
    '''
    Processes access requests.
    request_id - User's ID that is making a request.
    request_node - The MAC for the node where the user is making the request.

    Return 1 - Request approved.
    Return 2 - Request denied.
    '''
    with open('system.json', 'r', encoding="utf-8") as system_file:
        system_info = json.load(system_file)

    reference_node = mac_to_id(request_node)

    if is_owner(requested_id):
        threading.Thread(
            target=rec_api.access_log,
            args=(
                requested_id, "Requested access",
                "Owner Allowed", reference_node, system_info['facility']
            )
        ).start()

        return 1

    day_number = date.today().weekday()
    now = datetime.now(pytz.timezone(system_info['timezone']))
    time_now = timedelta(0, 0, 0, 0, now.minute, now.hour)
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    # --------------------------- Access Determination --------------------------- #
    user = get_details(requested_id)

    if not user['found']:
        threading.Thread(
            target=rec_api.access_log,
            args=(
                requested_id, "Requested access",
                "User not found", reference_node, system_info['facility']
            )
        ).start()
        return 2

    # ----------------------------- Manually Disabled ---------------------------- #
    if reference_node in user["restricted_nodes"]:
        threading.Thread(
            target=rec_api.access_log,
            args=(
                requested_id, "Requested access",
                "Manually Restricted", reference_node, system_info['facility']
            )
        ).start()
        return 2

    group = get_group_details(user['access_group'])

    if not group['found']:
        threading.Thread(
            target=rec_api.access_log,
            args=(
                requested_id, "Requested access",
                "Group Not Found", reference_node, system_info['facility']
            )
        ).start()
        return 2

    # ---------------------------- Find User In Group ---------------------------- #
    if reference_node not in group["allowedNodes"]:
        # Node Not Allowed
        threading.Thread(
            target=rec_api.access_log,
            args=(
                requested_id, "Requested access",
                "No node permission", reference_node, system_info['facility']
            )
        ).start()
        return 2

    # 24/7 Override
    if group.get("twenty_four_seven", False):
        print("Group has 24/7 access.")
        threading.Thread(
            target=rec_api.access_log,
            args=(
                requested_id, "Requested access",
                "Allowed", reference_node, system_info['facility']
            )
        ).start()
        return 1

    # Day Of Week Permission
    if not group[days[day_number]]:
        # Day Not Allowed
        threading.Thread(
            target=rec_api.access_log,
            args=(
                requested_id, "Requested access",
                "Now Allowed Day", reference_node, system_info['facility']
            )
        ).start()
        return 2

    # Time Of Day Permission
    start = timedelta(0, timeparse(group["startTime"]))
    end = timedelta(0, timeparse(group["endTime"]))

    if start < time_now < end:
        # Allowed
        threading.Thread(
            target=rec_api.access_log,
            args=(
                requested_id, "Requested access",
                "Allowed", reference_node, system_info['facility']
            )
        ).start()
        return 1

    # Time Not Allowed
    threading.Thread(
        target=rec_api.access_log,
        args=(
            requested_id, "Requested access",
            "Not Allowed Time", reference_node, system_info['facility']
        )
    ).start()
    return 2
