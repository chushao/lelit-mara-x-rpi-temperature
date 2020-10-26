# -*- coding: utf-8 -*-

import time
import digitalio
import board
import serial
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
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

##### End Boilerplate code from Adafruit #####

# Button usage
button_top = digitalio.DigitalInOut(board.D23)
button_bottom = digitalio.DigitalInOut(board.D24)
button_top.switch_to_input()
button_bottom.switch_to_input()

is_timer_mode = False
timer_started = False
time_elapsed = 0
start_time = time.time()
stop_time = time.time()


usb_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Change this to True to see Fahrenheit values
is_fahrenheit = False

def convert_to_fahrenheit(val):
    return round((val * 9/5) + 32, 2)

def temperature_to_string(val):
    return "{}° F".format(convert_to_fahrenheit(val)) if is_fahrenheit else "{}° C".format(val)


def draw_stats():
    """
    C1.23 - (C)offee or (V)apor, 1.23 Version
    124 - Current steam temperature in Celsius.
    126 - Target steam temperature in Celsius.
    096 - Current heat exchanger temperature in Celsius.
    0000 - If the machine is fast heating then this will count down until it goes to normal heating mode.
    0 - Heating Element 0 = off, 1 = on.
    """
    # read_vals = "C1.23,124,126,095,1337,0"
    read_vals = usb_serial.readline().decode('UTF-8').rstrip()
    try:
        individual_vals = read_vals.split(',')
        mode = individual_vals[0][0]
        current_steam_temp = int(individual_vals[1])
        target_steam_temp = int(individual_vals[2])
        current_hx_temp = int(individual_vals[3])
        fast_heating_time_left = int(individual_vals[4])
        is_heating_element_on = int(individual_vals[5])

        line_1 = "{} Mode".format("Espresso" if mode == 'C' else "Steam")
        line_2 = "Heating Element is {}".format("On" if is_heating_element_on else "Off")
        line_3 = "Tgt Steam Temp: {}".format(temperature_to_string(target_steam_temp))
        line_4 = "Cur Steam Temp: {}".format(temperature_to_string(current_steam_temp))
        line_5 = "Cur HX Temp: {}".format(temperature_to_string(current_hx_temp))
        line_6 = "Fast Heating: {} sec".format(fast_heating_time_left) if fast_heating_time_left else ""
    except IndexError:
        line_1 = ""
        line_2 = ""
        line_3 = ""
        line_4 = ""
        line_5 = ""
        line_6 = ""

    y = top
    draw.text((x, y), line_1, font=font, fill="#FFFFFF")
    y += font.getsize(line_1)[1]
    draw.text((x, y), line_2, font=font, fill="#FFFFFF")
    y += font.getsize(line_2)[1]
    draw.text((x, y), line_3, font=font, fill="#FFFFFF")
    y += font.getsize(line_3)[1]
    draw.text((x, y), line_4, font=font, fill="#FFFFFF")
    y += font.getsize(line_4)[1]
    draw.text((x, y), line_5, font=font, fill="#FFFFFF")
    y += font.getsize(line_5)[1]
    draw.text((x, y), line_6, font=font, fill="#FFFFFF")

def draw_timer():
    if timer_started:
        stop_time = time.time()
        time_elapsed = stop_time - start_time
    y = top
    draw.text((x, y), str(round(time_elapsed, 2)), font=font, fill="#FFFFFF")



while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    if not button_bottom.value and button_top.value: # reverse logic, bottom button pressed
        if is_timer_mode:
            time_elapsed = 0
            is_timer_mode = False
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        else:
            is_timer_mode = True
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)

    elif button_bottom.value and not button_top.value and is_timer_mode:
        if timer_started:
            timer_started = False
        else:
            start_time = time.time()
            timer_started = True


    if is_timer_mode:
        draw_timer()
    else:
        draw_stats()

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.1)


