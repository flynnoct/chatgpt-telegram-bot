from telegram import helpers as tg_helpers

# TODO: add more escaping
def escape_markdownv2(text):
    all_escaped_text = tg_helpers.escape_markdown(text, version=2)
    # only allowed code for now
    unescaped_text = all_escaped_text.replace("\`\`\`", "```")
    return unescaped_text