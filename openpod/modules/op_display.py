'''
OpenPod | op_display.py
Manages a TFT display, currently setup for the Adafruit 1.3" 240x240 TFT display.
https://learn.adafruit.com/adafruit-1-3-and-1-54-240-x-240-wide-angle-tft-lcd-displays
'''

import time
import busio
import digitalio
from board import SCK, MOSI, MISO, CE0, D24, D25

from adafruit_rgb_display import color565
from adafruit_rgb_display.st7789 import ST7789
from PIL import Image, ImageDraw, ImageFont

# Configuration for CS and DC pins:
CS_PIN = CE0
DC_PIN = D25
RESET_PIN = D24
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)

# Create the ST7789 display:
display = ST7789(
    spi,
    # rotation=90,
    # width=240,
    # height=240,
    # x_offset=53,
    # y_offset=40,
    baudrate=BAUDRATE,
    cs=digitalio.DigitalInOut(CS_PIN),
    dc=digitalio.DigitalInOut(DC_PIN),
    rst=digitalio.DigitalInOut(RESET_PIN))

# Main loop: same as above
while True:
    display.fill(0)  # Clear the display
    display.pixel(120, 160, color565(255, 0, 0))  # Draw a red pixel in the center.
    time.sleep(2)  # Pause 2 seconds.
    display.fill(color565(0, 0, 255))  # Clear the screen blue.
    time.sleep(2)  # Pause 2 seconds.

    width = display.width
    height = display.height
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

    draw.rectangle((0, 0, width, height), fill=(0, 255, 0))

    display.image(image)

    BORDER = 20
    draw.rectangle((BORDER, BORDER, width - BORDER - 1, height - BORDER - 1), fill=(170, 0, 136))

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

    TEXT = "Hello World!"
    (font_width, font_height) = font.getsize(TEXT)
    draw.text(
        (width // 2 - font_width // 2, height // 2 - font_height // 2),
        TEXT,
        font=font,
        fill=(255, 255, 0),
    )

    display.image(image)
    time.sleep(10)
