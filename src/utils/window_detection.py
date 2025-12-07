import pygetwindow as gw
import logging

def is_game_running(window_titles=["Blue Protocol: Star Resonance"], process_names=["BPSR_STEAM.exe"]):
    """
    Checks if the game is running by looking for window titles.
    Note: pygetwindow works with window titles. Process name checking would require psutil, 
    but for now we will stick to window titles as pygetwindow is simpler for this scope.
    If process checking is strictly required, we can add psutil.
    """
    windows = gw.getAllTitles()
    for title in windows:
        for target_title in window_titles:
            if target_title.lower() in title.lower():
                return True
    
    # Note: pygetwindow doesn't check process names directly. 
    # If we need to check BPSR_STEAM.exe specifically without a window title match, 
    # we would need the 'psutil' library.
    # For now, we assume the window title is sufficient as requested.
    return False

def get_game_window(window_titles=["Blue Protocol: Star Resonance"]):
    windows = gw.getWindowsWithTitle('')
    for window in windows:
        for target_title in window_titles:
            if target_title.lower() in window.title.lower():
                return window
    return None
