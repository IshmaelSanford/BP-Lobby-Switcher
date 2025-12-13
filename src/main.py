from nicegui import ui, app
import sys
import os
import keyboard
import pyautogui
import asyncio
import logging
from utils.resource_path import resource_path
from ui.layout import main_layout
from ui.theme import load_theme
from version import APP_VERSION
from ui.components.updater_ui import show_update_dialog

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cleanup old updates
if getattr(sys, 'frozen', False):
    exe_path = sys.executable
    old_exe = f"{exe_path}.old"
    if os.path.exists(old_exe):
        try:
            os.remove(old_exe)
            logging.info(f"Removed old executable: {old_exe}")
        except Exception as e:
            logging.warning(f"Failed to remove old executable: {e}")

# Serve assets
if getattr(sys, 'frozen', False):
    assets_path = resource_path('assets')
else:
    assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

if not os.path.exists(assets_path):
    # Fallback for some PyInstaller configurations where assets might be at root
    if getattr(sys, 'frozen', False) and os.path.exists(os.path.join(sys._MEIPASS, 'assets')):
        assets_path = os.path.join(sys._MEIPASS, 'assets')
    else:
        print(f"Warning: Assets path not found at {assets_path}")

app.add_static_files('/assets', assets_path)

# Login Page
@ui.page('/')
def login_page():
    load_theme()
    # Dark Theme Login (using theme variables)
    ui.query('body').classes('bg-[var(--clr-surface-a0)]')
    
    with ui.card().classes('absolute-center w-80 p-8 items-center bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)] shadow-xl'):
        # Logo
        ui.image('/assets/v-logo.png').classes('w-24 h-24 mb-6 opacity-90 hover:opacity-100 transition-opacity')
            
        ui.label('BP Lobby Switcher').classes('text-xl font-bold mb-6 text-[var(--clr-light-a0)] tracking-wide')
        
        username = ui.input('Username').props('outlined').classes('w-full text-[var(--clr-light-a0)] mb-2')
        password = ui.input('Password', password=True).props('outlined').classes('w-full mb-6 text-[var(--clr-light-a0)]')
        
        def try_login():
            if username.value == 'admin' and password.value == 'password':
                ui.navigate.to('/home')
            else:
                ui.notify('Invalid credentials', color='negative', position='top')

        # Add Enter key support
        username.on('keydown.enter', try_login)
        password.on('keydown.enter', try_login)

        ui.button('LOGIN', on_click=try_login).props('color=cyan').classes('w-full font-bold shadow-lg')

    # Check for updates on page load
    ui.timer(0.5, lambda: show_update_dialog(manual_check=False), once=True)

# Main App Page
@ui.page('/home')
def home():
    load_theme()
    main_layout()

# Visibility Toggle Logic
is_visible = True
def toggle_visibility():
    global is_visible
    try:
        if app.native.main_window:
            if is_visible:
                app.native.main_window.hide()
                is_visible = False
            else:
                app.native.main_window.show()
                is_visible = True
    except Exception as e:
        print(f"Visibility toggle error: {e}")

# Register Hotkey
# Note: This runs globally. Ensure it doesn't conflict.
try:
    keyboard.add_hotkey('right shift', toggle_visibility)
except:
    pass

# Run App
if __name__ in {"__main__", "__mp_main__"}:
    # Get icon path
    icon_path = resource_path(os.path.join('assets', 'v-logo.png'))
    if not os.path.exists(icon_path):
        icon_path = None 

    async def center_window():
        try:
            # Small delay to ensure window is created
            await asyncio.sleep(0.1)
            if app.native.main_window:
                screen_width, screen_height = pyautogui.size()
                window_width, window_height = 1000, 700
                x = (screen_width - window_width) // 2
                y = (screen_height - window_height) // 2
                app.native.main_window.move(x, y)
                
                # Set minimum size
                # Note: This attempts to set the min_size property on the pywebview window
                try:
                    app.native.main_window.min_size = (778, 500)
                except:
                    pass
        except Exception as e:
            print(f"Could not center window: {e}")

    app.on_startup(center_window)

    # Set minimum window size configuration for pywebview
    if hasattr(app, 'native'):
        app.native.window_args['min_size'] = (778, 500)

    ui.run(
        title=f'BP Lobby Switcher {APP_VERSION}',
        native=True,
        window_size=(1000, 700),
        favicon=icon_path,
        reload=False,
        dark=True # Force dark mode preference
    )
