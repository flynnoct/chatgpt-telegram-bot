# Version history

## v1.3.1

For backward compatibility, we add default parameter values to the `config.json.template` for newly added parameters.

Check issue [#78](https://github.com/flynnoct/chatgpt-telegram-bot/issues/78) for more information.

## v1.3.0

- System role customization is now supported.
- Update the config file from command line is now supported.
- Logging system is now completed for debug purposes.
- Some bugs are fixed.

## v1.2.2

- Some bugs in ACM and MSM are fixed.
- Update model to `gpt-3.5-turbo`.
- Removed support for Markdown response because the escape chars are hard to handle. Maybe it will be back in the future.

## v1.2.1

- A critical bug is fixed.

## v1.2.0

- Privacy protection improvement. The Bot now is unable to acquire messages in the group chat except user prompts.
- Beta version for Telegram inline mode. The Bot now can be invoked in a chat with a contact.
- Code hierarchy adjustment and bugs fixed.
- Documentation for config.json file is published.

## v1.1.0

- DALL·E API integration. The Bot now supports image generation based on user prompts.
- Whisper API integration. The Bot now supports interaction with voice messages.
- Usage limitation. Now support set daily limitation of requirements to DALL·E.
- Super user. Now support granting unlimited resources to Super Users.

## v1.0.0

- ChatGPT API integration.
- Telegram API integration.
- Private and group chat function.
