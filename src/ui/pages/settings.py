from nicegui import ui
from ui.components.updater_ui import show_update_dialog
from version import APP_VERSION

def settings_page():
    with ui.column().classes('w-full h-full p-6 gap-6'):
        ui.label('Settings').classes('text-3xl font-bold text-[var(--clr-primary-a10)]')
        
        with ui.card().classes('w-full bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)] rounded-[24px] p-6 shadow-lg'):
            ui.label('Application').classes('text-lg font-bold text-[var(--clr-surface-a60)] mb-4')
            
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Dark Mode').classes('text-[var(--clr-light-a0)]')
                
                def toggle_dark_mode(e):
                    if e.value:
                        ui.query('body').classes(remove='light-mode')
                    else:
                        ui.query('body').classes(add='light-mode')

                # Default to True (Dark Mode)
                ui.switch(value=True, on_change=toggle_dark_mode).props('color=purple').classes('text-[var(--clr-primary-a20)]')
            
            ui.separator().classes('bg-[var(--clr-surface-a20)] my-4')
            
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Notifications').classes('text-[var(--clr-light-a0)]')
                ui.switch(value=True).props('color=purple')

        with ui.card().classes('w-full bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)] rounded-[24px] p-6 shadow-lg'):
            ui.label('Updates').classes('text-lg font-bold text-[var(--clr-surface-a60)] mb-4')
            
            with ui.row().classes('w-full justify-between items-center'):
                with ui.column().classes('gap-0'):
                    ui.label('Current Version').classes('text-[var(--clr-light-a0)]')
                    ui.label(f'v{APP_VERSION}').classes('text-xs text-[var(--clr-surface-a50)]')
                
                ui.button('Check for Updates', on_click=lambda: show_update_dialog(manual_check=True)).props('color=purple icon=update')

        with ui.card().classes('w-full bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)] rounded-[24px] p-6 shadow-lg'):
            ui.label('Account').classes('text-lg font-bold text-[var(--clr-surface-a60)] mb-4')
            
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.avatar('person', color='grey-9', text_color='white')
                    with ui.column().classes('gap-0'):
                        ui.label('Admin User').classes('font-bold text-[var(--clr-light-a0)]')
                        ui.label('admin@gmail.com').classes('text-xs text-[var(--clr-surface-a50)]')
                
                ui.button('Log Out', on_click=lambda: ui.navigate.to('/')).props('flat color=red icon=logout').classes('font-bold')

        # Spacer for floating dock
        ui.element('div').classes('w-full h-64')
