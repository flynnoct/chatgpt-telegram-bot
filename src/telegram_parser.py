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
import io

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
        if ConfigLoader.get("openai", "image_generation", "enabled"):
            self.bot.add_handler(CommandHandler("dalle", self.cmd_image_generation))
        # if ConfigLoader.get("openai", "enable_custom_system_role"):
        #     self.bot.add_handler(CommandHandler("role", self.cmd_set_system_role))

        # inline query handler
        # if ConfigLoader.get("telegram", "enable_inline_mode"):
        #     self.bot.add_handler(InlineQueryHandler(self.inline_query))
        #     self.bot.add_handler(ChosenInlineResultHandler(self.inline_query_result_chosen))

        # self.bot.add_handler(MessageHandler(filters.AUDIO | filters.VIDEO, self.chat_file))

        # photo handler, handled with vision GPT
        self.bot.add_handler(MessageHandler(filters.PHOTO, self.chat_photo))

        # normal chat messages handlers in private chat
        self.bot.add_handler(MessageHandler((filters.TEXT | filters.Document.ALL) & (~filters.COMMAND), self.chat))
        # normal message handlers in group chat
        # self.bot.add_handler(CommandHandler("chat", self.cmd_chat_text))

        # unknown command handler
        # self.bot.add_handler(MessageHandler(filters.COMMAND, self.cmd_unknown))

    # normal chat messages
    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        # def reply_callback
        async def reply_callback(responses):
            for response_message in responses:
                for content in response_message:
                    # if it's a text message
                    if content["type"] == "text":
                        text_value = content["text_value"]
                        response_files = []
                        # file paths
                        annotations = content["annotations"]["file_path"]
                        for annotation in annotations:
                            response_files.append({
                                "file_name": annotation["file_name"], 
                                "file_content": io.BytesIO(annotation["file_content"]),
                                "placeholder_text": annotation["placeholder_text"]
                                })
                        # file citations
                        annotations = content["annotations"]["file_citation"]
                        for annotation in annotations:
                            pass # TODO: add citation
                        # send message
                        if len(response_files) == 0: # no files
                            text_value = escape_markdownv2(text_value)
                            await context.bot.send_message(
                                chat_id = update.effective_chat.id,
                                text = text_value,
                                parse_mode = 'MarkdownV2'
                                )
                        else: # with files
                            for i in range(len(response_files)):
                                text_value = text_value.replace(
                                    response_files[i]["placeholder_text"],
                                    response_files[i]["file_name"]
                                    )
                            text_value = escape_markdownv2(text_value)
                            await context.bot.send_message(
                                chat_id = update.effective_chat.id,
                                text = text_value,
                                parse_mode = 'MarkdownV2'
                                )
                            for response_file in response_files:
                                await context.bot.send_document(
                                    chat_id = update.effective_chat.id,
                                    document = response_file["file_content"],
                                    filename = response_file["file_name"]
                                )
                        return
                    # elif it is an image
                    elif content["type"] == "image_file":
                        await context.bot.send_document(
                            chat_id = update.effective_chat.id,
                            document = io.BytesIO(content["file_content"]),
                            filename = content["file_name"]
                        )
                        return
                    elif content["type"] == "thread_killed":
                        await context.bot.send_message(
                            chat_id = update.effective_chat.id,
                            text = "🧹 A new thread has been created."
                            )
                        return
        
        async def send_typing_action_callback():
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )

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
        

        if update.message.document: # if it's a file
            message_text = update.message.caption if update.message.caption else ""
            telegram_file = await update.message.document.get_file()
            bytes_io = io.BytesIO()
            await telegram_file.download_to_memory(out = bytes_io)
            bytes_io.seek(0)
            message_document = bytes_io.getvalue()
            await self.message_manager.get_file_message(
                str(update.effective_chat.id), 
                message_text, 
                message_document,
                reply_callback, 
                send_typing_action_callback
                )

        else:
            # get message
            message = update.effective_message.text
            # get response and send
            await self.message_manager.get_text_message(str(update.effective_chat.id), message, reply_callback, send_typing_action_callback)
        return


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
        response = escape_markdownv2(response)

        await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = response,
                reply_to_message_id = update.effective_message.message_id,
                allow_sending_without_reply = True,
                parse_mode = 'MarkdownV2'
            )
    
    # image_generation command, aka DALLE
    async def cmd_image_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        # check if user is allowed
        if not AccessManager.is_allowed(update.effective_user.id, "image_generation"):
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot to generate images."
            )
            return
        
        # remove dalle command from message
        # message = update.effective_message.text.replace("/dalle", "")
        message = " ".join(context.args)

        # send prompt to openai image generation and get image url
        image_url = self.message_manager.get_generated_image_url(
            message,
            num = 1
            )

        if image_url is None:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Please try again later."
            )

        else:
            # sending typing action
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="upload_document"
            )
            # send file to user
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=image_url
            )
        
    async def cmd_clear_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # check if user is allowed
        if not AccessManager.is_allowed(update.effective_user.id, "chat"):
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return
        self.message_manager.new_thread(str(update.effective_chat.id))
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Context cleared."
        )

    
    def run(self):
        self.bot.run_polling()

if __name__ == "__main__":
    my_bot = TelegramParser()
    my_bot.run()