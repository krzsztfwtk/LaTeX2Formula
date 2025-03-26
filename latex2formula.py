import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import re

POWER_FUNCT_NAME = "POWER"
SQRT_FUNCT_NAME = "SQRT"

def find_matching(s, start, open_char, close_char):
    count = 0
    for i in range(start, len(s)):
        if s[i] == open_char:
            count += 1
        elif s[i] == close_char:
            count -= 1
            if count == 0:
                return i
    return -1

def remove_outer_parentheses(expr):
    expr = expr.strip()
    if expr.startswith('(') and expr.endswith(')'):
        if find_matching(expr, 0, '(', ')') == len(expr) - 1:
            return remove_outer_parentheses(expr[1:-1])
    return expr

def simple_token(token):
    token = token.strip()
    return re.fullmatch(r'[0-9.]+', token) or re.fullmatch(r'[a-zA-Z]+', token)

def process_frac(s):
    pattern = re.compile(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}')
    while pattern.search(s):
        def rep(m):
            num = m.group(1).strip()
            den = m.group(2).strip()
            num = remove_outer_parentheses(num)
            den = remove_outer_parentheses(den)
            if not simple_token(num):
                num = f'({num})'
            if not simple_token(den):
                den = f'({den})'
            return f'{num}/{den}'
        s = pattern.sub(rep, s)
    return s

def process_power(s):
    while '^{' in s:
        idx = s.find('^{')
        base_end = idx
        if base_end > 0 and s[base_end - 1] == ')':
            j = base_end - 1
            count = 0
            while j >= 0:
                if s[j] == ')':
                    count += 1
                elif s[j] == '(':
                    count -= 1
                    if count == 0:
                        break
                j -= 1
            base_start = j
        else:
            j = base_end - 1
            while j >= 0 and (s[j].isalnum() or s[j] in '._/'):
                j -= 1
            base_start = j + 1
        base = remove_outer_parentheses(s[base_start:base_end])
        exp_start = idx + 2
        exp_end = find_matching(s, idx + 1, '{', '}')
        if exp_end == -1:
            break
        exponent = s[exp_start:exp_end].strip()
        replacement = f'{POWER_FUNCT_NAME}({base},{exponent})'
        s = s[:base_start] + replacement + s[exp_end+1:]
    return s

def process_sqrt(s):
    while r'\sqrt{' in s:
        idx = s.find(r'\sqrt{')
        content_start = idx + len(r'\sqrt{')
        content_end = find_matching(s, content_start - 1, '{', '}')
        if content_end == -1:
            break
        content = s[content_start:content_end].strip()
        replacement = f'{SQRT_FUNCT_NAME}({content})'
        s = s[:idx] + replacement + s[content_end+1:]
    return s

def latex_to_formula(latex):
    s = latex.replace(r'\cdot', '*').replace(r'\left', '').replace(r'\right', '')
    s = process_frac(s)
    s = process_power(s)
    s = process_sqrt(s)
    return s

def convert_and_show():
    input_text = input_entry.get("1.0", tk.END).strip()
    output_text = latex_to_formula(input_text)
    output_field.config(state='normal')
    output_field.delete("1.0", tk.END)
    output_field.insert(tk.END, output_text)
    output_field.config(state='normal')

def copy_output():
    output_text = output_field.get("1.0", tk.END).strip()
    root.clipboard_clear()
    root.clipboard_append(output_text)

root = tk.Tk()
root.title("LaTeX to Formula Converter")
root.configure(bg='white')

input_label = tk.Label(root, text="Enter LaTeX code:", bg='white', fg='black', font=('Arial', 12))
input_label.pack(pady=(10, 0))

input_entry = ScrolledText(root, width=70, height=6, font=('Arial', 12),
                           fg='black', bg='white', insertbackground='black', undo=True)
input_entry.pack(pady=10)

convert_button = tk.Button(root, text="Convert", command=convert_and_show,
                           bg='white', fg='black', font=('Arial', 12),
                           highlightthickness=1, highlightbackground='black')
convert_button.pack(pady=10)

output_label = tk.Label(root, text="Converted formula:", bg='white', fg='black', font=('Arial', 12))
output_label.pack(pady=(10, 0))

output_field = ScrolledText(root, width=70, height=6, font=('Arial', 12),
                            fg='black', bg='white', insertbackground='black', undo=True)
output_field.pack(pady=(0, 10))

copy_button = tk.Button(root, text="Copy Output", command=copy_output,
                        bg='white', fg='black', font=('Arial', 12),
                        highlightthickness=1, highlightbackground='black')
copy_button.pack(pady=(0, 10))

root.mainloop()
