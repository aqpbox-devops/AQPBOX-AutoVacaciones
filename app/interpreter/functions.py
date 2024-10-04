import pyautogui
from PIL import ImageDraw
from typing import List, Dict
from mylogger.mydecorators import singleton
import getpass
import cv2
import json
import numpy as np
import time
import os

from mylogger.printer import *

import pandas as pd 

@singleton
class DataFrameIterator:
    def __init__(self) -> None:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        self.reset()

    def eof(self, offset: int=0) -> bool:
        continue_it = (self.row_idx + offset) >= len(self.df)
        stprint(f"Dataframe reached end of file: {continue_it}")
        return continue_it
    
    def next_row(self, rows2jump: int=1) -> bool:
        self.row_idx += rows2jump
        return not self.eof()

    def reset(self) -> None:
        self.df: pd.DataFrame = None
        self.row_idx = -1

    def get_by_letter(self, col: str) -> str:
        col_idx = -1

        for i, char in enumerate(reversed(col)):
            if 'A' <= char <= 'Z':
                col_idx += (ord(char) - ord('A') + 1) * (26 ** i)
            else:
                stfatal(f"Column head {YLW}{col}{WHT} is not valid -> Issue '{CYN}{char}{WHT}' letter")
        
        stprint(f"Excel column style: {YLW}{col}{WHT} equals to {YLW}{col_idx}{WHT}.")
        return self.get_by_id(col_idx)

    def get_by_id(self, col: str | int) -> str:
        if self.df is not None:
            col_idx = col

            if isinstance(col, str):
                col_idx = self.df.get_loc(col)

            cell = self.df.iat[self.row_idx, col_idx]

            return str(cell)
        return ''
    

    def reformat_df(self):
        # Verificar si self.df es un DataFrame
        if not isinstance(self.df, pd.DataFrame):
            stfatal("The current dataframe variable does not contain a pd.DataFrame")

        # Convertir todos los datos a string
        self.df = self.df.astype(str)

        
        for col in self.df.columns:
            # Verificar si la columna es de tipo objeto
            if pd.api.types.is_object_dtype(self.df[col]):
                # Limpiar espacios y comprobar si la columna tiene el formato yyyy-mm-dd
                if self.df[col].str.strip().str.match(r'^\d{4}-\d{2}-\d{2}$').any():
                    # Reordenar la fecha a dd mm yyyy
                    self.df[col] = self.df[col].apply(lambda x: f"{x[8:10]}{x[5:7]}{x[0:4]}")

    def load_from_file(self, fn_data: str) -> None:
        try:
            self.reset()

            if fn_data.endswith('.xlsx'):
                self.df = pd.read_excel(fn_data, engine='openpyxl')
            elif fn_data.endswith('.csv'):
                self.df = pd.read_csv(fn_data, encoding='utf8')

            self.reformat_df()

            stprint(f"File {fn_data} successfully loaded.")

        except FileNotFoundError:
            stfatal(f"Dataframe {CYN}{fn_data}{WHT} source not found.")

def take_screenshot(region=None):
    ss = pyautogui.screenshot(region=region)
    ss = np.array(ss)
    return cv2.cvtColor(ss, cv2.COLOR_RGB2BGR)

def wait_screen_update(init_screenshot=None, interval=1):
    """Takes screenshots at intervals and compares with the previous one."""
    if interval > 0:
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
                stprint('Update on screen detected')
                break

            previous_screenshot = current_screenshot

def open_exe(fn_exe: str, wait: float=0):
    """Opens a program given its executable path."""
    try:
        ss_now = take_screenshot()
        os.startfile(fn_exe)
        wait_screen_update(ss_now, interval=wait)
    except FileNotFoundError:
        stfatal(f"Executable {CYN}{fn_exe}{WHT} not found.")

def find_image(fn_img: str, confidence: float=0.99, save_fn_img: str=None):
    location = pyautogui.locateOnScreen(fn_img, confidence=confidence)
    cx, cy = -1, -1

    if location:
        cx, cy = pyautogui.center(location)
        stprint(f"Found at: [{YLW}{cx}{WHT}, {YLW}{cy}{WHT}]")

        if save_fn_img is not None:
        
            screenshot = pyautogui.screenshot()

            draw = ImageDraw.Draw(screenshot)

            radius = 10
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill='red', outline='red')

            screenshot.save(save_fn_img)
            stprint(f"Saved found image with red dot to {save_fn_img}")

    return location is not None, cx, cy

def click(x: float, y: float, n_clicks: int=1) -> None:
    for _ in range(n_clicks):
        pyautogui.click(x, y)

def find_and_click(fn_img: str, confidence: float=0.99, save_fn_img: str=None, n_clicks: int=1, wait: float=0, ignore_fatal: bool=False):
    """Searches for an image on the screen and clicks its position, saving the found area as an image."""
    if not os.path.isfile(fn_img):
        stfatal(f"Image {CYN}{fn_img}{WHT} not found.")

    try:
        found, cx, cy = find_image(fn_img, confidence, save_fn_img)
        if found:
            ss_now = take_screenshot()
            click(cx, cy, n_clicks=n_clicks)
            wait_screen_update(ss_now, interval=wait)
            return True
    
    except pyautogui.ImageNotFoundException:
        if n_clicks > 0 and not ignore_fatal:
            stfatal(f"Image not found on screen to click {n_clicks} times.")
    
    return False

def write_text(text: str, wait: float=0):
    """Automatically types text."""
    ss_now = take_screenshot()
    pyautogui.write(text)
    stprint(f"Writing '{CYN}{text}{WHT}'")
    wait_screen_update(ss_now, interval=wait)

def press_keys(keys: List[str] | str, delay: float=0, wait: float=0):
    if delay > 0:
        time.sleep(delay)
    ss_now = take_screenshot()
    if isinstance(keys, str):
        pyautogui.press(keys)
    elif len(keys) == 1:
        pyautogui.press(keys[-1])
    elif len(keys) > 1:
        pyautogui.hotkey(*keys)
    stprint(f"Keys pressed: {YLW}{'+'.join(keys) if isinstance(keys, list) else keys}{WHT}")
    wait_screen_update(ss_now, interval=wait)

def load_credentials(fn_json: str) -> Dict[str, str] | None:
    data: Dict[str, str] = {}

    def add_data(key: str, val: str):
        if key not in data.keys() or val != '':
            data[key] = val
            
    overwrite = input(f"{CYN}$> {WHT}Overwrite {CYN}'{fn_json}'{WHT} ({YLW}y{WHT}/n)?: ")

    if not fn_json.endswith('.json'):
        return None
        
    if os.path.isfile(fn_json):
        with open(fn_json, 'r') as f:
            data = json.load(f)

    if overwrite.lower() == 'y':
        add_data('exe', input('Executable path: '))
        add_data('imgs', input('Dir to images for reference: '))
        add_data('xlsxi', input('Path to excel input: '))
        add_data('xlsxo', input('Path to excel output: '))
        add_data('username', input('Username: '))
        add_data('secret', getpass.getpass('Password: '))

        with open(fn_json, 'w') as f:
            json.dump(data, f, indent=1)

    return data

def save_dataframe(fn_data: str, df: pd.DataFrame) -> None:
    if fn_data.endswith('.xlsx'):
        df.to_excel(fn_data, index=None)
    elif fn_data.endswith('.csv'):
        df.to_csv(fn_data, index=None, encoding='utf8')
    else:
        stfatal(f"Not implemented save mode for '{RED}{fn_data}{WHT}'") 
    stprint(f"Report file saved at '{GRN}{fn_data}{WHT}'")   

def dirjoin(dir: str, fn: str) -> str:
    slash_join = ''
    if dir.__contains__('/') and not dir.endswith('/'):
        slash_join = '/'
    elif dir.__contains__('\\') and not dir.endswith('\\'):
        slash_join = '\\'
    return dir + slash_join + fn

if __name__ == "__main__":
    pass