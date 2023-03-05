import json
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update


class AccessManager:

    config_dict = {}

    def __init__(self) -> None:
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)

    # In case of granting users different authority between text, voice and file,
    # the <chat_type> field is currently reserved for future use.
    async def check_user_allowed(self, userid, chat_type, context: ContextTypes.DEFAULT_TYPE):
        with open("config.json") as f:
            config_dict = json.load(f)

            if userid in config_dict["allowed_users"]:
                return True
            else:
                await context.bot.send_message(
                    chat_id=userid,
                    text="Sorry, you are not allowed to use this bot. Contact the bot owner for more information."
                )
                return False
