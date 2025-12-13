import pyautogui
import time
import logging
import os
import threading
from utils.image_search import find_image_on_screen
from utils.resource_path import resource_path

class VoteMacro:
    def __init__(self):
        self.is_running = False
        self.assets_dir = resource_path('assets')
        self.image_name = 'vote_hand.png'
        
        # Worker thread for non-blocking execution
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def start(self):
        if not self.is_running:
            self.is_running = True
            logging.info("Vote Macro started.")

    def stop(self):
        if self.is_running:
            self.is_running = False
            logging.info("Vote Macro stopped.")

    def _worker_loop(self):
        """Runs in a separate thread to prevent UI blocking."""
        while True:
            if self.is_running:
                try:
                    self._execute_logic()
                except Exception as e:
                    logging.error(f"Error in vote macro: {e}")
                time.sleep(1) # Check every second
            else:
                time.sleep(0.5)

    def _execute_logic(self):
        image_path = os.path.join(self.assets_dir, self.image_name)
        # logging.info(f"Searching for {image_path}...") # Too verbose for a loop
        coords = find_image_on_screen(image_path, confidence=0.8)
        
        if coords:
            logging.info("Vote hand detected! Pressing F.")
            pyautogui.press('f')
            time.sleep(2) # Wait a bit to avoid spamming
