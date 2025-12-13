import pyautogui
import time
import logging
import os
import json
import keyboard
import threading
from utils.resource_path import resource_path
from utils.image_search import find_image_on_screen

class ClassSwitcher:
    def __init__(self):
        self.is_listening = False
        self.hotkey = None
        self.current_class = None
        self.desired_class = None
        self.is_on_current_class = True # Tracks which class we are currently on
        self.assets_dir = resource_path('assets')
        self.config_file = os.path.join(self.assets_dir, 'class_switcher_config.json')
        self.coordinates = self._load_coordinates()
        self.lock = threading.Lock()

    def _load_coordinates(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load config: {e}")
                return {}
        return {}

    def _save_coordinates(self, name, x, y):
        width, height = pyautogui.size()
        ratio_x = x / width
        ratio_y = y / height
        self.coordinates[name] = {'x': ratio_x, 'y': ratio_y}
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.coordinates, f)
            logging.info(f"Saved coordinates for {name}: {ratio_x:.4f}, {ratio_y:.4f}")
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def set_config(self, hotkey, current_class, desired_class):
        self.hotkey = hotkey
        self.current_class = current_class
        self.desired_class = desired_class
        self.is_on_current_class = True # Reset state when config changes

    def start_listening(self):
        if not self.is_listening and self.hotkey and self.current_class and self.desired_class:
            try:
                keyboard.add_hotkey(self.hotkey, self._run_macro)
                self.is_listening = True
                logging.info(f"Class Switcher started. Key: {self.hotkey}, Current: {self.current_class}, Desired: {self.desired_class}")
                return True
            except Exception as e:
                logging.error(f"Failed to start Class Switcher: {e}")
                return False
        return False

    def stop_listening(self):
        if self.is_listening:
            try:
                keyboard.remove_hotkey(self.hotkey)
            except:
                pass # Handle case where hotkey might not exist
            self.is_listening = False
            logging.info("Class Switcher stopped.")

    def _click_image(self, image_name, retries=3, delay=0.04, config_key=None, grayscale=True, confidence=0.7):
        image_path = os.path.join(self.assets_dir, image_name)
        
        # 1. Try to find the image
        for i in range(retries):
            coords = find_image_on_screen(image_path, confidence=confidence, grayscale=grayscale)
            if coords:
                x, y = coords
                logging.info(f"Found {image_name} at ({x}, {y}). Clicking.")
                
                # Save coordinates if config_key is provided
                if config_key:
                    self._save_coordinates(config_key, x, y)
                
                pyautogui.click(x, y)
                time.sleep(delay)
                return True
            time.sleep(0.1)
            
        # 2. If not found, check for saved coordinates (Fallback)
        if config_key and config_key in self.coordinates:
            ratio = self.coordinates[config_key]
            w, h = pyautogui.size()
            x = int(ratio['x'] * w)
            y = int(ratio['y'] * h)
            logging.info(f"Image {image_name} not found. Using saved coordinates for {config_key}: ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(delay)
            return True

        logging.warning(f"Could not find {image_name} after {retries} retries and no saved coordinates.")
        return False

    def _run_macro(self):
        if self.lock.locked():
            logging.info("Class Switcher already running.")
            return

        with self.lock:
            logging.info("Executing Class Switcher Macro...")
            
            # 0. Press Esc to ensure menus are closed or to open the main menu if that's the intent
            # User requested "click esc at the start"
            keyboard.send('esc')
            time.sleep(0.05)

            # 1. Find and click assets/profile.png
            if not self._click_image('profile.png', config_key='profile'):
                return

            # 2. Find current_class.png and click it
            # Use 'current_class' as the config key to enable fallback/saving
            if not self._click_image('current_class.png', config_key='current_class'):
                logging.error("Failed to click Current Class. If this is the first run, ensure you are on the class matching current_class.png.")
                return

            # 3. Find desired class png and click it
            # Determine which class to switch TO
            target_class = self.desired_class if self.is_on_current_class else self.current_class
            class_image = f"{target_class}.png"
            
            if not self._click_image(class_image, config_key=target_class):
                return

            # 4. Click switch_class.png
            if not self._click_image('switch_class.png', config_key='switch_class'):
                return

            # 5. Click confirm_class_switch.png TWICE
            # "maybe add really really low delay"
            if not self._click_image('confirm_class_switch.png', delay=0.04, config_key='confirm_class_switch'):
                return
            
            # Second click might need a re-search or just click again if it's the same spot?
            # Usually popups might move or it's a double confirmation. 
            # Safest is to search again.
            if not self._click_image('confirm_class_switch.png', delay=0.04, config_key='confirm_class_switch'):
                # If search fails (maybe it didn't disappear/reappear fast enough), try clicking blindly?
                # But let's assume it's findable.
                pass
            
            # If switching back to current_class, click equip_weapon.png
            if target_class == self.current_class:
                if not self._click_image('equip_weapon.png', delay=0.04, config_key='equip_weapon'):
                    logging.warning("Could not find equip_weapon.png")

            # If we reached here, the switch was likely successful
            self.is_on_current_class = not self.is_on_current_class
            logging.info(f"Switched to {target_class}. Next switch will be to {'Current' if self.is_on_current_class else 'Desired'}.")

            # 6. Click escape
            # 4 times for current class (to close equip menu), 3 times for desired class
            esc_count = 4 if target_class == self.current_class else 3
            
            for _ in range(esc_count):
                keyboard.send('esc')
                time.sleep(0.1) # Increased delay to ensure game registers the key presses

            logging.info("Class Switcher Macro finished.")
