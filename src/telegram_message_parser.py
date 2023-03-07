#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TelegramMessageParser

Enter description of this module

__author__ = Zhiquan Wang
__copyright__ = Copyright 2023
__version__ = 1.2.0
__maintainer__ = Zhiquan Wang
__email__ = i@flynnoct.com
__status__ = Dev
"""

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, InlineQueryHandler, ChosenInlineResultHandler, ContextTypes, filters
import json, os
from uuid import uuid4
from message_manager import MessageManager
from access_manager import AccessManager

with open("config.json") as f:
    config_dict = json.load(f)
if config_dict["enable_voice"]:
    import subprocess


class TelegramMessageParser:

    config_dict = {}

    def __init__(self):

        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)

        # init bot
        self.bot = ApplicationBuilder().token(self.config_dict["telegram_bot_token"]).build()
        # add handlers
        self.add_handlers()

        # init AccessManager
        self.access_manager = AccessManager()

        # init MessageManager
        self.message_manager = MessageManager(self.access_manager)

    def run_polling(self):
        self.bot.run_polling()

    def add_handlers(self):
        # command handlers
        self.bot.add_handler(CommandHandler("start", self.start))
        self.bot.add_handler(CommandHandler("clear", self.clear_context))
        self.bot.add_handler(CommandHandler("getid", self.get_user_id))

        # special message handlers
        if self.config_dict["enable_voice"]:
            self.bot.add_handler(MessageHandler(filters.VOICE, self.chat_voice))
        if self.config_dict["enable_dalle"]:
            self.bot.add_handler(CommandHandler("dalle", self.image_generation))
        self.bot.add_handler(MessageHandler(filters.PHOTO | filters.AUDIO | filters.VIDEO, self.chat_file))

        # inline query handler
        if self.config_dict["enable_inline"]:
            self.bot.add_handler(InlineQueryHandler(self.inline_query))
            self.bot.add_handler(ChosenInlineResultHandler(self.inline_query_result_chosen))

        # normal message handlers
        # self.bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.chat_text))
        # normal chat messages handlers in private chat
        self.bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.chat_text))
        self.bot.add_handler(CommandHandler("chat", self.chat_text_command))

        # unknown command handler
        self.bot.add_handler(MessageHandler(filters.COMMAND, self.unknown))

    # normal chat messages
    async def chat_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):


        # if group chat
        if update.effective_chat.type == "group" or update.effective_chat.type == "supergroup":
            return

        # get message
        message = update.effective_message.text

        # check if user is allowed
        allowed, _ = self.access_manager.check_user_allowed(str(update.effective_user.id))
        if not allowed:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return

        # sending typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        # send message to openai
        response = self.message_manager.get_response(
            str(update.effective_chat.id), 
            str(update.effective_user.id), 
            message
            )
        # reply response to user
        await update.message.reply_text(response)

    # command chat messages
    async def chat_text_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # get message
        message = update.effective_message.text

        # sending typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        # check if user is allowed
        allowed, _ = self.access_manager.check_user_allowed(str(update.effective_user.id))
        if not allowed:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return

        # send message to openai
        response = self.message_manager.get_response(
            str(update.effective_chat.id), 
            str(update.effective_user.id), 
            message
            )

        # reply response to user
        await update.message.reply_text(response, parse_mode='Markdown')

    # voice message in private chat, speech to text with Whisper API and process with ChatGPT
    async def chat_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # check if it's a private chat
        if not update.effective_chat.type == "private":
            return

        # check if user is allowed to use this bot
        allowed, _ = self.access_manager.check_user_allowed(str(update.effective_user.id))
        if not allowed:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return


        # sending typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        try:
            file_id = update.effective_message.voice.file_id
            new_file = await context.bot.get_file(file_id)
            await new_file.download_to_drive(file_id + ".ogg")

            file_size = os.path.getsize(file_id + ".ogg") / 1000
            # # if < 200kB, convert to wav and send to openai
            # if file_size > 50:
            #     await update.message.reply_text("Sorry, the voice message is too long.")
            #     return

            subprocess.call(
                ['ffmpeg', '-i', file_id + '.ogg', file_id + '.wav'],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
                )

            with open(file_id + ".wav", "rb") as audio_file:
                transcript = self.message_manager.get_transcript(
                    str(update.effective_user.id), 
                    audio_file
                    )
            os.remove(file_id + ".ogg")
            os.remove(file_id + ".wav")

        except Exception as e:
            await update.message.reply_text("Sorry, something went wrong. Please try again later.")
            return

        response = self.message_manager.get_response(
            str(update.effective_chat.id), 
            str(update.effective_user.id), 
            transcript
            )
        await update.message.reply_text("\"" + transcript + "\"\n\n" + response)

    # image_generation command, aka DALLE
    async def image_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # remove dalle command from message
        message = update.effective_message.text.replace("/dalle", "")

        # send prompt to openai image generation and get image url
        image_url, prompt = self.message_manager.get_generated_image_url(
            str(update.effective_user.id), 
            message
            )

        # if exceeds use limit, send message instead
        if image_url is None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=prompt
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
                document=image_url,
                caption=prompt
            )

    # inline text messages
    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # get query message
        query = update.inline_query.query   

        if query == "":
            return

        # check if user is allowed to use this bot
        allowed, _ = self.access_manager.check_user_allowed(str(update.effective_user.id))
        if not allowed:
            results = [
                InlineQueryResultArticle(
                    id = str(uuid4()),
                    title = "Sorry😢",
                    description = "Sorry, you are not allowed to use this bot.",
                    input_message_content = InputTextMessageContent("Sorry, you are not allowed to use this bot.")
                )
            ]
        else:
            results = [
                InlineQueryResultArticle(
                    id = str(uuid4()),
                    title = "Chat💬",
                    description = "Get a response from ChatGPT (It's a beta feature, no context ability yet)",
                    input_message_content = InputTextMessageContent(query),
                    reply_markup = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("🐱 I'm thinking...", switch_inline_query_current_chat = query)]
                        ]
                    )
                )
            ]

        # await update.inline_query.answer(results, cache_time=0, is_personal=True, switch_pm_text="Chat Privately 🤫", switch_pm_parameter="start")
        await update.inline_query.answer(results, cache_time=0, is_personal=True)
    
    async def inline_query_result_chosen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # invalid user won't get a response
        try:
            # get userid and resultid
            user_id = update.chosen_inline_result.from_user.id
            result_id = update.chosen_inline_result.result_id
            inline_message_id = update.chosen_inline_result.inline_message_id
            query = update.chosen_inline_result.query
            # query_id = query[query.find("My_Memory_ID: ")+14:query.find("\n=======")]
            
            # if query_id == "": # if no query_id, generate one
            #     query_id = str(uuid4())
            # else: # if query_id, remove it from query
            #     query = query[query.find("\n======="):]
            # print(query_id, query)

            # TODO: replace result_id
            response = "\"" + query + "\"\n\n" + self.message_manager.get_response(str(result_id), str(user_id), query)

            # edit message
            await context.bot.edit_message_text(
                response,
                inline_message_id = inline_message_id,
                # reply_markup = InlineKeyboardMarkup(
                #         [
                #             [InlineKeyboardButton("Continue...", switch_inline_query_current_chat = "My_Memory_ID: \n" + query_id + "\n=======\n\n")]
                #         ]
                #     )
                )
        except Exception as e:
            pass
            

    # file and photo messages

    async def chat_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # get message
        message = update.effective_message.text
        # group chat without @username
        if (update.effective_chat.type == "group" or update.effective_chat.type == "supergroup") and not ("@" + context.bot.username) in message:
            return
        # remove @username
        if (not message is None) and "@" + context.bot.username in message:
            message = message.replace("@" + context.bot.username, "")

        # check if user is allowed to use this bot
        allowed, acl_message = self.access_manager.check_user_allowed(str(update.effective_user.id))
        if not allowed:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, I can't handle files and photos yet."
        )

    # start command
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello, I'm a ChatGPT bot."
        )

    # clear context command
    async def clear_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        allowed, _ = self.access_manager.check_user_allowed(str(update.effective_user.id))
        if not allowed:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return
        self.message_manager.clear_context(str(update.effective_chat.id))
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

if __name__ == "__main__":
    my_bot = TelegramMessageParser()
    my_bot.run_polling()
