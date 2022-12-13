import pygame
import pygame.camera
import pygame_menu
import glob
import numpy as np
import wave
import cv2    
    
def object_tracking(self, window, current_frame, previous_frame):
    previous_frame = pygame.surfarray.array3d(previous_frame)
    current_frame = pygame.surfarray.array3d(current_frame)

    previous_frame = previous_frame.swapaxes(0,1)
    current_frame = current_frame.swapaxes(0,1)

    # Convert frames to grayscale
    old_frame_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
    current_frame_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    
    # Get template image from the old frame
    template_img = old_frame_gray[window[1]:window[3], window[0]:window[2]]
    
    # Create a matching template
    w, h = template_img.shape[::-1]

    res = cv2.matchTemplate(current_frame_gray, template_img, cv2.TM_CCOEFF_NORMED)
    
    # Get the location of the object in the current frame 
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return ([max_loc[0], max_loc[1]])