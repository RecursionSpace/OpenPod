#!/usr/bin/env python3

'''Settings file contains "constants" that are unlikely to be changed.'''

DEBUG = True
IS_PI = False


if DEBUG is True:
    RECURSION_SPACE_URL = 'https://dev.recursion.space'
    RECURSION_DOMAIN = 'dev.recursion.space'
    RECURSION_API_URL = 'https://dev.api.recursion.space'

else:
    RECURSION_SPACE_URL = 'https://recursion.space'
    RECURSION_DOMAIN = 'recursion.space'
    RECURSION_API_URL = 'https://api.recursion.space'

LED_IO = 23		#GPIO port that the green LED is connected to
LED_STAT = 17	#GPIO port that the yellow/amber LED is connected to
