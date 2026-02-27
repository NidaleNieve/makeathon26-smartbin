import uasyncio as asyncio
from machine import Pin
from neopixel import NeoPixel

# Setup NeoPixel for the rainbow effect
neo = NeoPixel(Pin(21), 41)   # 41 LEDs on Pin 4
rainbow_active = False

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

async def rainbow_effect():
    """Runs a moving rainbow effect with black gaps infinitely."""
    global rainbow_active
    rainbow_active = True
    
    j = 0
    while rainbow_active:
        for i in range(41):
            # Create moving gaps: 5 pixels on, 4 pixels off
            if (i - j) % 9 < 5:
                pixel_index = (i * 256 // 41) + (j * 15)
                neo[i] = wheel(pixel_index & 255)
            else:
                neo[i] = (0, 0, 0)
        neo.write()
        await asyncio.sleep_ms(50)
        j += 1
    
    # Turn off lights after the effect finishes
    neo.fill([0, 0, 0])
    neo.write()
    rainbow_active = False

async def main():
    print("Starting rainbow effect...")
    await rainbow_effect()
    print("Rainbow effect finished.")

# Run the standalone effect if this file is executed directly
if __name__ == "__main__":
    asyncio.run(main())
