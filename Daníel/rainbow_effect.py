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
    """Runs a rainbow effect for 3 seconds."""
    global rainbow_active
    rainbow_active = True
    
    # 3 seconds duration, update every 50ms -> 60 frames
    for j in range(60):
        if not rainbow_active:
            break
        for i in range(41):
            pixel_index = (i * 256 // 41) + (j * 15)
            neo[i] = wheel(pixel_index & 255)
        neo.write()
        await asyncio.sleep_ms(50)
    
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
