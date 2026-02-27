# Test/Example file used for ensuring that the connection module works (and coincidentally showing it's usage a little)
import time
import asyncio
import esp_connection
import main1DLraspberry
import math

connection = None

def most_common(lst):
    return max(set(lst), key=lst.count)

# Define certain callback functions
def motion():
    global connection
    values = []
    time.sleep(1)
    for i in range(5):
        values.append(main1DLraspberry.take_picture())

    average_confidence = sum(list(map(lambda x : x[1], values))) / len(values)
    common = most_common(list(map(lambda x : x[0], values)))

    if average_confidence > 0.95 and connection != None:
        match common:
            case "Plastic":
                connection.send("North")
            case "Paper":
                connection.send("South")
            case "General":
                connection.send("East")
            case "Glass":
                connection.send("West")
            case _:
                pass
    else:
        print("Either no connection or confidence low")


# Unfortunately, I was not able to make async disappear, please run yer code like this when using the connection module.
async def main():
    global connection
    await esp_connection.start()
    connection = esp_connection.Connection()


    # Attach certain callback functions to certain messages, the connection will run the callback when that message is received
    connection.attach("motion", motion)

    print("running")

    await asyncio.sleep(1)

    # Connection will remain open while main is still running
    while True:
        await asyncio.sleep(1)
    

asyncio.run(main())