import sys

with open('views/user_views.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix text colors for light theme
# Label fg=TEXT_WHITE -> fg=TEXT_PRIMARY (mostly headers on card/bg)
code = code.replace('fg=TEXT_WHITE, anchor="w"', 'fg=TEXT_PRIMARY, anchor="w"')
code = code.replace('fg=TEXT_WHITE).pack(', 'fg=TEXT_PRIMARY).pack(')
code = code.replace('fg=TEXT_WHITE).pack(side="left"', 'fg=TEXT_PRIMARY).pack(side="left"')
code = code.replace('fg=TEXT_WHITE, width=36', 'fg=TEXT_PRIMARY, width=36')
# Entry fields
code = code.replace('fg=TEXT_WHITE, insertbackground', 'fg=TEXT_PRIMARY, insertbackground')
code = code.replace('fg=TEXT_WHITE, relief', 'fg=TEXT_PRIMARY, relief')

with open('views/user_views.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Color replacement successful.")
