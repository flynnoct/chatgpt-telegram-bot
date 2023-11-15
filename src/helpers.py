from telegram import helpers as tg_helpers
import tiktoken

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
    
    # Process each replacement sequentially
    for original, replacement in replacements.items():
        md_str = md_str.replace(original, replacement)
        
    return md_str


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens