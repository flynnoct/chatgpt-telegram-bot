# Bot Command Usage Documentation

This documentation is for developers who are interested in customized the Bot.

## System Role Customization

Command `/role <prompt>` is for setting the Bot's role in conversation. ChatGPT API requires a short user prompt to describe the Bot's role.

At present, two configuration items, `enable_custom_system_role` and `system_role`, are set in the config.json file.

If ``enable_custom_system_role` is set to **true**, the `/rule` command will be allowed. `system_role` is the default prompt feeding to the ChatGPT backend API, which means the Bot's default role is "a helpful assistant".

When the `/role` command is invoked, our Bot automatically clears the previous context and sends "Say hello to me" to the ChatGPT API. Then, it will reply in the customized role tone.

Note that once the Bot exceeds the `wait_time` set in the config file, the Bot will automatically clears the conversation context and reset the role to default.
