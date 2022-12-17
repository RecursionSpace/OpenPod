## Electronics

Currently the system makes use of the GPIO on the Raspberry Pi. These pins are limited to an output of 3.3v at 16mA.

### Visual Indicators

The Pod has two LED indicators on it, a green and red. The [green LED](https://www.digikey.com/en/products/detail/lumex-opto-components-inc/SSI-LXH072GD/144732) is 2.2v at 25mA and will require a 68.75ohm (68ohm standard) resistor while the [red LED](https://www.digikey.com/en/products/detail/lumex-opto-components-inc/SSI-LXH072ID/144729) one is 2v at 30mA and will require a 81.25 ohm (82 ohm standard) resistor. Both resistors were [calculated](https://ohmslawcalculator.com/led-resistor-calculator) with the current caped at 16mA.

A combination of the LEDs blinking or solid on/off in a [controlled pattern](https://en.wikipedia.org/wiki/International_Blinking_Pattern_Interpretation) provides information to the users.

|                                                                                                                               | Green - I/O “Simulating XBee activity, should really be connected to one of the XBee pins” | Red - Overall Status |
|:-----------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------:|:--------------------:|
|                               **Initializing** - Program called, not ready to receive requests.                               |                                            Off                                             |          On          |
|                          No Ethernet: The HUB has not received an IP address and is set to 127.0.0.1                          |                                            N/A                                             |         4 Hz         |
|                                                    Ethernet, No Internet:                                                     |                                            N/A                                             |         2 Hz         |
|                                               Internet, Recursion Unreachable:                                                |                                            N/A                                             |         1 Hz         |
|                                                  Recursion.Space Reachable:                                                   |                                            N/A                                             |         Off          |
| **Unregistered** - All network and hardware tests passed, ready to receive XBee requests, Pod IS NOT registered with a space. |                                            1 Hz                                            |         N/A          |
|    **Ready** - All network and hardware tests passed, ready to receive XBee requests, and Pod IS registered with a space.     |                                             On                                             |         N/A          |
|                                    XBee I/O Data: Anytime the XBee receives or sends data.                                    |                                            4 Hz                                            |         N/A          |
|                                              Fatal Error: - USB XBee Unreachable                                              |                                      2 Hz Alternating                                      |   2 Hz Alternating   |

## Assembly

### Main Enclosure

1) Remove any stickers, labels, and decals from the enclosure, then remove the two screws to temporarily detach the door. (Goo Gone followed by rubbing alcohol, helps remove any residual sticker residue.
2) Using the top flange, trace the opening and then cut using a jigsaw and a fine wood bit attachment. The screw holes can be oversized with an 11/64 drill bit.
3) Cut off the top stands using an oscillating saw and then use a side cutter to clean any repairing plastic off.
4) Prepare part number HB-H-I-EBF/C with the threaded inserts.
5) Mount the flanges to the enclosure and place them in the 4 M4 philips mounting screws. The enclosure is now complete and can be set off to the side.

### Processing Unit

Prepare electronic assemblies, including power connectors, LEDs, and reset buttons.
Insert threads into the various housing components.
Insert the completed electronic assemblies, such as the power outlet, LEDs and ethernet jack.
