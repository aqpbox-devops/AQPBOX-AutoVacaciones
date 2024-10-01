import pyautogui
from PIL import ImageDraw
from typing import List
import cv2
import numpy as np
import time
import os

def open_exe(executable_path: str):
    """Opens a program given its executable path."""
    os.startfile(executable_path)

def find_and_click(image_path: str, confidence: float=0.9, save_image_path: str=None):
    """Searches for an image on the screen and clicks its position, saving the found area as an image."""
    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    if location:
        cx, cy = pyautogui.center(location)
        print(f"Found at: ({cx}, {cy})")

        if save_image_path is not None:
        
            screenshot = pyautogui.screenshot()

            draw = ImageDraw.Draw(screenshot)

            radius = 10
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill='red', outline='red')

            screenshot.save(save_image_path)
            print(f"Saved found image with red dot to {save_image_path}")

        pyautogui.click(cx, cy)
        return True
    
    print("Image not found.")
    return False

def type_text(text: str):
    """Automatically types text."""
    pyautogui.write(text)

def press_keys(keys: List[str]):
    if len(keys) == 1:
        pyautogui.press(keys[-1])
    elif len(keys) > 1:
        pyautogui.hotkey(*keys)

def take_screenshot(region=None):
    ss = pyautogui.screenshot(region=region)
    ss = np.array(ss)
    return cv2.cvtColor(ss, cv2.COLOR_RGB2BGR)

def wait_screen_update(init_screenshot=None, interval=1):
    """Takes screenshots at intervals and compares with the previous one."""
    if init_screenshot is not None:
        previous_screenshot = init_screenshot

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