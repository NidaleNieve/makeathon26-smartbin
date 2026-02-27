from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms

neo = NeoPixel(Pin(21), 41)   #  8 Leds (0 - 7)

# slökktu á öllum leds
neo.fill([0, 0, 0])

# Allar NeoPixel perurnar lýsa rauðu ljósi í eina sekúndu með fill aðferð.
neo.fill([255, 255, 255])
neo.write()
