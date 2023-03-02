#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""TelegramMessageParser

Enter description of this module

__author__ = Zhiquan Wang
__copyright__ = Copyright 2022
__version__ = 1.0
__maintainer__ = Zhiquan Wang
__email__ = i@flynnoct.com
__status__ = Dev
"""

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import json
# from openai_parser import OpenAIParser
from message_manager import MessageManager


class TelegramMessageParser:
    def __init__(self):
        # load config
        with open("config.json") as f:
            config_dict = json.load(f)
        # init bot
        self.bot = ApplicationBuilder().token(config_dict["telegram_bot_token"]).build()
        # add handlers
        self.add_handlers()

        # init openai
        # self.openai_parser = OpenAIParser()

        # init MessageManager
        self.message_manager = MessageManager()

        # start bot
        self.bot.run_polling()

    def add_handlers(self):
        self.bot.add_handler(CommandHandler("start", self.start))
        self.bot.add_handler(CommandHandler("clear", self.clear_context))
        self.bot.add_handler(CommandHandler("getid", self.get_user_id))
        self.bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.chat))
        self.bot.add_handler(MessageHandler(filters.COMMAND, self.unknown))

    # chat messages
    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # check if user is allowed to use this bot
        if not self.check_user_allowed(str(update.effective_user.id)):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, you are not allowed to use this bot. Contact the bot owner for more information."
            )
            return
        # get message
        message = update.effective_message.text
        # group chat without @username
        if (update.effective_chat.type == "group" or update.effective_chat.type == "supergroup") and not ("@" + context.bot.username) in message:
            return
        # send message to openai
        response = self.message_manager.get_response(str(update.effective_user.id), message)
        # send response to user
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response
        )

    # start command
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello, I'm your ChatGPT bot."
        )

    # clear context command
    async def clear_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.message_manager.clear_context(str(update.effective_user.id))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Context cleared."
        )
    
    # get user id command
    async def get_user_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=str(update.effective_user.id)
        )
    
    # unknown command
    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, I didn't understand that command."
        )

    # check if user is allowed to use this bot, add user to "allowed_users" in config.json
    def check_user_allowed(self, userid):
        with open("config.json") as f:
            config_dict = json.load(f)
            if userid in config_dict["allowed_users"]:
                return True
            else:
                return False

if __name__ == "__main__":
    TelegramMessageParser()
    


