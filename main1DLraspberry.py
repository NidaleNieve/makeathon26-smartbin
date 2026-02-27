import os
import sys
import numpy as np
import halcon as ha

def open_window(width, height):
    """Open native window for drawing."""
    if os.name == 'nt':
        # This handles Windows GUI threads. 
        # On Linux (Raspberry Pi), HALCON handles X11/XWayland threading automatically.
        ha.set_system('use_window_thread', 'true')

    return ha.open_window(
        row=0,
        column=0,
        width=width,
        height=height,
        father_window=0,
        mode='visible',
        machine=''
    )


# OPTIMIZATION: Raspberry Pi 5 has exactly 4 CPU cores.
# Explicitly telling HALCON to use 4 threads optimizes CPU inference.
ha.set_system('thread_num', 4)

# 1. INITIALIZE MODEL
print("Loading model...")
# CHANGE 1: Updated to a standard Linux path structure. 
# Make sure to place your model here or update this path!
model_path = '/home/smartbin/DL/model_Training-260227-105751_opt_sgd.hdl'
dl_model_handle = ha.read_dl_model(model_path)

img_w = ha.get_dl_model_param_s(dl_model_handle, 'image_width')
img_h = ha.get_dl_model_param_s(dl_model_handle, 'image_height')

#try:
    # Force CPU (Required on Raspberry Pi)
ha.set_dl_model_param(dl_model_handle, 'runtime', 'cpu')
print("works")
#except:
#    pass 
    
# ha.set_dl_model_param(dl_model_handle, 'batch_size', 1)

# 2. INITIALIZE IDS CAMERA
print("Connecting to IDS camera...")
# The USB3Vision device ID remains the same across Windows and Linux
device_id = '1409000BFC2E_IDSImagingDevelopmentSystemsGmbH_U33250MLCHQ'

acq_handle = ha.open_framegrabber(
    name='USB3Vision', horizontal_resolution=0, vertical_resolution=0,
    image_width=0, image_height=0, start_row=0, start_column=0,
    field='default', bits_per_channel=-1, color_space='default',
    generic=-1, external_trigger='false', camera_type='default',
    device=device_id, port=0, line_in=-1
)

# 3. SETUP DISPLAY
sample_img = ha.grab_image(acq_handle)
cam_w, cam_h = ha.get_image_size_s(sample_img)

window = open_window(cam_w // 2, cam_h // 2)
ha.set_part(window, 0, 0, cam_h - 1, cam_w - 1)
ha.set_font(window, 'DejaVu Sans-16')

def take_picture():
    try:
        print("Classification Active. Press Ctrl+C to exit.")

        # A. Grab Image
        raw_image = ha.grab_image(acq_handle)
        
        # B. NUMPY BIT-DEPTH CORRECTION
        img_np = ha.himage_as_numpy_array(raw_image)
        
        if img_np.dtype == np.uint16:
            img_max = img_np.max()
            if img_max > 255:
                img_np = (img_np.astype(np.float32) / img_max * 255.0).astype(np.uint8)
            else:
                img_np = img_np.astype(np.uint8)
        
        image = ha.himage_from_numpy_array(img_np)
        
        # C. Ensure 3-channel RGB
        channels = ha.count_channels_s(image)
        if channels == 1:
            image_rgb = ha.compose3(image, image, image)
        elif channels == 4:
            r, g, b, a = ha.decompose4(image)
            image_rgb = ha.compose3(r, g, b)
        else:
            image_rgb = image

        # D. Resize
        image_resized = ha.zoom_image_size(image_rgb, img_w, img_h, 'constant')
        
        # E. DL Normalization
        image_real = ha.convert_image_type(image_resized, 'real')
        image_norm = ha.scale_image(image_real, 0.00392156, 0) # 1/255.0
        
        # F. Inference
        sample = ha.create_dict()
        ha.set_dict_object(image_norm, sample, 'image')
        dl_result_batch = ha.apply_dl_model(dl_model_handle, [sample],[])
        
        # G. Extract Results
        dl_result = dl_result_batch[0]
        class_names = ha.get_dict_tuple(dl_result, 'classification_class_names')
        # Plastic, Glass, Paper, General
        confidences = ha.get_dict_tuple(dl_result, 'classification_confidences')
        
        predicted_type = class_names[0]
        predicted_confidence = confidences[0]
        
        # H. Display
        ha.disp_obj(image_rgb, window)
        msg = f"Type: {predicted_type} ({predicted_confidence * 100:.1f}%)"
        
        color = 'forest green' if predicted_confidence > 0.85 else 'red'
        ha.disp_text(window, msg, 'window', 12, 12, 'white',['box_color'], [color])

        return (predicted_type, predicted_confidence)

    except KeyboardInterrupt:
        print("\nUser stopped.")
    except ha.HError as e:
        print(f"\nHALCON ERROR: {str(e)}")
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
    finally:
        if 'acq_handle' in locals():
            ha.close_framegrabber(acq_handle)
        if 'window' in locals():
            ha.close_window(window)
        print("Cleaned up resources.")
        return ("None")

