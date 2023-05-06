# ChatGPT Bot for Telegram

![](/docs/dialog.png)

## 💥 Read This Before Updating to v1.4

We adjusted configuration format since v1.4.0, which is NOT compatible with previous versions. Please check the [config doc](./docs/config_file.md) for more details. You should backup your old config file and create a new one after updating to v1.4.0.

## 🎉 News

- **Microsoft Azure TTS** is now supported! The Bot can now reply with voice messages!
- **ChatGPT temperature** is now supported! You can set the temperature in configuration to customize the creativity of ChatGPT reply.
- A better **logging system** is provided for debugging purposes.
- A better-organized config structure is provided. You should go through the [config doc](./docs/config_file.md) and modify the config file. We have temporarily removed the `config.py` configuration script.
- Model selection ability is added. You can now choose the model you want to use in the config file. The Bot can be powered by GPT-4 if you have access.

## 🐱 Introduction

ChatGPT Bot for Telegram is implemented with [OpenAI ChatGPT API](https://platform.openai.com/docs/guides/chat) released on March 1, 2023. The Telegram integration framework is based on [python-telegram-bot](https://python-telegram-bot.org).

ChatGPT Bot can act as your Telegram contact. You can chat with it personally, share with a contact, and collabrate in a group chat. We attach great importance to privacy protection and make sure the Bot can't acquire any unrelated messages in group chats.

The Bot shares knowledge and inspires exciting new ideas. Many interesting features, such as **DALL·E** and **Whisper** are integrated together to make our Bot smarter and more usable.

We hope you enjoy it!

## 🌟 Features

The Telegram Bot features the following functions:

- **ChatGPT, the AI consultant**. You can customize the Bot's character according to preference.
- **DALL·E, the Image Generation AI Model**. Send a short prompt to the Bot and get your own painting.
- **Whisper, the Intelligent Speech Recognizer**. The Bot can read your voice messages.
- **Azure TTS, the Speech service feature that converts text to lifelike speech**. The Bot can reply with voice messages.
- **Comprehensive Privacy Protection**. The Bot is unable (and of course we won't) to collect any message in group chat except user prompts.

Additonal features:

- ChatGPT role and temperature Customization.
- The Telegram _inline mode_ allows you to query the Bot privately in a chat with a contact or group, even if the Bot is not a member.
- User White-list to control who can use the Bot. You can also set `allow_all_users` to `true` to allow any users to use the Bot.
- Set the daily limitation of requirements to **DALL·E**.
- Grant more resources to _Super Users_.
- Docker deployment is supported. (This method is maintained by community. Thanks for @EstrellaXD 's contribution)

## 👷 Deploy Your Own

### Preparation

1. Create a Telegram Bot by [@BotFather](https://t.me/BotFather) and get the token.
2. Create an OpenAI account and get the API key.
3. A Linux VM or a server with Python 3 is needed to run the Bot.
4. A practical Internet environment is required.
5. (Optional) [FFmpeg](https://ffmpeg.org) is required for the Bot to handle voice messages with Whisper. If you are not interested in using voice messages, you don't need to install it and **must set `enable_voice` in the config file to False**.
6. (Optional) [Azure TTS SDK](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/quickstarts/setup-platform?pivots=programming-language-python&tabs=linux) is required for the Bot to reply with voice messages.

### Installation

1. Git clone from main branch or download the latest release [Source code](https://github.com/flynnoct/chatgpt-telegram-bot/releases/latest) file and install the dependencies.

```bash
git clone https://github.com/flynnoct/chatgpt-telegram-bot.git
cd chatgpt-telegram-bot
pip install -r requirements.txt
```

2. Create a config file to manage the Bot.

The config file includes sensitive information, such as telegram_token and openai_api_key, and we only release the corresponding template `config.json.template`. Therefore, you need to create a new `config.json` file by replacing the relative fields in the template with your own.

```bash
cp config.json.template config.json
```

**Recommended:** You should keep `config.json.template` unmodified because the Bot needs to read default configuration values from it. For backward compatibility, it is highly recommended to check the template for newly added parameters when you update to a new version.

For more details, see [documentation](docs/config_file.md).

3. Run the Bot with `start_bot.sh` and try talk to it. You can also use docker to run the Bot.

```bash
# First, make sure you are in the root directory of the project,
# aka <your_download_location>/chatgpt-telegram-bot
bash ./bin/start_bot.sh # start the Bot

# Use docker compose to run the Bot
docker compose up -d
```

To clear ChatGPT conversation context and restart the Bot, run shell script `restart_bot.sh`. To shut down the Bot, run `stop_bot.sh`.

```bash
bash ./bin/restart_bot.sh # restart the Bot
bash ./bin/stop_bot.sh # stop the Bot
```

Up to now, you have successfully deployed the Bot.

### Usage

The Bot works in both personal and group chat of Telegram.
In a personal chat, simply send a message to the Bot and it will reply to you.
In a group chat, use the `/chat` to invoke the Bot. 

In a personal chat with a contact, use `@your_bot_name <your messages>` to invoke the Bot with Telegram inline mode. Both you and your contact can see the Bot's reply in the chat. 

1. The following commands are supported:

- `/start`: Start the Bot.
- `/role <prompt>`: Set role for conversation.
- `/chat` : Invoke the Bot in group chat.
- `/dalle <prompt>`: Ask DALL·E for a painting based on your prompt.
- `/clear`: Clear the conversation context.
- `/getid`: Get your Telegram user ID.

(Optinal) You can set them up as Telegram Bot command, see [here](https://core.telegram.org/bots/tutorial#creating-your-command).

2. Inline mode

To enable inline mode, see [here](https://core.telegram.org/bots/api#inline-mode). 

Type `/mybots` > Your_Bot_Name > Bot Settings > Inline Feedback, you must set the `Inline Feedback` to 100%.


### TroubleShooting

See [documentation](./docs/troubleshooting.md).

## 🧑‍💻 For developers

Documentation is provided under [docs](./docs) for developers who wants to customize the Bot.

## 📚 Release Notes

The latest released version is [here](https://github.com/flynnoct/chatgpt-telegram-bot/releases/latest).

The release notes are [here](/docs/release_notes.md).

More interesting new features are coming soon!

## 🪪 License

[MIT](LICENSE.md)

## ☕️ Buy Me a Coffee (not Java)

If you like this project, you can buy me a coffee ❤️ or give this repository a free star ⭐️.

Click [Alipay](docs/donate_code/alipay.jpg) to open QR code.
