import pyautogui
import pydirectinput
import time
import logging
import os
import threading
import random
from utils.image_search import find_image_on_screen
from utils.resource_path import resource_path
from utils.window_detection import get_game_window

class SurfMacro:
    def __init__(self):
        self.is_running = False
        self.assets_dir = resource_path('assets')
        # Subdirectory 'roblox' and file 'surf.png'
        self.image_rel_path = os.path.join('roblox', 'surf.png')
        
        # Worker thread for non-blocking execution
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def start(self):
        if not self.is_running:
            self.is_running = True
            logging.info("Surf Macro started.")

    def stop(self):
        if self.is_running:
            self.is_running = False
            logging.info("Surf Macro stopped.")

    def _worker_loop(self):
        """Runs in a separate thread to prevent UI blocking."""
        while True:
            if self.is_running:
                try:
                    self._execute_logic()
                except Exception as e:
                    logging.error(f"Error in surf macro: {e}")
                time.sleep(0.1) # Check more frequently for faster reaction
            else:
                time.sleep(0.5)

    def _execute_logic(self):
        image_path = os.path.join(self.assets_dir, self.image_rel_path)
        
        # Lower confidence to account for partial occlusion
        coords = find_image_on_screen(image_path, confidence=0.6)
        
        if coords:
            # Ensure window is focused
            try:
                window = get_game_window(["Roblox", "Blue Protocol"])
                if window and not window.isActive:
                    window.activate()
                    time.sleep(0.1)
            except Exception as e:
                logging.warning(f"Could not activate window: {e}")

            logging.info(f"Surf image found at {coords}. Clicking...")
            
            # Convert tuple to int coordinates
            x, y = int(coords[0]), int(coords[1])

            # Move mouse naturally using pyautogui (smoother)
            pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.4))
            
            # Click strategy: multiple methods to ensure registration
            # 1. pydirectinput standard click (often most reliable for Roblox)
            pydirectinput.click(x=x, y=y)
            time.sleep(0.05)
            
            # 2. explicit down/up if single click failed
            pydirectinput.mouseDown(x=x, y=y)
            time.sleep(random.uniform(0.1, 0.2)) 
            pydirectinput.mouseUp(x=x, y=y)

            # Retry logic: If image persists, click nearby (radius 5-10px) until gone or max retries
            max_retries = 10
            for i in range(max_retries):
                # Check cancellation
                if not self.is_running:
                    return

                time.sleep(random.uniform(0.3, 0.5)) # Variable pause
                
                # Check if image is still there
                if not find_image_on_screen(image_path, confidence=0.6):
                    break # Successfully clicked away
                
                # Apply random offset (radius 5-10 pixels)
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                
                target_x = x + offset_x
                target_y = y + offset_y
                
                logging.info(f"Image persistent. Retry {i+1}/{max_retries} at offset ({offset_x}, {offset_y})")
                
                # Small jitter move
                pyautogui.moveTo(target_x, target_y, duration=random.uniform(0.1, 0.2))
                
                # Aggressive retry click
                pydirectinput.click(x=target_x, y=target_y)
                time.sleep(0.05)
                pydirectinput.mouseDown(x=target_x, y=target_y)
                time.sleep(random.uniform(0.08, 0.15))
                pydirectinput.mouseUp(x=target_x, y=target_y)
            
            time.sleep(1.0) # Cooldown before next major scan cycle
