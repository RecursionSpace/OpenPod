'''
Returns the system information of the host.
'''

from modules import op_config

PI_CONTROLLERS = ['BCM2835']


def is_pi():
    '''
    Returns True if the host is a Raspberry Pi.
    '''
    mcu = op_config.get('Hardware').get('controller')

    if mcu in PI_CONTROLLERS:
        return True

    return False
