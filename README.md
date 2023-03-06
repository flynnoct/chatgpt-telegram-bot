# ChatGPT Bot for Telegram

![](/docs/dialog.png)

## News

- **DALL·E, the OpenAI Image Generation Model**, is now supported! Send a short prompt to the Bot and get your own painting!
- **Whisper, the OpenAI Intelligent Speech Recognizer**, is now supported! Now chat with the Bot with audio messages!
- **Telegram Inline Mode** is now supported! You can ask @BotFather to enable **both** inline mode & **Inline feedback to 100%** for your Bot and use it in any private chat with a contact and group chat (even without inviting the bot as a member).
- **Important privacy protection strategy** is deployed! The Bot is unable (and of course we won't) to collect any message in group chat except user prompts.
- Better config.json.template is provided. 

## Introduction

ChatGPT Bot for Telegram is implemented with [OpenAI ChatGPT API](https://platform.openai.com/docs/guides/chat) released on March 1, 2023. The Telegram integration framework is based on [python-telegram-bot](https://python-telegram-bot.org).

ChatGPT Bot can act as your Telegram contact. You can chat with it personally, share with a contact, and collabrate in a group chat. We attach great importance to privacy protection and make sure the Bot can't acquire any unrelated messages in group chats.

The Bot shares knowledge and inspires exciting new ideas. Many interesting features, such as **DALL·E** and **Whisper** are integrated together to make our Bot smarter and more usable.

We hope you enjoy it!

## Features

The Telegram Bot features the following functions:

- An AI consultant, based on OpenAI ChatGPT, interacts in a conversational way.
- A flexible speech recognizer which supports audio interaction.
- A AI painter reponses to user's requirement prompt.

Additonal functions are also implemented:

- (Beta) _Telegram inline mode_ is supported to invoke the Bot in a private chat with a contact.
- Set `allow_all_users` to `true` to allow all users to use the Bot.
- Set the daily limitation of requirements to **DALL·E**.
- Grant more resources to _Super Users_.
- Docker deployment is supported. (This method is maintained by community. Thanks for @EstrellaXD 's contribution)

## Commands

- `/start`: Start the bot.
- `/chat` : Invoke the Bot in group chat.
- `/dalle <prompt>`: Ask DALL·E for a painting based on your prompt.
- `/clear`: Clear the conversation context.
- `/getid`: Get your Telegram user ID.

## Sample Usage

The Bot works in both personal and group chat of Telegram.

In a personal chat, simply send a message to the Bot and it will reply to you.

In a group chat, use the `/chat` to invoke the Bot. It will not collect any other message except the prompts after the command.

**(Beta)** In a personal chat with a contact, use `@your_bot_name <your messages>` to invoke the Bot with Telegram inline mode. Both you and your contact can see the Bot's reply in the chat. This function is Beta because it currently can't record the chat context.

### Preparation

1. Create a Telegram bot by [@BotFather](https://t.me/BotFather) and get the token.
2. Create an OpenAI account and get the API key.
3. A Linux VM or a server with Python 3 is needed to run the bot.
4. A practical Internet environment is required.
5. (Optional) [FFmpeg](https://ffmpeg.org) is required for the Bot to handle voice messages with Whisper. If you are not interested in using voice messages, you don't need to install it and **must set `enable_voice` in the config file to False**.

> **Note**: You should disable the privacy mode of the bot. Otherwise the bot will not receive the messages from the group chat. You can do this by sending `/setprivacy` to [@BotFather](https://t.me/BotFather).

### Deployment

1. Git clone from main branch or download the latest release [Source code](https://github.com/flynnoct/chatgpt-telegram-bot/releases/latest) file and install the dependencies.

```bash
git clone https://github.com/flynnoct/chatgpt-telegram-bot.git
cd chatgpt-telegram-bot
pip install -r requirements.txt
```

2. Create a config file to manage the Bot. The config file includes sensitive information, such as telegram_token and openai_api_key, and we only release the corresponding template `config.json.template`. Therefore, you need to create a new `config.json` file by replacing the relative fields in the template with your own.

```bash
cp config.json.template config.json
```

Follow the [documentation](docs/config_file.md) to complete your `config.json` file.

3. Run the Bot with `start_bot.sh` and try talk to it. Also, you can invite it to group chats and share with your friends! Or you can also use docker to run the bot.

```bash
# First, make sure you are in the root directory of the project,
# aka <your_download_location>/chatgpt-telegram-bot
bash ./bin/start_bot.sh # start the bot

# Use docker compose to run the bot
docker compose up -d
```

To clear ChatGPT conversation context and restart the Bot, run shell script `restart_bot.sh`. To shut down the Bot, run `stop_bot.sh`.

```bash
bash ./bin/restart_bot.sh # restart the bot
bash ./bin/stop_bot.sh # stop the bot
```

## Release version and notes

The latest released version is [here](https://github.com/flynnoct/chatgpt-telegram-bot/releases/latest).

The release notes are [here](/docs/release_notes.md).

More interesting new features are comming soon!

## License

[MIT](LICENSE.md)

## Buy Me a Coffee

If you like this project, you can buy me a coffee ❤️ or give this repository a free star ⭐️.

Click [Alipay](docs/donate_code/alipay.jpg) to open QR code.
