# BP Lobby Switcher

A lightweight, automated tool for switching lobbies in Blue Protocol.

## Features
- **Modern GUI**: Built with NiceGUI for a clean, responsive interface.
- **Automated Switching**: Automatically iterates through lobby numbers.
- **Resolution Independent**: Works on any screen resolution (scales from 1440p reference).
- **Loop Mode**: Option to loop back to the start lobby after reaching the end.
- **Custom Keybinds**: Set your preferred trigger key.
- **Stealth Mode**: Toggle the UI visibility with `Right Shift`.
- **Logging**: Real-time color-coded logs.

## Installation
1. Download the latest `BP Lobby Switcher.exe` from the [Releases](https://github.com/IshmaelSanford/BP-Lobby-Switcher/releases) page.
2. Run the executable.

## Usage
1. Launch the application.
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `password`
3. Set your **Start Lobby** (e.g., 99) and **End Lobby** (e.g., 85).
4. Configure your **Keybind** (Default: `-`).
5. Click **Start Macro**.
6. In-game, press your keybind to trigger the lobby switch.
7. Press `Right Shift` to hide/show the overlay.

## Development
### Requirements
- Python 3.x
- Dependencies listed in `requirements.txt`

### Build
To build the executable locally:
```bash
pip install -r requirements.txt
python build.py
```
