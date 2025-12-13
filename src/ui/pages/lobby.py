from nicegui import ui
from state import iterator, vote_macro
import pyautogui

def lobby_page():
    # Main Container - Responsive Layout
    # Use flex-row to place items side-by-side on larger screens, wrap on smaller.
    with ui.row().classes('w-full min-h-full p-4 gap-24 items-center justify-center flex-wrap'):
        
        # Status Indicator (Large) - Now a flex item
        with ui.column().classes('items-center gap-2 mb-4 flex-shrink-0'):
            status_ring = ui.element('div').classes('w-32 h-32 rounded-full border-4 border-[var(--clr-surface-a20)] flex items-center justify-center shadow-[0_0_30px_rgba(0,0,0,0.5)] transition-all duration-500')
            with status_ring:
                status_icon = ui.icon('power_settings_new', size='4rem').classes('text-[var(--clr-surface-a40)] transition-colors duration-300')
            
            status_text = ui.label('READY').classes('text-xl font-bold text-[var(--clr-surface-a50)] tracking-widest mt-4')

        # Controls Container
        with ui.card().classes('w-full max-w-md bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)] rounded-[32px] p-6 sm:p-8 gap-6 shadow-2xl flex-shrink-0 items-center'):
            
            # Inputs
            with ui.row().classes('w-full gap-4 flex-nowrap'):
                with ui.column().classes('flex-1 gap-1 min-w-0'):
                    ui.label('START').classes('text-xs font-bold text-[var(--clr-primary-a30)] ml-2')
                    start_input = ui.number(value=99, format='%.0f').props('outlined dense rounded').classes('w-full bg-[var(--clr-surface-a0)] rounded-2xl text-center font-bold text-lg text-[var(--clr-light-a0)]')
                
                with ui.column().classes('flex-1 gap-1 min-w-0'):
                    ui.label('END').classes('text-xs font-bold text-[var(--clr-primary-a30)] ml-2')
                    end_input = ui.number(value=85, format='%.0f').props('outlined dense rounded').classes('w-full bg-[var(--clr-surface-a0)] rounded-2xl text-center font-bold text-lg text-[var(--clr-light-a0)]')

            # Keybind & Loop
            with ui.row().classes('w-full gap-4 items-center bg-[var(--clr-surface-a0)] p-3 rounded-2xl border border-[var(--clr-surface-a20)] flex-wrap sm:flex-nowrap'):
                ui.icon('keyboard', color='grey').classes('ml-2')
                keybind_input = ui.input(value='-').props('borderless dense').classes('flex-1 text-center font-mono font-bold text-[var(--clr-light-a0)] min-w-[50px]')
                ui.separator().props('vertical').classes('h-6 bg-[var(--clr-surface-a20)] hidden sm:block')
                
                with ui.row().classes('items-center ml-auto'):
                    loop_switch = ui.switch().props('color=purple keep-color').classes('mr-2')
                    ui.label('LOOP').classes('text-xs font-bold text-[var(--clr-surface-a50)] mr-2')

            # Vote Macro Toggle
            with ui.row().classes('w-full gap-4 items-center bg-[var(--clr-surface-a0)] p-3 rounded-2xl border border-[var(--clr-surface-a20)]'):
                ui.icon('how_to_vote', color='grey').classes('ml-2')
                ui.label('AUTO VOTE').classes('flex-1 font-bold text-[var(--clr-light-a0)]')
                
                def toggle_vote(e):
                    if e.value:
                        vote_macro.start()
                        ui.notify('Auto Vote Enabled', color='positive')
                    else:
                        vote_macro.stop()
                        ui.notify('Auto Vote Disabled', color='warning')

                ui.switch(on_change=toggle_vote).props('color=cyan keep-color').classes('mr-2')

            # Action Button
            def toggle_macro():
                if iterator.is_running:
                    iterator.stop_listening()
                    btn.text = 'ACTIVATE'
                    btn.props('color=purple icon=play_arrow')
                    btn.classes(replace='shadow-[0_0_20px_rgba(218,31,255,0.3)]')
                    
                    status_ring.classes(remove='border-[var(--clr-success-a10)] shadow-[0_0_50px_rgba(71,213,166,0.4)]', add='border-[var(--clr-surface-a20)]')
                    status_icon.classes(replace='text-[var(--clr-surface-a40)]')
                    status_text.text = 'READY'
                    status_text.classes(replace='text-[var(--clr-surface-a50)]')
                else:
                    try:
                        s = int(start_input.value)
                        e = int(end_input.value)
                        k = keybind_input.value
                        l = loop_switch.value
                        
                        iterator.set_config(s, e, k, l)
                        iterator.start_listening()
                        
                        btn.text = 'DEACTIVATE'
                        btn.props('color=red icon=stop')
                        btn.classes(replace='shadow-[0_0_20px_rgba(255,0,0,0.3)]')
                        
                        status_ring.classes(remove='border-[var(--clr-surface-a20)]', add='border-[var(--clr-success-a10)] shadow-[0_0_50px_rgba(71,213,166,0.4)]')
                        status_icon.classes(replace='text-[var(--clr-success-a10)]')
                        status_text.text = 'ACTIVE'
                        status_text.classes(replace='text-[var(--clr-success-a10)]')
                        
                    except Exception as e:
                        ui.notify(f'Error: {e}', color='negative')

            # Fixed width container to prevent resizing
            with ui.element('div').classes('w-[200px] h-14 flex-shrink-0 relative'):
                btn = ui.button('ACTIVATE', on_click=toggle_macro).props('color=purple icon=play_arrow unelevated no-wrap').classes('w-full h-full text-lg font-bold rounded-2xl shadow-[0_0_20px_rgba(218,31,255,0.3)] transition-all hover:scale-[1.02]').style('width: 200px !important; min-width: 200px !important; max-width: 200px !important;')
