#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TelegramParser

Enter description of this module

__author__ = Zhiquan Wang
__copyright__ = Copyright 2023
__version__ = 2.0.0
__maintainer__ = Zhiquan Wang
__email__ = contact@flynnoct.com
__status__ = Dev
"""

import asyncio
import random

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, InlineQueryHandler, ChosenInlineResultHandler, ContextTypes, filters

from message_manager import MessageManager
from access_manager import AccessManager
from config_loader import ConfigLoader

from helpers import escape_markdownv2

class TelegramParser:

    def __init__(self):
        # init bot
        self.bot = ApplicationBuilder().token(ConfigLoader.get("telegram", "bot_token")).concurrent_updates(True).build()
        # add handlers
        self.add_handlers()
        # init managers
        self.access_manager = AccessManager()
        self.message_manager = MessageManager()

    def add_handlers(self):
        # command handlers
        # self.bot.add_handler(CommandHandler("start", self.cmd_start))
        self.bot.add_handler(CommandHandler("clear", self.cmd_clear_context))
        # self.bot.add_handler(CommandHandler("getid", self.cmd_get_user_id))

        # special message handlers
        # if ConfigLoader.get("voice_message", "enable_voice"):
        #     self.bot.add_handler(MessageHandler(filters.VOICE, self.chat_voice))
        # if ConfigLoader.get("image_generation", "enable_image_generation"):
        #     self.bot.add_handler(CommandHandler("dalle", self.cmd_image_generation))
        # if ConfigLoader.get("openai", "enable_custom_system_role"):
        #     self.bot.add_handler(CommandHandler("role", self.cmd_set_system_role))

        # inline query handler
        # if ConfigLoader.get("telegram", "enable_inline_mode"):
        #     self.bot.add_handler(InlineQueryHandler(self.inline_query))
        #     self.bot.add_handler(ChosenInlineResultHandler(self.inline_query_result_chosen))

        # self.bot.add_handler(MessageHandler(filters.AUDIO | filters.VIDEO, self.chat_file))

        # photo handler
        self.bot.add_handler(MessageHandler(filters.PHOTO, self.chat_photo))

        # normal chat messages handlers in private chat
        self.bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.chat_text))
        # normal message handlers in group chat
        # self.bot.add_handler(CommandHandler("chat", self.cmd_chat_text))

        # unknown command handler
        # self.bot.add_handler(MessageHandler(filters.COMMAND, self.cmd_unknown))

    # normal chat messages
    async def chat_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # if group chat
        if update.effective_chat.type == "group" or update.effective_chat.type == "supergroup":
            return

        # check if user is allowed
        if not AccessManager.is_allowed(update.effective_user.id, "chat"):
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return
        
        # get message
        message = update.effective_message.text

        # FIXME: sending typing action
        # await context.bot.send_chat_action(
        #     chat_id=update.effective_chat.id,
        #     action="typing"
        # )

        # get response and send
        responses = await self.message_manager.get_chat_response(str(update.effective_chat.id), message)
        for response in responses:
            # FIXME: Handle Images
            if response["type"] == "text":
                escaped_response = escape_markdownv2(response["value"])
            message = await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = escaped_response,
                reply_to_message_id = update.effective_message.message_id,
                allow_sending_without_reply = True,
                parse_mode = 'MarkdownV2'
            )

    # chat photos
    async def chat_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # if group chat
        if update.effective_chat.type == "group" or update.effective_chat.type == "supergroup":
            return
        
        # check if user is allowed
        if not AccessManager.is_allowed(update.effective_user.id, "chat"):
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return
        
        # get photo url and text
        file_id = update.effective_message.photo[-1].file_id # largest photo
        photo_file = await context.bot.get_file(file_id)
        photo_url = photo_file.file_path
        text = update.effective_message.caption

        # sending typing action
        # FIXME: crash when sending two photos
        # await context.bot.send_chat_action(
        #     chat_id=update.effective_chat.id,
        #     action="typing"
        # )

        response = await self.message_manager.get_vision_response(text, photo_url)
        escaped_response = escape_markdownv2(response)

        await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = escaped_response,
                reply_to_message_id = update.effective_message.message_id,
                allow_sending_without_reply = True,
                parse_mode = 'MarkdownV2'
            )
        
    async def cmd_clear_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # check if user is allowed
        if not AccessManager.is_allowed(update.effective_user.id, "chat"):
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return
        self.message_manager.clear_context(str(update.effective_chat.id))
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Context cleared."
        )

    
    def run(self):
        self.bot.run_polling()

if __name__ == "__main__":
    my_bot = TelegramParser()
    my_bot.run()