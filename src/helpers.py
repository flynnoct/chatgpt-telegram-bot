from telegram import helpers as tg_helpers

def escape_markdownv2(text):
    md_str = tg_helpers.escape_markdown(text, version=2)
    # Replacements for escaped characters which should be unescaped
    replacements = {
        # basic markdown
        r'\*': '*',     # bold or list
        r'\_': '_',     # italic or underline
        r'\~': '~',     # strikethrough
        r'\[': '[',     # link
        r'\]': ']',     # link
        r'\(': '(',     # link
        r'\)': ')',     # link
        r'\!': '!',     # image
        r'\`\`\`': '```', # code block
        r'\`': '`',     # inline code
        r'\|': '|',     # spoiler
        # unicode emoji or other future chars can be easy added here
    }

    md_str = md_str.replace('\`\`\`', '```')
    
    # Process each replacement sequentially
    # for original, replacement in replacements.items():
    #     md_str = md_str.replace(original, replacement)
        
    return md_str
