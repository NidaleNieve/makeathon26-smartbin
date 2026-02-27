# Test/Example file used for ensuring that the connection module works (and coincidentally showing it's usage a little)

import asyncio
import esp_connection

# Define certain callback functions
def test():
    print("test!")

def motion():
    # Motion code
    print("would activate machine vision here")

# Unfortunately, I was not able to make async disappear, please run yer code like this when using the connection module.
async def main():
    await esp_connection.start()

    connection = esp_connection.Connection()

    # Attach certain callback functions to certain messages, the connection will run the callback when that message is received
    connection.attach("test", test)
    connection.attach("motion", motion)

    print("running")

    await asyncio.sleep(1)

    # We can send our own messages, here we send down, which prompts the esp test code to send back "test"
    connection.send("test")


    # Connection will remain open while main is still running
    while True:
        await asyncio.sleep(1)
    

asyncio.run(main())