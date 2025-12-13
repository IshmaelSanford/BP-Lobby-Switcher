from nicegui import ui
from ui.pages.lobby import lobby_page
from ui.pages.settings import settings_page
from ui.components.logger import LogView

def main_layout():
    # Main Container with background - Flex Column, Full Height, No Scroll
    with ui.column().classes('w-full h-screen p-0 gap-0 bg-[var(--clr-surface-a0)] text-[var(--clr-light-a0)] relative overflow-hidden flex flex-col'):
        
        # Navigation Bar (Top) - Fixed Height
        with ui.row().classes('w-full h-14 flex-none items-center justify-between bg-[var(--clr-surface-a10)] border-b border-[var(--clr-surface-a20)] z-10 p-0 m-0 gap-0'):
            # Logo / Title
            with ui.row().classes('items-center gap-3 pl-4'):
                ui.image('/assets/v-logo.png').classes('w-8 h-8 object-contain')
                ui.label('MACRO UI').classes('text-lg font-bold tracking-wider text-[var(--clr-light-a0)] hidden sm:block') # Hide text on very small screens

            # Navigation Tabs
            with ui.tabs().classes('bg-transparent text-[var(--clr-surface-a50)] pr-4') \
                .props('indicator-color=purple active-color=purple dense') as tabs:
                lobby_tab = ui.tab('LOBBY')
                logs_tab = ui.tab('CONSOLE')
                settings_tab = ui.tab('SETTINGS')

        # Content Area (Scrollable) - Flex Grow
        # The tab panels container takes remaining space.
        # Each panel handles its own scrolling if needed.
        with ui.tab_panels(tabs, value=lobby_tab).classes('w-full flex-1 h-full bg-transparent p-0 overflow-hidden'):
            
            # Lobby Page - Handles its own layout/scrolling
            with ui.tab_panel(lobby_tab).classes('w-full h-full p-0 overflow-y-auto pb-48'): # pb-48 for floating panel space
                lobby_page()
            
            # Logs Page
            with ui.tab_panel(logs_tab).classes('w-full h-full p-0 overflow-hidden'):
                with ui.column().classes('w-full h-full p-4 pb-48'):
                    LogView().render()
            
            # Settings Page
            with ui.tab_panel(settings_tab).classes('w-full h-full p-0 overflow-y-auto pb-48'):
                settings_page()

        # Floating Bottom Panel - Compact
        with ui.row().classes('absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)] rounded-full px-6 py-3 shadow-[0_10px_40px_rgba(0,0,0,0.5)] backdrop-blur-md items-center gap-6 z-20 glass-panel max-w-[90vw] overflow-hidden'):
            
            # Search Dialog
            with ui.dialog() as search_dialog, ui.card().classes('w-96 max-w-[90vw] bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)]'):
                ui.label('Search').classes('text-lg font-bold mb-2 text-[var(--clr-light-a0)]')
                search_input = ui.input(placeholder='Type to search...').props('autofocus outlined rounded dense').classes('w-full text-[var(--clr-light-a0)]')
                
                def perform_search():
                    query = search_input.value.lower()
                    if 'setting' in query or 'dark' in query or 'light' in query:
                        tabs.set_value(settings_tab)
                        ui.notify('Navigated to Settings', color='positive')
                    elif 'log' in query or 'console' in query:
                        tabs.set_value(logs_tab)
                        ui.notify('Navigated to Console', color='positive')
                    elif 'lobby' in query or 'macro' in query or 'start' in query:
                        tabs.set_value(lobby_tab)
                        ui.notify('Navigated to Lobby', color='positive')
                    else:
                        ui.notify(f'No results for: {query}', color='warning')
                    search_dialog.close()

                # Search on Enter
                search_input.on('keydown.enter', perform_search)

                with ui.row().classes('w-full justify-end mt-4 gap-2'):
                    ui.button('Cancel', on_click=search_dialog.close).props('flat color=grey')
                    ui.button('Search', on_click=perform_search).props('unelevated color=purple')

            # Search Trigger
            with ui.row().classes('items-center gap-2 cursor-pointer hover:text-[var(--clr-primary-a30)] transition-colors w-48').on('click', search_dialog.open):
                ui.icon('search', size='1.2rem').classes('text-[var(--clr-surface-a50)]')
                ui.label('Search...').classes('text-sm font-medium text-[var(--clr-surface-a40)]')
            
            ui.separator().props('vertical').classes('h-4 bg-[var(--clr-surface-a30)]')
            
            # Account Trigger
            with ui.row().classes('items-center gap-3 cursor-pointer group relative'):
                ui.element('div').classes('w-8 h-8 rounded-full bg-gradient-to-tr from-[var(--clr-primary-a30)] to-[var(--clr-secondary-a30)] shadow-lg flex-shrink-0')
                with ui.column().classes('gap-0'):
                    ui.label('Admin').classes('text-xs font-bold text-[var(--clr-light-a0)] group-hover:text-[var(--clr-primary-a30)] transition-colors')
                    ui.label('Pro Plan').classes('text-[10px] font-medium text-[var(--clr-surface-a50)]')
                
                # Profile Menu
                with ui.menu().classes('bg-[var(--clr-surface-a10)] border border-[var(--clr-surface-a20)]'):
                    ui.menu_item('Account Settings', on_click=lambda: tabs.set_value(settings_tab)).classes('text-[var(--clr-light-a0)] hover:bg-[var(--clr-surface-a20)]')
                    ui.separator().classes('bg-[var(--clr-surface-a20)]')
                    ui.menu_item('Log Out', on_click=lambda: ui.navigate.to('/')).classes('text-red-400 hover:bg-[var(--clr-surface-a20)]')

    # Debug Resolution Overlay
    ui.add_body_html('''
        <div id="debug-res" style="position: fixed; bottom: 5px; left: 5px; color: lime; font-family: monospace; font-size: 10px; z-index: 9999; pointer-events: none; opacity: 0.7;"></div>
        <script>
            function updateRes() {
                const el = document.getElementById("debug-res");
                if(el) el.innerText = window.outerWidth + "x" + window.outerHeight;
                
                // Enforce minimum window size (778x500)
                let w = window.outerWidth;
                let h = window.outerHeight;
                let changed = false;
                
                if (w < 778) { w = 778; changed = true; }
                if (h < 500) { h = 500; changed = true; }
                
                if (changed) {
                    window.resizeTo(w, h);
                }
            }
            window.addEventListener("resize", updateRes);
            setInterval(updateRes, 100); // Check more frequently
        </script>
    ''')
