import sys

# --- Fix views/restaurant_views.py ---
with open('views/restaurant_views.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_const = '''BG_DARK       = "#0d0d18"
BG_CARD       = "#1a1a2e"
BG_CARD2      = "#151525"
BG_SIDEBAR    = "#111122"
ACCENT_ORANGE = "#f97316"
ACCENT_BLUE   = "#3b82f6"
ACCENT_GREEN  = "#22c55e"
ACCENT_YELLOW = "#eab308"
ACCENT_RED    = "#ef4444"
TEXT_PRIMARY  = "#f0f0f0"
TEXT_MUTED    = "#8892a4"
TEXT_WHITE    = "#ffffff"
BORDER_COLOR  = "#2a2a3e"
INPUT_BG      = "#252540"'''

new_const = '''BG_DARK       = "#f4f1ea"
BG_CARD       = "#faf9f6"
BG_CARD2      = "#ebe7dd"
BG_SIDEBAR    = "#e6e2d8"
ACCENT_ORANGE = "#e09f3e"
ACCENT_BLUE   = "#73a5c6"
ACCENT_GREEN  = "#6b9080"
ACCENT_YELLOW = "#e09f3e"
ACCENT_RED    = "#e56b6f"
TEXT_PRIMARY  = "#3a4042"
TEXT_MUTED    = "#808a8d"
TEXT_WHITE    = "#ffffff"
BORDER_COLOR  = "#d1cec7"
INPUT_BG      = "#ffffff"'''

code = code.replace(old_const, new_const)
code = code.replace('fg=TEXT_WHITE).pack(', 'fg=TEXT_PRIMARY).pack(')
code = code.replace('fg=TEXT_WHITE).pack(anchor="w"', 'fg=TEXT_PRIMARY).pack(anchor="w"')
code = code.replace('fg=TEXT_WHITE).pack(anchor="e"', 'fg=TEXT_PRIMARY).pack(anchor="e"')
code = code.replace('fg=TEXT_WHITE, width=30', 'fg=TEXT_PRIMARY, width=30')
code = code.replace('fg=TEXT_WHITE, width=25', 'fg=TEXT_PRIMARY, width=25')
code = code.replace('fg=TEXT_WHITE, relief', 'fg=TEXT_PRIMARY, relief')
code = code.replace('bg="#222235"', 'bg="#ebe7dd"')
code = code.replace('bg="#374151"', 'bg="#d1cec7"')
code = code.replace('bg="#252540"', 'bg="#e6e2d8"')
code = code.replace('fg=TEXT_WHITE).pack(side="left")', 'fg=TEXT_PRIMARY).pack(side="left")')
# Add highlightthickness to entries
code = code.replace(', relief="flat", bd=0, insertbackground=', ', relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_ORANGE, insertbackground=')

with open('views/restaurant_views.py', 'w', encoding='utf-8') as f:
    f.write(code)

# --- Fix restaurant_app.py ---
with open('restaurant_app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace hardcoded colors
code = code.replace('bg="#0d0d18"', 'bg="#f4f1ea"')
code = code.replace('bg=self.BG_DARK, fg=self.TEXT_WHITE', 'bg=self.BG_DARK, fg=self.TEXT_PRIMARY')
code = code.replace('bg=self.INPUT_BG, fg=self.TEXT_WHITE', 'bg=self.INPUT_BG, fg=self.TEXT_PRIMARY')
code = code.replace(', relief="flat", bd=0)', ', relief="flat", bd=0, highlightthickness=1, highlightbackground=self.BORDER_COLOR)')

# Fix LoginFrame constants
old_login = '''    BG_DARK    = "#0d0d18"
    BG_CARD    = "#1a1a2e"
    ACCENT     = "#f97316"
    TEXT_WHITE = "#f0f0f0"
    TEXT_MUTED = "#8892a4"
    INPUT_BG   = "#252540"'''

new_login = '''    BG_DARK    = "#f4f1ea"
    BG_CARD    = "#faf9f6"
    ACCENT     = "#e09f3e"
    TEXT_PRIMARY = "#3a4042"
    TEXT_MUTED = "#808a8d"
    TEXT_WHITE = "#ffffff"
    INPUT_BG   = "#ffffff"
    BORDER_COLOR = "#d1cec7"'''

code = code.replace(old_login, new_login)

# Fix ttk styles
old_ttk = '''        style.configure("TScrollbar",
                        background="#2a2a3e",
                        troughcolor="#0d0d18",
                        arrowcolor="#8892a4",
                        borderwidth=0)
        style.configure("TCombobox",
                        fieldbackground="#252540",
                        background="#252540",
                        foreground="#f0f0f0",
                        selectbackground="#f97316",
                        selectforeground="#ffffff")
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#252540")],
                  foreground=[("readonly", "#f0f0f0")])'''

new_ttk = '''        style.configure("TScrollbar",
                        background="#d1cec7",
                        troughcolor="#f4f1ea",
                        arrowcolor="#808a8d",
                        borderwidth=0)
        style.configure("TCombobox",
                        fieldbackground="#ffffff",
                        background="#ffffff",
                        foreground="#3a4042",
                        selectbackground="#e09f3e",
                        selectforeground="#ffffff")
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#ffffff")],
                  foreground=[("readonly", "#3a4042")])'''

code = code.replace(old_ttk, new_ttk)

with open('restaurant_app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Resto color sync done.")
