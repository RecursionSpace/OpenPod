#!/usr/bin/env python3
'''
Recursion.Space - XBee Module
'''

import json
import binascii
import time
# import threading
from time import sleep
import serial
from pubsub import pub

import settings

from modules import rec_lookup, rec_api
from modules.rec_log import log_xbee

#Not sure if LED indicators are being used here.
# if settings.Pi:
#    from modules import rec_gpio

    #Serial information needed to detect and use XBee.
    # https://www.reddit.com/r/Python/comments/6jtzua/pyserial_minimum_time_for_timeout/
try:
    ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=.3)
except serial.serialutil.SerialException as serial_err:
    log_xbee.error('Could not establish serial connection: %s', serial_err)

# from settings import LED_IO, LED_STAT

def receive():
    '''
    Processes incoming xbee serial data.
    '''
    rx_data = ser.readline()                        #Read data that is currently waiting.
    sleep(.05)
    data_remaining = ser.inWaiting()                #Read any data that was not origionally read.
    rx_data += ser.read(data_remaining)             #Add any data that was left out in first pass.

    rx_data = binascii.b2a_hex(rx_data).strip().decode('utf-8')

    log_xbee.info('RX Raw: %s RX Data: %s', rx_data, rx_data[41:(len(rx_data)-2)])

    if rx_data == '7e00028a066f':
        log_xbee.info("The cordinator has started.")
        return (0, 0, 5)

    if rx_data[41:(len(rx_data)-2)].isdigit() is False and rx_data  != '7e00028a066f':
        rx_source = rx_data[8:24]
        log_xbee.info('Device %s is connecting to network', rx_source)
        # rx_data = rx_data[30:(len(rx_data)-2)]

        lookup_responce = rec_lookup.count_matching_mac(rx_source)
        #for Responce in MySQL_Responce:
        log_xbee.info('Returned %s matches for MAC addressed.', lookup_responce)
        if lookup_responce == 0:

            if len(rx_source) == 16:
                rec_api.pair_node(rx_source)
                log_xbee.info('%s Connected To XBee Network', rx_source)
                return (0,0,5)

            log_xbee.warning("%s is not a valid MAC length, not paired", rx_source)

        return (0,0,0) # (Placeholder) Need to set a return that an error has occured.

    if rx_data[42:(len(rx_data)-2)].isdigit() is True and rx_data  != '7e00028a066f':
        rx_source = rx_data[8:24]
        rx_data = rx_data[42:(len(rx_data)-2)]
        log_xbee.info('User %s requesting access from node %s', rx_data, rx_source)
        serial_lookup = rec_lookup.access_request(rx_data, rx_source)
        return rx_source,rx_data,serial_lookup

    return (0,0,0) # (Placeholder) Need to set a return that an error has occured.

def transmit(destination, data):
    '''
    Transmits outgoing serial xbee data.
    '''
    #global LED_STAT
    # BlinkThread = threading.Thread(target = rec_gpio.Blink, args = (LED_STAT, .075, 3))
    # BlinkThread.start()
    dest_16bit = 'FFFE'
    #data_hex = binascii.hexlify(data)
    data_hex  = data
    hex_len = hex(14 + (len(data_hex)//2))
    hex_len = hex_len.replace('x','00')
    checksum = 17
    for i in range(0,len(destination),2):
        checksum = checksum + int(destination[i:i+2],16)
    for i in range(0,len(dest_16bit),2):
        checksum = checksum + int(dest_16bit[i:i+2],16)
    for i in range(0,len(data_hex),2):
        checksum = checksum + int(data_hex[i:i+2],16)
    checksum = checksum%256
    checksum = 256 - checksum
    checksum = format(checksum, '02x')
    #checksum = hex(checksum)
    #checksum = checksum[-2:]
    tx_req = ("7E" + hex_len + "10" + "00" + destination
                + dest_16bit + "00" + "00" + data_hex + checksum)
    transmission = binascii.unhexlify(tx_req)
    log_xbee.info("Transmitting: %s", transmission)
    ser.write(transmission)

# ---------------------------------------------------------------------------- #
#                           New XBee Setup Procedure                           #
# ---------------------------------------------------------------------------- #
def configure_xbee():
    '''
    Configure Hub XBee modules for first time use.
    '''
    log_xbee.info("Configuring XBee for first time use")

    with open('system.json', 'r', encoding="UTF-8") as file:
        system_data = json.load(file)

        #Sequence of commands to configure a new XBee, sent in transparent mode.
        param_config = [
            b'ATCE1\r',                                         #Enable Cordinator
            b'ATAP1\r',                                         #Enable API Mode
            b'ATAO1\r',                                         #Set Output Mode To Explicit
            b'ATEE1\r',                                         #Enable Security
            b'ATEO2\r',                                         #Enable Trust Center
            f'ATKY{system_data["XBEE_KY"]}'.encode(),           #Set Encryption Key
            b'ATAC\r',                                          #Apply Queued Changes
            b'ATCN\r',                                          #Exit Command Mode
            ]

        ser.write(b'+++')                                       #Enter Command Mode
        sleep(1)
        print(ser.readline())
        for command in param_config:
            ser.write(command)
            rx_data = ser.read_until(expected='\r').decode()    #Reads buffer until carriage return.
            rx_data = str(rx_data.rstrip())
            log_xbee.info("Initial XBee Configuration TX: %s - RX: %s", command, rx_data)

        sleep(10)


def listing():
    '''Function to handling incoming serial info'''
    while True:
        if settings.Pi:
            if ser.in_waiting != 0:
                pub.sendMessage('xbee_rx')
        sleep(.01) #Allows CPU time for other threads.


# def mqtt_xbee(firstName, lastName, cardNumber, action, result, timestamp, space):
#     data = {}
#     data['firstName'] = firstName
#     data['lastName'] = lastName
#     data['cardNumber'] = cardNumber
#     data['action'] = action
#     data['result'] = result
#     data['timestamp'] = timestamp
#     data['space'] = space
#     json_data = json.dumps(data)

#     rec_mqtt.MQTTtx('log', json_data)

#     return

def xbee_info():
    '''
    Outputs information about the XBee module.
    '''
    log_xbee.info("rec_xbee.xbee_info called")

    sleep(1)                # No characters sent for 1 second (Guard Times)
    ser.write(b'+++')       # Enters AT Command Mode
    sleep(1)                # No characters sent for 1 second (Guard Times)

    ser.readline()          # Clear buffer

    ser.write(b'ATAP\r')    # Checks for API mode

    sleep(.1)
    rx_data = 1 # TEMP PATCH
    try:
        rx_data = ser.read_until(expected='\r').decode()        # Read buffer until carriage return
        rx_data = str(rx_data.rstrip())
    except TypeError as err:
        log_xbee.error("XBee ATAP command error info: %s", err)

    # If not in API mode, needs to configure the module.
    if rx_data != 1:
        configure_xbee()


    with open("system.json", "r+", encoding="UTF-8") as file:
        data = json.load(file)

        sleep(1)            # No characters sent for 1 second (Guard Times)
        ser.write(b'+++')   # Enters AT Command Mode
        sleep(1)            # No characters sent for 1 second (Guard Times)

        ser.readline()      # Clear buffer

        ser.write(b'ATOP\r')    # Read the operating 64-bit PAN ID.

        sleep(.1)
        try:
            rx_data = ser.read_until(expected='\r').decode()    # Read buffer until carriage return
            rx_data = str(rx_data.rstrip())
        except TypeError as err:
            log_xbee.error("XBee ATOP command error: %s", err)

        data.update( {"XBEE_OP":rx_data} )
        file.seek(0)
        json.dump(data, file)
        file.truncate()

        ser.write(b'ATCN\r')    # Exit Command Mode
        ser.readline()          # Clear buffer

    xbee_network_discovery()


def xbee_network_discovery():
    '''
    Issues a command to find what devices are currently connected to the hub.
    '''
    sleep(1)                # No characters sent for 1 second (Guard Times)
    ser.write(b'+++')       # Enters AT Command Mode
    sleep(1)                # No characters sent for 1 second (Guard Times)

    ser.readline()          # Clear buffer
    ser.write(b'ATND\r')    # Sends out a Node Discovery Request

    t_end = time.time() + 6
    while time.time() < t_end:
        try:
            sleep(.1)
            rx_data = ser.read_until(expected='\r').decode()    # Read buffer until carriage return
            rx_data = str(rx_data.rstrip())

            log_xbee.info('ND: %s', rx_data)
        except TypeError as err:
            log_xbee.error("Could not obtain xbee info: %s", err)

    ser.write(b'ATCN\r')    # Exit Command Mode
    ser.readline()          # Clear buffer
