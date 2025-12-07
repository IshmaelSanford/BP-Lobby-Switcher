from nicegui import ui
import logging

class NiceGuiLogHandler(logging.Handler):
    def __init__(self, container):
        super().__init__()
        self.container = container

    def emit(self, record):
        msg = self.format(record)
        # Use theme colors instead of hardcoded tailwind colors
        color = 'text-[var(--clr-surface-a60)]' # Default gray
        if record.levelno >= logging.ERROR:
            color = 'text-[var(--clr-danger-a10)]'
        elif record.levelno >= logging.WARNING:
            color = 'text-[var(--clr-warning-a10)]'
        elif record.levelno >= logging.INFO:
            color = 'text-[var(--clr-success-a10)]'
        
        def append():
            if self.container:
                with self.container:
                    ui.label(msg).classes(f'{color} font-mono text-xs')
                self.container.scroll_to(percent=1.0)
        
        # Run on UI thread
        append()

class LogView:
    def __init__(self):
        self.container = None

    def render(self):
        # Use theme variables for background and border
        with ui.column().classes('w-full h-full bg-[var(--clr-surface-a0)] rounded-lg p-2 border border-[var(--clr-surface-a20)]'):
            self.container = ui.scroll_area().classes('w-full h-full')
            
            # Setup Logging
            handler = NiceGuiLogHandler(self.container)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
            logger = logging.getLogger()
            logger.setLevel(logging.INFO) # Ensure INFO logs are captured
            
            # Avoid adding multiple handlers if re-rendering
            if not any(isinstance(h, NiceGuiLogHandler) for h in logger.handlers):
                logger.addHandler(handler)
                
            # Test log
            logger.info("Console initialized.")
