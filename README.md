# ChatGPT Bot for Telegram

This repository contains a Telegram bot implemented with OpenAI ChatGPT API (gpt-3.5-turbo-0301) released on March 1, 2023.

## Introduction

This is a Telegram bot implemented with OpenAI ChatGPT API (gpt-3.5-turbo-0301). It is based on [OpenAI ChatGPT API](https://platform.openai.com/docs/guides/chat) and [python-telegram-bot](https://python-telegram-bot.org).

## Usage

### Private Chat

You can just send a message to the bot in private chat. The bot will reply to you.

### Group Chat

You can add the bot to a group chat. However, it will only reply the messages with `@<bot_name>` mentioned.

### Commands

- `/start`: Start the bot.
- `/clear`: Clear the conversation context.
- `/getid`: Get your Telegram user ID.

## Installation

### Prepare

1. Create a Telegram bot by [@BotFather](https://t.me/BotFather) and get the token.
2. Create an OpenAI account and get the API key.
3. A VM or a server with Python 3 is needed to run the bot.

> **Note**: You should disable the privacy mode of the bot. Otherwise the bot will not receive the messages from the group chat. You can do this by sending `/setprivacy` to [@BotFather](https://t.me/BotFather).

### Deploy

Clone this repository.

```bash
git clone git@github.com:flynnoct/chatgpt-telegram-bot.git
```

Install the dependencies.

```bash
pip install -r requirements.txt
```

Create config file.

```bash
cp config.json.template config.json
```

Modify config file. First,

```bash
vim config.json
```

then, replace the `telegram_token` and `openai_api_key` with your own.

Add allowed users to the `allowed_users` list. You can get your user id by sending `/start` to [@userinfobot](https://t.me/userinfobot) or send `/getid` to this bot (after you start it).

> Note: the user ID is a series of numbers, you should add it to the `allowed_users` list as a string (add quotation marks around it).

Run the bot.

```bash
nohup python3 telegram_message_parser.py &
```

> Note: A launch script will be added later.

Now you can start a private chat to the bot or add the bot to your group chat. Enjoy.

## License

[MIT](LICENSE.md)

## Buy Me a Coffee

If you like this project, you can buy me a coffee ❤️ or give this repository a free star ⭐️.

Click [Alipay](donate_code/alipay.jpg) to open QR code.
