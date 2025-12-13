from nicegui import ui
import asyncio
import logging
import sys
from version import APP_VERSION
from utils.updater import check_for_updates, download_update, restart_and_update

async def show_update_dialog(manual_check=False):
    try:
        if manual_check:
            ui.notify('Checking for updates...', color='info')

        update_info = await asyncio.to_thread(check_for_updates)
        
        if not update_info['available']:
            if manual_check:
                ui.notify('No updates available. You are on the latest version.', color='positive')
            return

        # Update available
        with ui.dialog() as dialog, ui.card().classes('w-96 items-center bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)]'):
            ui.label('Update Available!').classes('text-xl font-bold text-purple-400')
            ui.label(f"New Version: {update_info['version']}").classes('text-gray-300')
            ui.label(f"Current: {APP_VERSION}").classes('text-gray-500 text-sm mb-4')
            
            progress_bar = ui.linear_progress(value=0).classes('w-full mb-4 hidden').props('color=purple')
            status_label = ui.label('Downloading...').classes('text-xs text-gray-400 hidden')
            
            async def start_update():
                progress_bar.classes(remove='hidden')
                status_label.classes(remove='hidden')
                download_btn.disable()
                cancel_btn.disable()
                # Prevent closing while updating
                dialog.props('persistent') 
                
                def update_progress(p):
                    progress_bar.value = p
                    
                temp_file = "update.new"
                success = await asyncio.to_thread(download_update, update_info['url'], temp_file, update_progress)
                
                if success:
                    status_label.text = 'Installing...'
                    
                    # Check if running from source
                    if not getattr(sys, 'frozen', False):
                        ui.notify('Update downloaded, but cannot self-update when running from source.', color='warning', timeout=5000)
                        status_label.text = 'Dev Mode: Cannot install.'
                        await asyncio.sleep(2)
                        dialog.props(remove='persistent')
                        cancel_btn.enable()
                        cancel_btn.text = 'Close'
                        return

                    ui.notify('Update downloaded. Restarting...', color='positive')
                    await asyncio.sleep(1)
                    restart_and_update(temp_file)
                else:
                    ui.notify('Download failed.', color='negative')
                    dialog.props(remove='persistent')
                    download_btn.enable()
                    cancel_btn.enable()

            with ui.row().classes('w-full justify-end gap-2'):
                cancel_btn = ui.button('Later', on_click=dialog.close).props('flat color=grey')
                download_btn = ui.button('Update Now', on_click=start_update).props('color=purple')
        
        dialog.open()
    except Exception as e:
        logging.error(f"Update check error: {e}")
        if manual_check:
             ui.notify(f"Error checking for updates: {e}", color='negative')
