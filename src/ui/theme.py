from nicegui import ui

def load_theme():
    ui.add_head_html('''
    <style>
        :root {
            /* Base colors */
            --clr-dark-a0: #000000;
            --clr-light-a0: #ffffff;

            /* Theme primary colors */
            --clr-primary-a0: #da1fff;
            --clr-primary-a10: #e14bff;
            --clr-primary-a20: #e768ff;
            --clr-primary-a30: #ed80ff;
            --clr-primary-a40: #f197ff;
            --clr-primary-a50: #f6adff;
            --clr-primary-a60: #f9c2ff;
            --clr-primary-a70: #fcd6ff;
            --clr-primary-a80: #feebff;
            --clr-primary-a90: #ffffff;

            /* Theme surface colors (Dark Mode Default) */
            --clr-surface-a0: #121212;
            --clr-surface-a10: #282828;
            --clr-surface-a20: #3f3f3f;
            --clr-surface-a30: #575757;
            --clr-surface-a40: #717171;
            --clr-surface-a50: #8b8b8b;
            --clr-surface-a60: #a7a7a7;
            --clr-surface-a70: #c4c4c4;

            /* Theme tonal surface colors */
            --clr-surface-tonal-a0: #241826;
            --clr-surface-tonal-a10: #392d3a;
            --clr-surface-tonal-a20: #4f4450;
            --clr-surface-tonal-a30: #655c67;
            --clr-surface-tonal-a40: #7d757e;
            --clr-surface-tonal-a50: #968f97;
            --clr-surface-tonal-a60: #afaab0;
            --clr-surface-tonal-a70: #c9c5ca;

            /* Success colors */
            --clr-success-a0: #22946e;
            --clr-success-a10: #47d5a6;
            --clr-success-a20: #9ae8ce;

            /* Warning colors */
            --clr-warning-a0: #a87a2a;
            --clr-warning-a10: #d7ac61;
            --clr-warning-a20: #ecd7b2;

            /* Danger colors */
            --clr-danger-a0: #9c2121;
            --clr-danger-a10: #d94a4a;
            --clr-danger-a20: #eb9e9e;

            /* Info colors */
            --clr-info-a0: #21498a;
            --clr-info-a10: #4077d1;
            --clr-info-a20: #92b2e5;
        }

        /* Light Mode Overrides */
        body.light-mode {
            --clr-light-a0: #121212;
            --clr-surface-a0: #f8f9fa;
            --clr-surface-a10: #ffffff;
            --clr-surface-a20: #e9ecef;
            --clr-surface-a30: #dee2e6;
            --clr-surface-a40: #ced4da;
            --clr-surface-a50: #adb5bd;
            --clr-surface-a60: #6c757d;
            --clr-surface-a70: #495057;
        }
        
        /* Ensure buttons have correct text color in light mode */
        body.light-mode .q-btn {
            color: white !important;
        }
        
        /* Ensure inputs have correct text color in light mode */
        body.light-mode .q-field__native {
            color: var(--clr-light-a0) !important;
        }

        html, body {
            height: 100%;
            width: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden; /* Prevent global scroll */
            background-color: var(--clr-surface-a0);
            color: var(--clr-light-a0);
            transition: background-color 0.3s, color 0.3s;
        }

        /* Ensure NiceGUI app container takes full height */
        #app {
            height: 100%;
            width: 100%;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: transparent; 
        }
        ::-webkit-scrollbar-thumb {
            background: var(--clr-surface-a30); 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--clr-surface-a40); 
        }

        /* Animations */
        .fade-in {
            animation: fadeIn 0.3s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Glassmorphism for floating panel */
        .glass-panel {
            background: rgba(40, 40, 40, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        body.light-mode .glass-panel {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(0, 0, 0, 0.1);
        }

        /* Input styling override */
        .q-field__control {
            border-radius: 16px !important; /* Rounder inputs */
        }
        
        .q-btn {
            border-radius: 16px !important; /* Rounder buttons */
        }
    </style>
    ''')
