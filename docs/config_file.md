# Documentation for config.json

This documentation is for users who are unfamilar with JSON file and have trouble in using the `config.json` file.

## Usage

Follow below procedures to modify your `config.json`:

1. Replace the `telegram_token` and `openai_api_key` with your own.
2. Add allowed users to the `allowed_users` list. You can get your user id by sending `/start` to [@userinfobot](https://t.me/userinfobot) or send `/getid` to the Bot (after you start it).

> Note: the user ID is a series of numbers, you should add it to the `allowed_users` list as a string (add quotation marks around it).

```
{
    "openai_api_key": "<YOUR_OPENAI_API_KEY_HERE>",
    "telegram_bot_token": "<YOUR_TELEGRAM_BOT_TOKEN_HERE>",

    // Allow all users to use the bot, if enabled, "allowed_users" list won't have any effect.
    "allow_all_users": false,

    "allowed_users": [
        "<USER_ID_1>",
        "<USER_ID_2>"
    ],

    // When enabled, Bot will accept audio messages with Whisper and reply.
    "enable_voice": true,

    // The time limit in seconds that the Bot will clear the conversation context.
    "wait_time": 600,

    // When enabled, Bot will involve DALL·E to handle requests for painting.
    "enable_dalle": true,

    // Super users are granted unlimited usage on DALL·E per day.
    "super_users": [
        "<SUPER_USER_ID_1>",
        "<SUPER_USER_ID_2>"
    ],

    // The upper limit that a normal user is allowed to invoke DALL·E per day.
    "image_generation_limit_per_day": 5,

    // Beta! When enabled, Bot will be able to work in inline mode, contact @BotFather to enable inline mode for your Bot
    "enable_inline": False
}
```

## Troubleshooting

- Comments are not allowed in JSON specification. Make sure there are no commented code and words left in the file.
- There should be **no comma** after the last element in `allowed_users` and `super_users` lists.
