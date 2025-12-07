import tkinter as tk
from tkinter import ttk, scrolledtext
import keyboard
import threading
import logging
import sys
import os
import pyautogui
from utils.resource_path import resource_path

# Add src to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from macros.lobby_iterator import LobbyIterator

class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

class LobbyIteratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lobby Iterator")
        self.root.geometry("400x450") # Increased size for log
        self.root.attributes("-topmost", True) # Keep on top
        
        # Set Icon
        try:
            icon_path = resource_path(os.path.join('assets', 'v-logo.png'))
            if os.path.exists(icon_path):
                # Tkinter expects .ico for iconbitmap on Windows usually, but PhotoImage works for iconphoto
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, icon)
        except Exception as e:
            print(f"Failed to load icon: {e}")

        self.iterator = LobbyIterator()
        self.is_visible = True
        
        # Styles
        style = ttk.Style()
        style.configure("TLabel", padding=5)
        style.configure("TButton", padding=5)
        
        # UI Elements
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Start Lobby
        ttk.Label(main_frame, text="Start Lobby:").grid(row=0, column=0, sticky=tk.W)
        self.start_var = tk.StringVar(value="99")
        ttk.Entry(main_frame, textvariable=self.start_var, width=10).grid(row=0, column=1)
        
        # End Lobby
        ttk.Label(main_frame, text="End Lobby:").grid(row=1, column=0, sticky=tk.W)
        self.end_var = tk.StringVar(value="85")
        ttk.Entry(main_frame, textvariable=self.end_var, width=10).grid(row=1, column=1)
        
        # Keybind
        ttk.Label(main_frame, text="Keybind:").grid(row=2, column=0, sticky=tk.W)
        self.keybind_var = tk.StringVar(value="-")
        ttk.Entry(main_frame, textvariable=self.keybind_var, width=10).grid(row=2, column=1)
        
        # Loop
        self.loop_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, text="Loop", variable=self.loop_var).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Start/Stop Button
        self.toggle_btn = ttk.Button(main_frame, text="Start Macro", command=self.toggle_macro)
        self.toggle_btn.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=2)

        # Log Window
        ttk.Label(main_frame, text="Logs:").grid(row=6, column=0, sticky=tk.W, pady=(10,0))
        self.log_text = scrolledtext.ScrolledText(main_frame, state='disabled', height=8)
        self.log_text.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Configure Logging
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        # Remove existing handlers to avoid duplicates if re-run
        for h in logger.handlers[:]:
            logger.removeHandler(h)
        logger.addHandler(text_handler)
        # Also log to console for debug
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

        # Log Resolution
        width, height = pyautogui.size()
        logging.info(f"Native Resolution Detected: {width}x{height}")
        
        # Global Hotkey for Visibility
        keyboard.add_hotkey('right shift', self.toggle_visibility)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_macro(self):
        if self.iterator.is_running:
            self.iterator.stop_listening()
            self.toggle_btn.config(text="Start Macro")
            self.status_label.config(text="Status: Stopped", foreground="red")
        else:
            try:
                start = int(self.start_var.get())
                end = int(self.end_var.get())
                keybind = self.keybind_var.get()
                loop = self.loop_var.get()
                
                self.iterator.set_config(start, end, keybind, loop)
                self.iterator.start_listening()
                
                self.toggle_btn.config(text="Stop Macro")
                self.status_label.config(text="Status: Running", foreground="green")
            except ValueError:
                self.status_label.config(text="Error: Invalid Numbers", foreground="red")

    def toggle_visibility(self):
        # Must be run on main thread
        self.root.after(0, self._toggle_visibility_safe)

    def _toggle_visibility_safe(self):
        if self.is_visible:
            self.root.withdraw()
            self.is_visible = False
        else:
            self.root.deiconify()
            self.is_visible = True

    def on_close(self):
        self.iterator.stop_listening()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = LobbyIteratorApp(root)
    root.mainloop()
