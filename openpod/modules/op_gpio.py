#!/usr/bin/env python3

'''
Module manages raspberry pi gpio functionality.
'''

import json
from time import sleep

import config

try:
    from RPi import GPIO
    GPIO_AVAILABLE = True
except (RuntimeError, ModuleNotFoundError):
    GPIO_AVAILABLE = False

try:
    with open('/opt/OpenPod/system.json', 'r', encoding="UTF-8") as system_file:
        system = json.load(system_file)
    LED_IO = system['GPIO']['LED_IO']
    LED_STAT = system['GPIO']['LED_STAT']
except FileNotFoundError:
    LED_IO = 0
    LED_STAT = 0


if GPIO_AVAILABLE:
    GPIO.setmode(GPIO.BCM)  # Setup for LED indicators.
    GPIO.setwarnings(False)

    GPIO.setup(LED_IO, GPIO.OUT)
    GPIO.setup(LED_STAT, GPIO.OUT)

    GPIO.output(LED_IO, GPIO.LOW)
    GPIO.output(LED_STAT, GPIO.LOW)

config.LED_IO_ON = 0
config.LED_IO_OFF = 0

config.LED_STAT_ON = 0
config.LED_STAT_OFF = 0


# ---------------------------------------------------------------------------- #
#                               Indicator Presets                              #
# ---------------------------------------------------------------------------- #
def initializing():
    '''
    Indicates that the system is initializing.
    LED_IO - Solid on
    LED_STAT - Off
    '''
    state(LED_IO, 1, 0)


def unregistered():
    '''
    Indicates that the system is not registered.
    LED_IO - 1 Hz
    LED_STAT - N/A
    '''
    state(LED_IO, 1, 1)


def ready():
    '''
    Indicates that the system is ready.
    LED_IO - Solid on
    LED_STAT - N/A
    '''
    state(LED_IO, 1, 0)


def incoming_data():
    '''
    Indicates that there is incoming XBee data.
    LED_IO - 4 Hz
    LED_STAT - N/A
    '''
    state(LED_IO, 0.125, 0.125)


def no_network():
    '''
    Indicates that there is no network connection.
    LED_IO - N/A
    LED_STAT - 4 Hz
    '''
    state(LED_STAT, 0.125, 0.125)


def no_internet():
    '''
    Indicates that there is no internet connection.
    LED_IO - N/A
    LED_STAT - 2 Hz
    '''
    state(LED_STAT, 0.25, 0.25)


def no_recursion():
    '''
    Indicates that a connection to recursion.space could not be established.
    LED_IO - N/A
    LED_STAT - 1 Hz
    '''
    state(LED_STAT, 1, 1)


def networked():
    '''
    Indicates that the system is connected to the network.
    LED_IO - N/A
    LED_STAT - Off
    '''
    state(LED_STAT, 0, 0)

# ---------------------------------------------------------------------------- #
#                               Set LED Patterns                               #
# ---------------------------------------------------------------------------- #


def state(io_pin, on_time=0, off_time=0):
    """
    Sets the io_pin state to on or off.
    """
    if io_pin == LED_IO:
        led_io_on_off(on_time, off_time)
    if io_pin == LED_STAT:
        led_io_stat_on_off(on_time, off_time)


def led_io_on_off(on_time=0, off_time=0):
    '''
    Controls the LED used to indicate input/output actions
    '''
    config.LED_IO_ON = on_time
    config.LED_IO_OFF = off_time


def led_io_stat_on_off(on_time=0, off_time=0):
    '''
    Controls the LED used to indicate general system status
    '''
    config.LED_STAT_ON = on_time
    config.LED_STAT_OFF = off_time


# ---------------------------------------------------------------------------- #
#                                  LED Threads                                 #
# ---------------------------------------------------------------------------- #

def led_io_thread():
    '''
    Process occurring in the thread for the I/O LED
    '''
    while True:
        if config.LED_IO_ON > 0:
            GPIO.output(LED_IO, GPIO.HIGH)
            sleep(config.LED_IO_ON)
        if config.LED_IO_OFF > 0:
            GPIO.output(LED_IO, GPIO.LOW)
            sleep(config.LED_IO_OFF)
        if config.LED_IO_ON == 0 and config.LED_IO_OFF == 0:
            GPIO.output(LED_IO, GPIO.LOW)
            sleep(.1)  # Allows CPU time for other threads.


def led_stat_thread():
    '''
    Process occurring in thread for the System Status LED
    '''
    while True:
        if config.LED_STAT_ON > 0:
            GPIO.output(LED_STAT, GPIO.HIGH)
            sleep(config.LED_STAT_ON)
        if config.LED_STAT_OFF > 0:
            GPIO.output(LED_STAT, GPIO.LOW)
            sleep(config.LED_STAT_OFF)
        if config.LED_STAT_ON == 0 and config.LED_STAT_OFF == 0:
            GPIO.output(LED_STAT, GPIO.LOW)
            sleep(.1)  # Allows CPU time for other threads.
