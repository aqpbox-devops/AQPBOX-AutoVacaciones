import pyautogui
from PIL import ImageDraw
from typing import List
import cv2
import numpy as np
import time
import os

from mylogger.printer import *

def open_exe(executable_path: str):
    """Opens a program given its executable path."""
    try:
        os.startfile(executable_path)
    except FileNotFoundError:
        stfatal(f"Executable {CYN}{executable_path}{WHT} not found.")

def find_image(image_path: str, confidence: float=0.9, save_image_path: str=None):
    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    cx, cy = -1, -1

    if location:
        cx, cy = pyautogui.center(location)
        stprint(f"Found at: [{YLW}{cx}{WHT}, {YLW}{cy}{WHT}]")

        if save_image_path is not None:
        
            screenshot = pyautogui.screenshot()

            draw = ImageDraw.Draw(screenshot)

            radius = 10
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill='red', outline='red')

            screenshot.save(save_image_path)
            print(f"Saved found image with red dot to {save_image_path}")

    return location is not None, cx, cy

def find_and_click(image_path: str, confidence: float=0.9, save_image_path: str=None, perform_click: bool=True):
    """Searches for an image on the screen and clicks its position, saving the found area as an image."""
    if not os.path.isfile(image_path):
        stfatal(f"Image {CYN}{image_path}{WHT} not found.")

    try:
        found, cx, cy = find_image(image_path, confidence, save_image_path)
        if found:
            if perform_click:
                pyautogui.click(cx, cy)
            return True
    
    except pyautogui.ImageNotFoundException:
        if perform_click:
            stfatal("Image not found on screen.")
    return False

def write_text(text: str):
    """Automatically types text."""
    pyautogui.write(text)

def press_keys(keys: List[str] | str):
    if isinstance(keys, str):
        pyautogui.press(keys)
    elif len(keys) == 1:
        pyautogui.press(keys[-1])
    elif len(keys) > 1:
        pyautogui.hotkey(*keys)

def take_screenshot(region=None):
    ss = pyautogui.screenshot(region=region)
    ss = np.array(ss)
    return cv2.cvtColor(ss, cv2.COLOR_RGB2BGR)

def wait_screen_update(init_screenshot=None, interval=1):
    """Takes screenshots at intervals and compares with the previous one."""
    previous_screenshot = init_screenshot
    
    if init_screenshot is None:
        previous_screenshot = take_screenshot()
    
    while True:
        time.sleep(interval)
        current_screenshot = take_screenshot()
        diff = cv2.absdiff(current_screenshot, previous_screenshot)
        _, thresh = cv2.threshold(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY),
                                  25, 255, cv2.THRESH_BINARY)
        if ((np.sum(thresh) / thresh.size) * 100) > 30:
            print('Update on screen detected')
            break

        previous_screenshot = current_screenshot

if __name__ == "__main__":
    pass