# BP Lobby Switcher

A lightweight, automated tool for switching lobbies in Blue Protocol.

## Features
- **Automated Switching**: Automatically iterates through lobby numbers.
- **Resolution Independent**: Works on any screen resolution (scales from 1440p reference).
- **Loop Mode**: Option to loop back to the start lobby after reaching the end.
- **Custom Keybinds**: Set your preferred trigger key.
- **Stealth Mode**: Toggle the UI visibility with `Right Shift`.

## Installation
1. Download the latest `main.exe` from the [Releases](https://github.com/IshmaelSanford/BP-Lobby-Switcher/releases) page.
2. Run the executable.

## Usage
1. Launch the application.
2. Set your **Start Lobby** (e.g., 99) and **End Lobby** (e.g., 85).
3. Configure your **Keybind** (Default: `-`).
4. Click **Start Macro**.
5. In-game, press your keybind to trigger the lobby switch.
6. Press `Right Shift` to hide/show the overlay.

## Development
### Requirements
- Python 3.x
- Dependencies listed in `requirements.txt`

### Build
To build the executable locally:
```bash
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --icon "assets/v-logo.png" --add-data "assets;assets" src/main.py
```
