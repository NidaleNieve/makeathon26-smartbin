#Setup
    #libraries
    #Camera pins
    #MVTec Software setup


#setting up BLE Server and listener. Uses asyncio to run the server and listener concurrently


#Main Function, runs when received message from ESP (stops the asyncio threads)
    #Starts camera and MVTec software.

    #If else statement with the results from the the MVTec Software
        #Depending on the results (paper, plastic, etc.) send "Up", "Down", "Left", "Right"
        #Sends BLE Packet to ESP with the direction and confidence score.

#Infinite asyncio loop that listens for message from ESP
    #when it does it calls the main function


