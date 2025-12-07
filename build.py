import os
import nicegui
import subprocess
import sys
from pathlib import Path

# Get NiceGUI path
nicegui_path = Path(nicegui.__file__).parent
print(f"NiceGUI Path: {nicegui_path}")

# Assets path
assets_path = "assets"

# PyInstaller command
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name", "BP Lobby Switcher",
    "--icon", "assets/v-logo.png",
    f"--add-data={nicegui_path}{os.pathsep}nicegui",
    f"--add-data={assets_path}{os.pathsep}assets",
    "src/main.py"
]

print("Running command:")
print(" ".join(cmd))

subprocess.run(cmd, check=True)
