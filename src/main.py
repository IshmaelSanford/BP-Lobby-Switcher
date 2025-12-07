from nicegui import ui, app
import logging
import sys
import os
import pyautogui
from utils.resource_path import resource_path

# Add src to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from macros.lobby_iterator import LobbyIterator

# Initialize Iterator
iterator = LobbyIterator()

# Custom Log Handler
class NiceGuiLogHandler(logging.Handler):
    def __init__(self, container):
        super().__init__()
        self.container = container

    def emit(self, record):
        msg = self.format(record)
        color = 'text-gray-800'
        if record.levelno >= logging.ERROR:
            color = 'text-red-500'
        elif record.levelno >= logging.WARNING:
            color = 'text-orange-500'
        elif record.levelno >= logging.INFO:
            color = 'text-green-600'
        
        # Schedule UI update
        def append():
            with self.container:
                ui.label(msg).classes(f'{color} text-xs font-mono')
            self.container.scroll_to(percent=1.0)
        
        try:
            append()
        except:
            pass 

# Login Page
@ui.page('/')
def login_page():
    ui.colors(primary='#5898d4')
    
    with ui.card().classes('absolute-center w-80 p-8 items-center'):
        # Logo
        try:
            logo_path = resource_path(os.path.join('assets', 'v-logo.png'))
            if os.path.exists(logo_path):
                ui.image(logo_path).classes('w-24 h-24 mb-4')
        except:
            pass
            
        ui.label('BP Lobby Switcher').classes('text-xl font-bold mb-6')
        
        username = ui.input('Username').classes('w-full')
        password = ui.input('Password', password=True).classes('w-full mb-4')
        
        def try_login():
            if username.value == 'admin' and password.value == 'password':
                ui.navigate.to('/home')
            else:
                ui.notify('Invalid credentials (try admin/password)', color='negative')

        ui.button('Login', on_click=try_login).classes('w-full')

# Main App Page
@ui.page('/home')
def home_page():
    ui.colors(primary='#5898d4')
    
    # Container
    with ui.column().classes('w-full h-full p-4 items-center gap-4'):
        # Header
        with ui.row().classes('w-full items-center justify-between'):
            with ui.row().classes('items-center gap-2'):
                try:
                    logo_path = resource_path(os.path.join('assets', 'v-logo.png'))
                    if os.path.exists(logo_path):
                        ui.image(logo_path).classes('w-8 h-8')
                except:
                    pass
                ui.label('Lobby Switcher').classes('text-lg font-bold')
            
            # Resolution Info
            w, h = pyautogui.size()
            ui.label(f'Res: {w}x{h}').classes('text-xs text-gray-500')

        ui.separator()

        # Controls
        with ui.card().classes('w-full p-4 gap-4'):
            with ui.grid(columns=2).classes('w-full gap-4'):
                start_input = ui.number('Start Lobby', value=99, format='%.0f').classes('w-full')
                end_input = ui.number('End Lobby', value=85, format='%.0f').classes('w-full')
            
            keybind_input = ui.input('Keybind', value='-').classes('w-full')
            loop_switch = ui.switch('Loop Mode').classes('w-full')
            
            status_label = ui.label('Status: Stopped').classes('text-red-500 font-bold self-center')
            
            def toggle_macro():
                if iterator.is_running:
                    iterator.stop_listening()
                    btn.text = 'Start Macro'
                    btn.props('color=primary')
                    status_label.text = 'Status: Stopped'
                    status_label.classes(replace='text-red-500')
                else:
                    try:
                        s = int(start_input.value)
                        e = int(end_input.value)
                        k = keybind_input.value
                        l = loop_switch.value
                        
                        iterator.set_config(s, e, k, l)
                        iterator.start_listening()
                        
                        btn.text = 'Stop Macro'
                        btn.props('color=negative')
                        status_label.text = 'Status: Running'
                        status_label.classes(replace='text-green-500')
                    except Exception as e:
                        ui.notify(f'Error: {e}', color='negative')

            btn = ui.button('Start Macro', on_click=toggle_macro).classes('w-full')

        # Logs
        ui.label('Logs').classes('text-sm font-bold self-start mt-2')
        log_container = ui.scroll_area().classes('w-full h-48 border rounded p-2 bg-gray-50')
        
        # Setup Logging
        handler = NiceGuiLogHandler(log_container)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        # Clear existing handlers to avoid duplicates
        for h in logger.handlers[:]:
            logger.removeHandler(h)
        logger.addHandler(handler)
        
        # Also log to console
        console = logging.StreamHandler()
        logger.addHandler(console)

        logging.info(f"App started. Native Resolution: {w}x{h}")

# Run App
if __name__ in {"__main__", "__mp_main__"}:
    # Get icon path
    icon_path = resource_path(os.path.join('assets', 'v-logo.png'))
    if not os.path.exists(icon_path):
        icon_path = None # Fallback

    ui.run(
        title='BP Lobby Switcher',
        native=True,
        window_size=(400, 650),
        favicon=icon_path,
        reload=False # Disable reload for production/exe
    )
