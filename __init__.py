import display
import time
from machine import Pin
from neopixel import NeoPixel
import nvs
import buttons
import mch22 

# Pin 19 controls the power supply to SD card and neopixels
powerPin = Pin(19, Pin.OUT)

# Pin 5 is the LED's data line
dataPin = Pin(5, Pin.OUT)

# create a neopixel object for 5 pixels
np = NeoPixel(dataPin, 5)

# turn on power to the LEDs
powerPin.on()

def on_home_button(pressed):
  if pressed:
    mch22.exit_python()

buttons.attach(buttons.BTN_HOME, on_home_button)

class State:
    name = nvs.nvs_getstr("owner", "nickname") # Thanks to https://mch2022.badge.team/files/4721 for finding this completely undocumented function
    x = 0
    y = 0
    x_motion = 2
    y_motion = 2
    x_scale = 2
    y_scale = 2
    fps = 30
    color_index = 0

    delay_per_frame = 1 / fps


colors = [
    0xFF0000,
    0x00FF00,
    0x0000FF,
    0xFFFF00,
    0x00FFFF,
    0xFF00FF,
    0xFFA500,
    0xAA00FF,
    0xAA0000,
    0xFFFFFF,
]

def hex_to_rgb(hex_color):
    return (hex_color >> 16, (hex_color >> 8) & 0xFF, hex_color & 0xFF)

def get_color_by_index(index):
    index = index % len(colors)
    return colors[index]

def cycle_color():
    State.color_index += 1
    State.color_index = State.color_index % len(colors)

    # Set the color of the neopixels
    for i in range(5):
        np[i] = hex_to_rgb(get_color_by_index(State.color_index + i))
    np.write()

def draw_text():
    display.drawText(
        State.x,
        State.y,
        State.name,
        colors[State.color_index],
        "PermanentMarker22",
        State.x_scale,
        State.y_scale,
    )
    display.flush()


def movetick():
    # Move the text
    State.x += State.x_motion
    State.y += State.y_motion

    x_upperbound = display.width() - (
        display.getTextWidth(State.name, "PermanentMarker22") * State.x_scale
    )
    y_upperbound = display.height() - (
        display.getTextHeight("PermanentMarker22") * State.y_scale * 2
    )
    # Check for collisions
    if State.x < 0 or State.x > x_upperbound:
        State.x_motion = -State.x_motion
        State.x += State.x_motion
        cycle_color()
    if State.y < 0 or State.y > y_upperbound:
        State.y_motion = -State.y_motion
        State.y += State.y_motion
        cycle_color()


while True:
    performance_start = time.time()
    display.drawFill(0x000000)
    movetick()
    draw_text()
    display.flush()
    performance_end = time.time()
    performance_time = performance_end - performance_start
    # if performance_time < State.delay_per_frame:
    #     time.sleep(State.delay_per_frame - performance_time)
