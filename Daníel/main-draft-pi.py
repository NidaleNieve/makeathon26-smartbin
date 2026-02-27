import os
import sys
import numpy as np
import halcon as ha
import asyncio
from pi_connection_async import PiConnection

#Setup
    #libraries
    #Camera pins
    #MVTec Software setup

def setup_mvtec():
    # OPTIMIZATION: Raspberry Pi 5 has exactly 4 CPU cores.
    ha.set_system('thread_num', 4)
    print("Loading model...")
    model_path = '/home/smartbin/DL/model_Training-260227-105751_opt_sgd.hdl'
    dl_model_handle = ha.read_dl_model(model_path)
    
    img_w = ha.get_dl_model_param_s(dl_model_handle, 'image_width')
    img_h = ha.get_dl_model_param_s(dl_model_handle, 'image_height')
    
    try:
        # Force CPU (Required on Raspberry Pi)
        ha.set_dl_model_param(dl_model_handle, 'device', 'cpu')
    except:
        pass 
        
    ha.set_dl_model_param(dl_model_handle, 'batch_size', 1)

    print("Connecting to IDS camera...")
    device_id = '1409000BFC2E_IDSImagingDevelopmentSystemsGmbH_U33250MLCHQ'
    
    acq_handle = ha.open_framegrabber(
        name='USB3Vision', horizontal_resolution=0, vertical_resolution=0,
        image_width=0, image_height=0, start_row=0, start_column=0,
        field='default', bits_per_channel=-1, color_space='default',
        generic=-1, external_trigger='false', camera_type='default',
        device=device_id, port=0, line_in=-1
    )
    
    return dl_model_handle, acq_handle, img_w, img_h

#setting up BLE Server and listener. Uses asyncio to run the server and listener concurrently
connection = PiConnection()

# Global variables for MVTec
dl_model_handle = None
acq_handle = None
img_w = None
img_h = None

#Main Function, runs when received message from ESP (stops the asyncio threads)
    #Starts camera and MVTec software.
def process_trash():
    global dl_model_handle, acq_handle, img_w, img_h
    
    print("Processing trash...")
    try:
        # Grab Image
        raw_image = ha.grab_image(acq_handle)
        
        # NUMPY BIT-DEPTH CORRECTION
        img_np = ha.himage_as_numpy_array(raw_image)
        
        if img_np.dtype == np.uint16:
            img_max = img_np.max()
            if img_max > 255:
                img_np = (img_np.astype(np.float32) / img_max * 255.0).astype(np.uint8)
            else:
                img_np = img_np.astype(np.uint8)
        
        image = ha.himage_from_numpy_array(img_np)
        
        # Ensure 3-channel RGB
        channels = ha.count_channels_s(image)
        if channels == 1:
            image_rgb = ha.compose3(image, image, image)
        elif channels == 4:
            r, g, b, a = ha.decompose4(image)
            image_rgb = ha.compose3(r, g, b)
        else:
            image_rgb = image

        # Resize
        image_resized = ha.zoom_image_size(image_rgb, img_w, img_h, 'constant')
        
        # DL Normalization
        image_real = ha.convert_image_type(image_resized, 'real')
        image_norm = ha.scale_image(image_real, 0.00392156, 0) # 1/255.0
        
        # Inference
        sample = ha.create_dict()
        ha.set_dict_object(image_norm, sample, 'image')
        dl_result_batch = ha.apply_dl_model(dl_model_handle, [sample],[])
        
        # Extract Results
        dl_result = dl_result_batch[0]
        class_names = ha.get_dict_tuple(dl_result, 'classification_class_names')
        confidences = ha.get_dict_tuple(dl_result, 'classification_confidences')
        
        predicted_type = class_names[0]
        predicted_confidence = confidences[0]
        
        #If else statement with the results from the the MVTec Software
            #Sends BLE Packet to ESP with the direction and confidence score (format: paper 86).
        confidence_percentage = int(predicted_confidence * 100)
        message = f"{predicted_type},{confidence_percentage}"
        print(f"Sending result to ESP: {message}")
        connection.send(message)
        
    except Exception as e:
        print(f"Error processing trash: {e}")

# Attach the process_trash function to the "start" message from ESP
connection.attach("start", process_trash)

#Infinite asyncio loop that listens for message from ESP
    #when it does it calls the main function
async def main():
    global dl_model_handle, acq_handle, img_w, img_h
    
    try:
        print("Initializing MVTec software...")
        dl_model_handle, acq_handle, img_w, img_h = setup_mvtec()
        
        print("Starting BLE connection...")
        await connection.start()
        
    except KeyboardInterrupt:
        print("\nUser stopped.")
    except ha.HError as e:
        print(f"\nHALCON ERROR: {str(e)}")
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
    finally:
        if acq_handle is not None:
            ha.close_framegrabber(acq_handle)
        print("Cleaned up resources.")

if __name__ == '__main__':
    asyncio.run(main())


