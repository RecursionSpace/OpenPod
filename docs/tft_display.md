# TFT Display

A small TFT display provides excellent feedback for the user. It can be used to display the current status of the device, or to display the current settings.

## Pod Display

The latest version of the Pod uses the [Adafruit 1.3" TFT display](https://www.adafruit.com/product/4313). This display is a 240x240 pixel display with a 16-bit color depth. It is a wide-angle display, which means that it can be viewed from a wide range of angles without the image becoming distorted.

Detailed connection instructions are available on the [Adafruit Website](https://learn.adafruit.com/adafruit-1-14-240x135-color-tft-breakout/python-wiring-and-setup), basic pin connections are shown below.

| TFT Display | Pod     |
|-------------|---------|
| Vin         | 3.3V    |
| GND         | GND     |
| SCK         | SLCK    |
| MOSI(SI)    | MOSI    |
| CS          | CE0     |
| RST         | GPIO 24 |
| D/C         | GPIO 25 |

## Programming the Display

**Note: All requirements are fulfilled when running the OpenPod installer.**

Drivers for the display are found in the [Adafruit CircuitPython RGB Display Repository](https://github.com/adafruit/Adafruit_CircuitPython_RGB_Display) and can be installed using the following command:

```bash
sudo pip3 install adafruit-circuitpython-rgb-display
```

To use the display with Python, you will need to install the following packages and libraries:

```bash
sudo apt-get install libjpeg-dev
sudo apt-get install zlib1g-dev
sudo apt-get install libfreetype6-dev
sudo pip3 install Pillow
```
