import subprocess
import sys

def build_executable():
    command = [
        'pyinstaller',
        '--onefile',
        '--clean',
        '--name', 'babybot',
        'app/main.py',
        '--add-data', 'app/interpreter;interpreter',
        '--add-data', 'app/mylogger;mylogger',
        '--add-data', 'app/static;static',
        '--hidden-import', 'pyautogui',
        '--hidden-import', 'colorama',
        '--hidden-import', 'winshell',
        '--hidden-import', 'opencv-python',
        '--hidden-import', 'Pillow',
        '--hidden-import', 'pandas',
        '--hidden-import', 'numpy',
        '--hidden-import', 'pandas',
    ]

    try:
        # Ejecutar el comando
        subprocess.run(command, check=True)
        print("Everything is ok.")
    except subprocess.CalledProcessError as e:
        print(f"Error  while compiling: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

