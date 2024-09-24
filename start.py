import pyautogui
import cv2
import numpy as np
import time
import os

STATIC_DIR = 'static/'

def open_program(executable_path):
    """Opens a program given its executable path."""
    os.startfile(executable_path)

def find_and_click(image_path, confidence=0.8):
    """Searches for an image on the screen and clicks its position."""
    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    if location:
        cx, cy = pyautogui.center(location)
        pyautogui.click(cx, cy)
        return True
    return False

def type_text(text):
    """Automatically types text."""
    pyautogui.write(text)

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

def main():
    executable_path = r"C:\Ofisegu\IN000001.exe"
    at_begin = take_screenshot()

    open_program(executable_path)

    wait_screen_update(init_screenshot=at_begin, interval=1)

    # Find image and click
    if find_and_click(STATIC_DIR + 'REF_START.png'):
        print("Image found and click performed.")
    
    # Automatically enter text
    type_text("Sample text")
    
    # Take screenshots and compare
    wait_screen_update(interval=1)

if __name__ == "__main__":
    main()