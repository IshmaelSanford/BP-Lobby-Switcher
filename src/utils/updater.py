import requests
import sys
import os
import subprocess
import logging
from version import APP_VERSION

GITHUB_REPO = "IshmaelSanford/BP-Lobby-Switcher"

def check_for_updates():
    """
    Checks GitHub Releases for a newer version.
    Returns a dict with update info or {"available": False}.
    """
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_tag = data['tag_name']
            
            # Compare versions (assuming vX.Y.Z format)
            # This is a simple string comparison, which works for v2.0.3 vs v2.0.4
            # but might fail for v2.9 vs v2.10. Ideally use packaging.version.
            if latest_tag != APP_VERSION: 
                # Find the .exe asset
                exe_asset = next((a for a in data['assets'] if a['name'].endswith('.exe')), None)
                if exe_asset:
                    return {
                        "available": True,
                        "version": latest_tag,
                        "url": exe_asset['browser_download_url'],
                        "size": exe_asset['size']
                    }
    except Exception as e:
        logging.error(f"Update check failed: {e}")
    return {"available": False}

def download_update(url, save_path, progress_callback=None):
    """
    Downloads the file from url to save_path.
    progress_callback(float): 0.0 to 1.0
    """
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192 
        downloaded = 0
        
        with open(save_path, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
                downloaded += len(data)
                if progress_callback and total_size > 0:
                    progress_callback(downloaded / total_size)
        return True
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return False

def restart_and_update(new_exe_path):
    """
    Creates a batch script to swap the executable and restart.
    Only works if frozen (compiled).
    """
    if not getattr(sys, 'frozen', False):
        logging.warning("Cannot self-update when running from source.")
        return

    current_exe = sys.executable
    
    # Batch script to:
    # 1. Wait for this process to end
    # 2. Rename the old exe to .old (more reliable than delete)
    # 3. Move the new exe to the old location
    # 4. Start the new exe
    # 5. Delete itself
    bat_script = f"""
@echo off
timeout /t 3 /nobreak > NUL
if exist "{current_exe}.old" del "{current_exe}.old"
move /y "{current_exe}" "{current_exe}.old"
move /y "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
    bat_path = "update_installer.bat"
    with open(bat_path, "w") as f:
        f.write(bat_script)
        
    # Run the batch script detached
    subprocess.Popen(bat_path, shell=True)
    
    # Exit the application immediately
    sys.exit(0)
