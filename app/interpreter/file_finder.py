import os
import win32com.client
import winshell

def find_shortcut_target(shortcut_name):
    desktop_paths = [
        winshell.desktop(),
        os.path.join(os.environ['PUBLIC'], 'Desktop')
    ]
    
    for desktop_path in desktop_paths:
        shortcut_path = os.path.join(desktop_path, f"{shortcut_name}.lnk")

        if os.path.exists(shortcut_path):
            try:
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)

                return shortcut.TargetPath
            except Exception as e:
                continue
        else:
            continue
    return None
