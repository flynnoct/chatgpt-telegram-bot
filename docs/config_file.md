# Configuration File

This document is intended to assist administrators in deploying and configuring this bot correctly, and covers the meanings of all the items that appear in the `config.json` file, which is in JSON file format and located in the root of this project's workspace. 

> Note: It is important to pay attention to the use of quotation marks in JSON files, as they may introduce type issues and potential errors.

## Usage

Follow below procedures to modify your `config.json`:

1. Replace the `telegram_token` and `openai_api_key` with your own.
2. Add allowed users to the `allowed_users` list. You can get your user id by sending `/start` to [@userinfobot](https://t.me/userinfobot) or send `/getid` to the Bot (after you start it).

> Note: the user ID is a series of numbers, you should add it to the `allowed_users` list as a string (add quotation marks around it).

3. Customize the rest config keys for your own need, or just use the default values.

```json
{
    <!-- The Telegram config list. -->
    "telegram": {
        "bot_token": "<YOUR_TELEGRAM_BOT_TOKEN_HERE>",

        <!-- The Telegram inline mode switch (https://telegram.org/blog/inline-bots). It allows you to invoke and share the Bot without leaving the current session. -->
        "enable_inline_mode": true,

        <!-- The time limit that Bot records the conversation context. Over this bond will cause the Bot to clean up previous context. -->
        "context_expiration_time": 600
    },

    <!-- The ChatGPT config list. -->
    "openai": {
        "api_key": "<YOUR_OPENAI_API_KEY_HERE>",

        <!-- The ChatGPT model. -->
        "chat_model": "gpt-3.5-turbo",

        <!-- The ChatGPT temperature (https://platform.openai.com/docs/api-reference/chat/create#chat/create-temperature). Higher value provides more creativity in the response. -->
        "chat_temperature": 1.0,

        <!-- The system role customization switch. -->
        "enable_custom_system_role": true,

        <!-- The prompt to indicate the system role. -->
        "default_system_role": "You are a helpful assistant",

        <!-- The time limit that the Bot will stall the previous message. The Bot will process the next message if ChatGPT spends more time than apt_timeout on the previous message. -->
        "api_timeout": 30
    },

    <!-- The user privilege config list. -->
    "user_management": {
        <!-- The user privilege switch. Set to true will grant access to all users and ignore the allowed_users list. -->
        "allow_all_users": false,

        <!-- The list that contains the ID of allowed users. -->
        "allowed_users": [
            "<USER_ID_1>", 
            "<USER_ID_2>"
        ],

        <!-- The list that contains the ID of super users. Super users are granted unlimited usage on DALL·E per day. -->
        "super_users": [
            "<SUPER_USER_ID_1>",
            "<SUPER_USER_ID_2>"
        ]
    },

    <!-- The Dalle config list. -->
    "image_generation": {

        <!-- The Dalle switch. -->
        "enable_dalle": true,

        <!-- The upper limit that an unprivileged user is allowed to invoke DALL·E per day. -->
        "limit_per_day": 5
    },

    <!-- The voice interaction config list. -->
    "voice_message": {

        <!-- The voice interaction switch. Set to true will enable the Bot to resolve voice messages with Whisper. -->
        "enable_voice": true,

        <!-- The Azure TTS switch. Set to true will enable the Bot to reply in voice messages with TTS. -->
        "tts_reply": true,

        <!-- The TTS caption mode switch. When enabled, the Bot will reply the text together with the TTS voice messages.  -->
        "text_as_caption": true
    },

    <!-- The Azure TTS config list. -->
    "azure_tts": {

        <!-- The language used in TTS input text. -->
        "language": "en-US",

        <!-- The voice that TTS uses. Note that if the voice key will overwrite the language key if they mismatch. For more voice options, see https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts#prebuilt-neural-voices -->
        "voice": "en-US-AmberNeural",

        <!-- To get Azure TTS key, see https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech -->
        "subscription_key": "<YOUR_AZURE_TTS_SUBSCRIPTION_KEY_HERE>",
        "subscription_region": "<YOUR_AZURE_TTS_SUBSCRIPTION_REGION_HERE>"
    },

    <!-- The logging system config list. -->
    "logging": {
        "log_level": "INFO",
        "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "log_path": "./log/",
        "log_file_with_time": false
    }
}

```



## Troubleshooting

- Comments are not allowed in JSON specification. Make sure there are no commented code and words left in the file.
- There should be **no comma** after the last element in `allowed_users` and `super_users` lists.
