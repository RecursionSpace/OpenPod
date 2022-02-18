#!/usr/bin/env python3

'''
Modlue manages raspbery pi gpio functionality.
'''

from time import sleep

import config

from RPi import GPIO

from settings import LED_IO, LED_STAT

GPIO.setmode(GPIO.BCM)								#Setup for LED indicators.
GPIO.setwarnings(False)

GPIO.setup(LED_IO, GPIO.OUT)
GPIO.setup(LED_STAT, GPIO.OUT)

GPIO.output(LED_IO,GPIO.LOW)
GPIO.output(LED_STAT,GPIO.LOW)

LED_IO_ON 		= 0
LED_IO_OFF 		= 0
LED_STAT_ON 	= 0
LED_STAT_OFF 	= 0

config.LED_IO_ON = 0
config.LED_IO_OFF = 0

config.LED_STAT_ON = 0
config.LED_STAT_OFF = 0

# def Blink(io_pin, BlinkTime, BlinkCount):
# 	for i in range (BlinkCount):
# 		sleep (BlinkTime)
# 		GPIO.output (io_pin, GPIO.HIGH)
# 		sleep (BlinkTime)
# 		GPIO.output (io_pin, GPIO.LOW)
# 	return

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
    # global LED_IO_ON
    # global LED_IO_OFF
    config.LED_IO_ON = on_time
    config.LED_IO_OFF = off_time


def led_io_stat_on_off(on_time=0, off_time=0):
    '''
    Controls the LED used to indicate general system status
    '''
    # global LED_STAT_ON
    # global LED_STAT_OFF
    config.LED_STAT_ON = on_time
    config.LED_STAT_OFF = off_time

# ---------------------------------------------------------------------------- #
#                                  LED Threads                                 #
# ---------------------------------------------------------------------------- #

def led_io_thread():
    '''
    Process occuring in the thread for the I/O LED
    '''
    while True:
        # global LED_IO_ON
        # global LED_IO_OFF
        if config.LED_IO_ON > 0:
            GPIO.output(LED_IO, GPIO.HIGH)
            sleep (config.LED_IO_ON)
        if config.LED_IO_OFF > 0:
            GPIO.output(LED_IO, GPIO.LOW)
            sleep (config.LED_IO_OFF)
        if config.LED_IO_ON == 0 and config.LED_IO_OFF == 0:
            GPIO.output(LED_IO, GPIO.LOW)
            sleep(.1) #Allows CPU time for other threads.


def led_stat_thread():
    '''
    Process occuring in thethread for the System Status LED
    '''
    while True:
        # global LED_STAT_ON
        # global LED_STAT_OFF
        if config.LED_STAT_ON > 0:
            GPIO.output(LED_STAT, GPIO.HIGH)
            sleep (config.LED_STAT_ON)
        if config.LED_STAT_OFF>0:
            GPIO.output(LED_STAT, GPIO.LOW)
            sleep (config.LED_STAT_OFF)
        if config.LED_STAT_ON == 0 and config.LED_STAT_OFF == 0:
            GPIO.output(LED_STAT, GPIO.LOW)
            sleep(.1) #Allows CPU time for other threads.
