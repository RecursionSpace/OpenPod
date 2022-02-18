#!/usr/bin/env python3

'''Settings file contains "constants" that are unlikely to be changed.'''

DEBUG = True
Pi = False


if DEBUG is True:
    RecursionURL = 'https://dev.recursion.space'
    RECURSION_DOMAIN = 'dev.recursion.space'
    RECURSION_API_URL = 'https://dev.api.recursion.space'

else:
    RecursionURL = 'https://recursion.space'
    RECURSION_DOMAIN = 'recursion.space'
    RECURSION_API_URL = 'https://api.recursion.space'

LED_IO = 23		#GPIO port that the green LED is connected to
LED_STAT = 17	#GPIO port that the yellow/amber LED is connected to
