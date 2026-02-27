#Setup
    #libraries
    #GPIO pin
    #confidence score minimum
    #motor starting positions


#setting up BLE Server and listener. Uses asyncio to run the server and listener concurrently



#Reset motoros to starting positions


#Main trash Function, runs when received message from PI (stops the asyncio threads)
    #Basic If or else statements. Depending on the message. "Up", "Down", "Left", "Right" and the confidence score
        #If confidence score is less than X amount then move to Waste position.

        #Each message moves the stepper motor Y amount of degrees. 

    #Pushes Servo motor to open the lid

    #Servo goes down.

    #Resets Stepper to original position


#Send function
    #Send BLE Packet to PI with "Start".
    

#Infinite asyncio loop that looks for movement from movement sensor
    #when it does it runs the Send function. 


#Infinite asyncio loop that listens for message from PI
    #when it does it calls the main function with the message from the pi as the argument. 


