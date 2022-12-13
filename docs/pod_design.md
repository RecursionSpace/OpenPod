## Electronics

Currently the system makes use of the GPIO on the Raspberry Pi. These pins are limited to an output of 3.3v at 16mA.

### Visual Indicators

The Hub has two LED indicators on it, a green and red. The [green LED](https://www.digikey.com/en/products/detail/lumex-opto-components-inc/SSI-LXH072GD/144732) is 2.2v at 25mA and will require a 68.75ohm (68ohm standard) resistor while the [red LED](https://www.digikey.com/en/products/detail/lumex-opto-components-inc/SSI-LXH072ID/144729) one is 2v at 30mA and will require a 81.25 ohm (82 ohm standard) resistor. Both resistors were [calculated](https://ohmslawcalculator.com/led-resistor-calculator) with the current caped at 16mA.

A combination of the LEDs blinking or solid on/off in a [controlled pattern](https://en.wikipedia.org/wiki/International_Blinking_Pattern_Interpretation) provides information to the users.

|                                                                                                                                                      | Green - I/O “Simulating XBee activity, should really be connected to one of the XBee pins” | Red - Overall Status |
|:----------------------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------:|:--------------------:|
|                                Program Called: Not ready to receive requests and have not tested network connection.                                 |                                            Off                                             |          On          |
|                                     No Ethernet: The HUB has not received an IP address and is set to 127.0.0.1                                      |                                            N/A                                             |         4 Hz         |
|                                                                Ethernet, No Internet:                                                                |                                            N/A                                             |         2 Hz         |
|                                                           Internet, Recursion Unreachable:                                                           |                                            N/A                                             |         1 Hz         |
|                                                              Recursion.Space Reachable:                                                              |                                            N/A                                             |         Off          |
| Unregistered: Registered and Ready: All network and hardware tests passed, ready to receive XBee requests and HUB IS NOT registered with a facility. |                                            1 Hz                                            |         N/A          |
|         Registered and Ready: All network and hardware tests passed, ready to receive XBee requests, and HUB IS registered with a facility.          |                                             On                                             |         N/A          |
|                                               XBee I/O Data: Anytime the XBee receives or sends data.                                                |                                            4 Hz                                            |         N/A          |
|                                                         Fatal Error: - USB XBee Unreachable                                                          |                                      2 Hz Alternating                                      |   2 Hz Alternating   |
