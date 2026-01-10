import tkinter as tk
import multiprocessing
import logging
import os
import time
import ctypes
import pyautogui
from PIL import Image
try:
    import pytesseract
    # Attempt to locate tesseract executable on Windows if not in PATH
    if os.name == 'nt':
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.join(os.getenv('LOCALAPPDATA', ''), r"Tesseract-OCR\tesseract.exe"),
            os.path.join(os.getenv('LOCALAPPDATA', ''), r"Programs\Tesseract-OCR\tesseract.exe")
        ]
        
        # Check if tesseract is already in path
        import shutil
        if not shutil.which("tesseract"):
            for p in possible_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    logging.info(f"Found Tesseract at {p}")
                    break
except ImportError:
    pytesseract = None

from utils.image_search import find_image_box, find_image_on_screen
from utils.resource_path import resource_path

def _show_overlay_func():
    try:
        root = tk.Tk()
        root.title("MAX DREAMSTONE ALERT")
        
        # Remove window decorations and make topmost
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        
        # Transparent background setup
        # Windows supports transparent color key
        bg_color = 'black'
        root.wm_attributes('-transparentcolor', bg_color)
        root.configure(bg=bg_color)
        
        # Current screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Visual Config
        text_str = "MAX DREAMSTONE"
        font_spec = ("Arial", 72, "bold")
        text_color = "#FF5555"
        
        # Use Canvas for better layering and transparency handling
        canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg=bg_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Center coordinates
        cx = screen_width * 0.5
        cy = screen_height * 0.3
        
        # Tag for all items to control visibility easily
        tag_name = "alert_text"

        # Main Text
        canvas.create_text(
            cx, cy, 
            text=text_str, font=font_spec, fill=text_color,
            tags=tag_name
        )
        
        # Force window creation so HWND is valid
        root.update()

        # Make click-through and No-Activate (Windows only)
        try:
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            if hwnd == 0:
                hwnd = root.winfo_id()
             
            # Styles
            WS_EX_TRANSPARENT = 0x00000020 # Click-through
            WS_EX_LAYERED     = 0x00080000 # Transparency support
            WS_EX_TOPMOST     = 0x00000008 # Always on top
            WS_EX_NOACTIVATE  = 0x08000000 # Don't take focus (Keyboard/Input)
            WS_EX_TOOLWINDOW  = 0x00000080 # Hide from taskbar (optional but good)
            
            new_style = WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
            
            # Get current style
            ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, ex_style | new_style)
            
        except Exception as e:
            print(f"Could not set window styles: {e}")

        # Flashing Logic
        flash_count = 0
        max_flashes = 3

        def show_text():
            canvas.itemconfigure(tag_name, state='normal')

        def hide_text():
            canvas.itemconfigure(tag_name, state='hidden')

        def close_overlay():
            root.destroy()

        def final_show():
            show_text()
            root.after(3000, close_overlay)

        def flash_off():
            nonlocal flash_count
            hide_text()
            if flash_count < max_flashes:
                 root.after(300, flash_on)
            else:
                final_show()

        def flash_on():
            nonlocal flash_count
            show_text()
            flash_count += 1
            root.after(300, flash_off)

        # Start sequence
        flash_on()
        
        # Run the tkinter loop
        root.mainloop()
        
        # Flashing Logic
        flash_count = 0
        max_flashes = 3
        # Total time to show after flashing: 3 seconds
        # Flash cycle: On (300ms) -> Off (300ms) -> On...
        
        def close_overlay():
            root.destroy()

        def final_show():
            # Show steady for 3 seconds
            label.place(relx=0.5, rely=0.3, anchor="center")
            root.after(3000, close_overlay)

        def flash_off():
            nonlocal flash_count
            label.place_forget() # Hide
            if flash_count < max_flashes:
                 root.after(300, flash_on)
            else:
                final_show()

        def flash_on():
            nonlocal flash_count
            label.place(relx=0.5, rely=0.3, anchor="center") # Show
            flash_count += 1
            root.after(300, flash_off)

        # Start sequence
        flash_on()
        
        # Run the tkinter loop
        root.mainloop()
    except Exception as e:
        print(f"Overlay process error: {e}")

class DreamstoneMonitor:
    def __init__(self):
        self.enabled = False # User togglable
        self._overlay_process = None
        self._last_log_value = None # Track last logged value
        self.ocr_missing_logged = False
        # Path to the reference image
        self.image_path = resource_path(os.path.join('assets', '999.png'))

    def check(self):
        """
        Called periodically. Checks if image is on screen.
        If found, reads the number using OCR.
        """
        if not self.enabled:
            return

        # Don't trigger if overlay is already active
        if self._overlay_process and self._overlay_process.is_alive():
            return

        try:
            # 1. ATTEMPT SCAN
            # Strategy: Try OCR first if enabled/installed. If that fails (or not installed), fallback to high-precision image match.
            
            ocr_success = False
            
            # Use a broader search for OCR box finding (confidence 0.8)
            # This allows finding the region even if the numbers are different (e.g. 499)
            if pytesseract:
                try:
                    box = find_image_box(self.image_path, confidence=0.8)
                    if box:
                        # Perform OCR
                        left, top, width, height = box
                        screenshot = pyautogui.screenshot(region=(int(left), int(top), int(width), int(height)))
                        screenshot = screenshot.convert('L') # Grayscale
                        
                        # Use tesseract to find digits
                        text = pytesseract.image_to_string(screenshot, config='--psm 7 outputbase digits')
                        clean_text = "".join(filter(str.isdigit, text))
                        
                        if clean_text:
                            value = int(clean_text)
                            ocr_success = True 
                            
                            if value != self._last_log_value:
                                logging.info(f"Dreamstone OCR Detected Change: {value}")
                                self._last_log_value = value
                            
                            if value >= 900:
                                logging.info(f"Dreamstone condition met (Value: {value}). Triggering overlay.")
                                self.trigger_overlay()
                                return # Done
                except pytesseract.pytesseract.TesseractNotFoundError:
                    if not self.ocr_missing_logged:
                        logging.warning("Tesseract not found. Falling back to strict image matching.")
                        self.ocr_missing_logged = True
                    # Set pytesseract to None to skip future specific OCR tries effectively
                    # (We don't remove the global import but we know it failed)
                    pass
                except Exception as e:
                    logging.error(f"OCR specific error: {e}")

            # 2. FALLBACK: Strict Image Matching
            # If OCR didn't run or didn't find anything, but we still might have a match.
            # Only use this if OCR failed/wasn't used.
            if not ocr_success:
                # Use very high confidence (0.98) to ensure it is EXACTLY "999" and not "499"
                # This assumes "999.png" is the image of the number "999"
                pos = find_image_on_screen(self.image_path, confidence=0.98)
                if pos:
                    logging.info("Dreamstone condition met (Strict Image Match 0.98). Triggering overlay.")
                    self.trigger_overlay()

        except Exception as e:
            logging.error(f"Error in Dreamstone check: {e}")

    def trigger_overlay(self):
        # Spawn independent process
        self._overlay_process = multiprocessing.Process(target=_show_overlay_func)
        self._overlay_process.daemon = True # Kill if main app dies
        self._overlay_process.start()
