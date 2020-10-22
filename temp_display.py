# -*- coding: utf-8 -*-

import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789


##### Boilerplate code from Adafruit #####
# https://github.com/adafruit/Adafruit_CircuitPython_RGB_Display/

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

##### End Boilerplate code from Adafruit #####

# Change this to True to see Fahrenheit values
is_fahrenheit = False

def convert_to_fahrenheit(val):
    return round((val * 9/5) + 32, 2)

def temperature_to_string(val):

    return "{}° F".format(convert_to_fahrenheit(val)) if is_fahrenheit else "{}° C".format(val)


while True:
    """
    C1.23 - (C)offee or (V)apor, 1.23 Version
    124 - Current steam temperature in Celsius.
    126 - Target steam temperature in Celsius.
    096 - Current heat exchanger temperature in Celsius.
    0000 - This is a countdown used to track if the machine is in "fast heating" mode, it seems to go anywhere from 1500-0. 0 means it's no longer boosting.
    0 - This represents if the heating element is on, 0 is Off, 1is On.
    """
    read_vals = "C1.23,124,126,095,1337,0"
    try:
        individual_vals = read_vals.split(',')
        mode = individual_vals[0][0]
        current_steam_temp = int(individual_vals[1])
        target_steam_temp = int(individual_vals[2])
        current_hx_temp = int(individual_vals[3])
        fast_heating_time_left = int(individual_vals[4])
        is_heating_element_on = int(individual_vals[5])

        line_1 = "{} Mode".format("Espresso" if mode == 'C' else "Steam")
        line_2 = "Heating Element is {}, Target Steam Temp: {}".format(
            "On" if is_heating_element_on else "Off",
            temperature_to_string(target_steam_temp)
        )
        line_3 = "Current Steam Temp: {}, Current HX Temp: {}".format(
            temperature_to_string(current_steam_temp),
            temperature_to_string(current_hx_temp)
        )
        line_4 = "Fast Heating Mode - Time Left: {}".format(fast_heating_time_left) if fast_heating_time_left else ""

        error = False
    except IndexError:
        line_1 = "Error - Bad Data"
        line_2 = read_vals
        line_3 = ""
        line_4 = ""
        error = True


    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    y = top
    draw.text((x, y), line_1, font=font, fill="#FFFFFF")
    y += font.getsize(line_1)[1]
    draw.text((x, y), line_2, font=font, fill="#FFFFFF")
    y += font.getsize(line_2)[1]
    draw.text((x, y), line_3, font=font, fill="#FFFFFF")
    y += font.getsize(line_3)[1]
    draw.text((x, y), line_4, font=font, fill="#FFFFFF")

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.1)
