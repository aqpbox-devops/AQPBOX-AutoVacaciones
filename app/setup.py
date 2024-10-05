from cx_Freeze import setup, Executable

setup(
    name = "babybot",
    version = "1.0",
    description = "Vacations Bot",
    executables = [Executable("app/main.py")]
)
