import pyautogui
import keyboard
import time
import logging
import os
import threading
from utils.image_search import find_image_on_screen
from utils.window_detection import get_game_window
from utils.resource_path import resource_path

class LobbyIterator:
    def __init__(self):
        self.start_lobby = 99
        self.end_lobby = 85
        self.current_lobby = 99
        self.direction = -1 # Default down
        self.trigger_key = '-' # Default key
        self.loop = False
        self.cached_coordinates = None
        self.is_running = False
        self.assets_dir = resource_path('assets')
        self.image_name = 'enter_line.png'
        
        # Worker thread for non-blocking execution
        self.trigger_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def set_config(self, start, end, keybind, loop):
        self.start_lobby = start
        self.end_lobby = end
        self.current_lobby = start
        self.loop = loop
        
        # Auto-decide direction
        if start < end:
            self.direction = 1
        else:
            self.direction = -1
            
        self.trigger_key = keybind

    def _worker_loop(self):
        """Runs in a separate thread to prevent UI blocking."""
        while True:
            self.trigger_event.wait()
            self.trigger_event.clear()
            
            if self.is_running:
                try:
                    self._execute_step_logic()
                except Exception as e:
                    logging.error(f"Error in macro step: {e}")

    def _trigger_callback(self):
        """Lightweight callback for the hotkey."""
        if self.is_running:
            self.trigger_event.set()

    def _execute_step_logic(self):
        game_window = get_game_window()
        if not game_window:
            logging.warning("Game window not found.")
            return 

        # 1. Press 'p'
        pyautogui.press('p')
        time.sleep(0.1) # Small delay

        # 2. Find coordinates if not cached
        if self.cached_coordinates is None:
            image_path = os.path.join(self.assets_dir, self.image_name)
            logging.info(f"Searching for {image_path}...")
            coords = find_image_on_screen(image_path)
            if coords:
                self.cached_coordinates = coords
                logging.info(f"Coordinates cached: {coords}")
            else:
                logging.error("Could not find enter_line.png on screen.")
                return
        
        # 3. Click coordinates
        if self.cached_coordinates:
            pyautogui.click(self.cached_coordinates)
            time.sleep(0.1)

            # 4. Enter number
            pyautogui.write(str(self.current_lobby))
            time.sleep(0.1)

            # 5. Press Enter and Verify
            self.press_enter_and_verify()
            
            # 6. Iterate
            logging.info(f"Entered lobby {self.current_lobby}")
            self.current_lobby += self.direction

            # Check bounds
            reset_needed = False
            if self.direction > 0:
                if self.current_lobby > self.end_lobby:
                    reset_needed = True
            elif self.direction < 0:
                if self.current_lobby < self.end_lobby:
                    reset_needed = True
            
            if reset_needed:
                if self.loop:
                    self.current_lobby = self.start_lobby
                    logging.info("Reached end of range, resetting to start (Looping).")
                else:
                    logging.info("Reached end of range. Stopping.")
                    self.is_running = False 
                    self.current_lobby = self.start_lobby 
                    # Note: UI won't update automatically here unless we use a callback or polling

    def press_enter_and_verify(self):
        # Look for lobby_change_1.png through lobby_change_6.png
        valid_images = []
        for i in range(1, 7):
            img_name = f'lobby_change_{i}.png'
            path = os.path.join(self.assets_dir, img_name)
            if os.path.exists(path):
                valid_images.append(path)
        
        # Fallback to original if no numbered ones found
        if not valid_images:
            path = os.path.join(self.assets_dir, 'lobby_change.png')
            if os.path.exists(path):
                valid_images.append(path)

        if not valid_images:
            logging.warning("No lobby_change images found. Skipping verification.")
            pyautogui.press('enter')
            return

        max_retries = 50 
        
        # Initial press
        pyautogui.press('enter')
        
        logging.info(f"Verifying lobby change using {len(valid_images)} images...")
        
        go_image_path = os.path.join(self.assets_dir, 'go.png')
        menu_check_image = os.path.join(self.assets_dir, self.image_name) # enter_line.png
        menu_closed_count = 0
        menu_closed_threshold = 3 

        for i in range(max_retries):
            time.sleep(0.5) 
            
            # Check if loading screen appeared
            detected = False
            for img_path in valid_images:
                if find_image_on_screen(img_path, confidence=0.6, grayscale=True):
                    logging.info(f"Lobby change detected via {os.path.basename(img_path)}.")
                    detected = True
                    break
            
            if detected:
                return
            
            # Check if menu is still open
            menu_open = False
            if os.path.exists(menu_check_image):
                if find_image_on_screen(menu_check_image, confidence=0.8):
                    menu_open = True
            
            if not menu_open:
                # Check go.png as well just in case
                if os.path.exists(go_image_path) and find_image_on_screen(go_image_path, confidence=0.8):
                    menu_open = True

            if not menu_open:
                menu_closed_count += 1
                logging.info(f"Menu not detected ({menu_closed_count}/{menu_closed_threshold})...")
                if menu_closed_count >= menu_closed_threshold:
                    logging.info("Menu assumed closed. Lobby change likely in progress or complete.")
                    return
            else:
                menu_closed_count = 0 
            
                logging.info(f"Lobby change not detected (Attempt {i+1}/{max_retries})...")
                
                if self.cached_coordinates:
                     pyautogui.click(self.cached_coordinates)
                     time.sleep(0.1)

                if os.path.exists(go_image_path):
                    go_coords = find_image_on_screen(go_image_path, confidence=0.8)
                    if go_coords:
                        logging.info("Clicking go.png...")
                        pyautogui.click(go_coords)
                    else:
                        logging.warning("go.png not found on screen, pressing Enter instead.")
                        pyautogui.press('enter')
                else:
                     logging.warning("go.png asset missing, pressing Enter instead.")
                     pyautogui.press('enter')
        
        logging.warning("Timed out waiting for lobby change.")

    def start_listening(self):
        self.is_running = True
        try:
            keyboard.remove_hotkey(self.trigger_key)
        except:
            pass
        
        keyboard.add_hotkey(self.trigger_key, self._trigger_callback)
        logging.info(f"Macro listening on {self.trigger_key}")

    def stop_listening(self):
        self.is_running = False
        try:
            keyboard.remove_hotkey(self.trigger_key)
        except:
            pass
        logging.info("Macro stopped.")
