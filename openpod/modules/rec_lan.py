#!/usr/bin/env python3
'''
Handles all network related activities for the hub.
DOES NOT PERFORM KEEPALIVE - SEE rec_api
'''

import socket
import threading
import requests

from modules import op_gpio, op_system
from modules.rec_log import network_log


# ------------ Triggers visual indicators based on network status. ----------- #
def monitor_network(last_network_status=5, thread_delay=30):
    '''
    Threaded: Yes
    Checks network connection, then updates visual indicators.
    Thread delay is extended to up 600 seconds if error occurs. Resets to 10 seconds on success.
    '''
    try:
        current_network_status = test_network()

        if current_network_status != last_network_status:
            network_status = current_network_status
        else:
            network_status = last_network_status

        if op_system.is_pi():
            if network_status == 0:
                op_gpio.no_network()

            if network_status == 1:
                op_gpio.no_internet()

            if network_status == 2:
                op_gpio.no_recursion()

            if network_status == 3:
                op_gpio.networked()

        thread_delay = 30  # Reset thread delay to 30 seconds.

    except UnboundLocalError as err:
        network_log.error('monitor_network error: %s', err)
        current_network_status = 0

    except Exception as err:
        network_log.error('Unable to perform network monitor: %s', err)
        current_network_status = 0

        if thread_delay <= 1200:
            thread_delay = thread_delay*2

        raise RuntimeError('Network monitoring thread has failed.') from err

    finally:
        network_log.debug('Thread timer set for %s second from now.', thread_delay)  # DEBUG POINT

        network_watch_thread = threading.Timer(
            thread_delay,
            monitor_network,
            [current_network_status, thread_delay]
        )
        network_watch_thread.name = 'network_watch_thread'
        network_watch_thread.start()

    return True


def test_network():
    '''
    Performs tired network tests.
    '''
    # No ethernet connection and reporting a 127.0.0.1 address.
    if networked() is False:
        return 0

    # Received a IP address that is not 127.0.0.1, but was unable to access the internet.
    if internet_on() is False:
        network_log.warning('LAN Check Fail')
        return 1

    # Internet connection is established but unable contact recursion Servers.
    if recursion_connection() is False:
        return 2

    # All checks passed and Recursion server is reachable
    # network_log.info('LAN Check Pass') # This would be called every 10 seconds
    return 3


def networked():
    '''
    Verifies that the Pi did not self assign ip.
    Returns: True or False
    True - Indicates a network connection
    False - No network connection
    '''
    local_ip = get_ip()[1]

    if local_ip == "127.0.0.1":
        return False

    return True


def internet_on():
    '''
    Performs requests to known external servers.
    '''
    try:
        if requests.get('https://recursion.space', timeout=10).status_code == requests.codes.ok:
            return True
    except requests.exceptions.RequestException:

        try:
            if requests.get('https://google.com', timeout=10).status_code == requests.codes.ok:
                return True
        except requests.exceptions.RequestException:

            try:
                if requests.get('https://amazon.com', timeout=10).status_code == requests.codes.ok:
                    return True
            except requests.exceptions.RequestException:

                return False

    return False


def recursion_connection():
    '''
    Checks if Recursion.Space is reachable.
    '''
    try:
        req = requests.get('https://recursion.space', timeout=10)
        if req.status_code == requests.codes.ok:
            return True

    except requests.exceptions.RequestException:
        return False

    return False


def get_ip():
    '''
    Obtains both the external and internal ip addresses.
    '''
    if internet_on() is True:
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=60).text

        except requests.exceptions.RequestException as err:
            public_ip = f'Failed to get public IP with error: {err}'
            network_log.error(public_ip)

    else:
        public_ip = "WLAN not available."

    try:
        hostname = socket.gethostname()

        ip_address = socket.gethostbyname_ex(hostname)[2]

        local_ip_address = [ip for ip in ip_address if not ip.startswith("127.")][:1]

        sock = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]

        socket_connections = [
            [
                (s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in sock
            ][0][1]
        ]

        local_ip = ([l for l in (local_ip_address, socket_connections) if l][0][0])

        # network_log.info("Hub's local IP address: {0}".format(local_ip))
        # Prevent constant log writing since now in loop

    except OSError as err:
        network_log.error('Unable to get local IP address with error: %s', err)
        local_ip = "127.0.0.1"

    return (public_ip, local_ip)
