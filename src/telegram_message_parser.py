#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TelegramMessageParser

Enter description of this module

__author__ = Zhiquan Wang
__copyright__ = Copyright 2023
__version__ = 1.4.0
__maintainer__ = Zhiquan Wang
__email__ = i@flynnoct.com
__status__ = Dev
"""

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, InlineQueryHandler, ChosenInlineResultHandler, ContextTypes, filters
import json, os
import logging
import subprocess
from uuid import uuid4
from message_manager import MessageManager
from logging_manager import LoggingManager
from access_manager import AccessManager
from config_loader import ConfigLoader
from azure_parser import AzureParser

from openai_parser import OpenAIParser

class TelegramMessageParser:

    # config_dict = {}

    def __init__(self):

        print("Bot is running, press Ctrl+C to stop...\nRecording log to %s" % ConfigLoader.get("logging", "log_path"))

        # load config
        # with open("config.json") as f:
        #     self.config_dict = json.load(f)

        # init bot
        self.bot = ApplicationBuilder().token(ConfigLoader.get("telegram", "bot_token")).concurrent_updates(True).build()
        # add handlers
        self.add_handlers()

        # init AccessManager
        self.access_manager = AccessManager()

        # init MessageManager
        self.message_manager = MessageManager(self.access_manager)

        # TODO: init AzureParser
        self.azure_parser = AzureParser()

    def run_polling(self):
        LoggingManager.info("Starting polling, the bot is now running...", "TelegramMessageParser")
        self.bot.run_polling()

    def add_handlers(self):
        # command handlers
        self.bot.add_handler(CommandHandler("start", self.start))
        self.bot.add_handler(CommandHandler("clear", self.clear_context))
        self.bot.add_handler(CommandHandler("getid", self.get_user_id))

        # special message handlers
        if ConfigLoader.get("voice_message", "enable_voice"):
            self.bot.add_handler(MessageHandler(filters.VOICE, self.chat_voice))
        if ConfigLoader.get("image_generation", "enable_dalle"):
            self.bot.add_handler(CommandHandler("dalle", self.image_generation))
        if ConfigLoader.get("openai", "enable_custom_system_role"):
            self.bot.add_handler(CommandHandler("role", self.set_system_role))
        self.bot.add_handler(MessageHandler(filters.PHOTO | filters.AUDIO | filters.VIDEO, self.chat_file))

        # inline query handler
        if ConfigLoader.get("telegram", "enable_inline_mode"):
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
        LoggingManager.info("Get a chat message from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
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
        # response = await self.message_manager.get_response(
        #     str(update.effective_chat.id), 
        #     str(update.effective_user.id), 
        #     message
        #     )

        # send first message chunk to user
        async def chat_text_first_chunk_callback(response_message, chat_id, original_message_id):
            message = await context.bot.send_message(
                chat_id = chat_id,
                text = response_message,
                reply_to_message_id = original_message_id,
                allow_sending_without_reply = True
            )
            message_id = message.message_id
            return message_id

        # append message blocks in stream
        async def chat_text_append_chunks_callback(response_message, chat_id, response_message_id):
            await context.bot.edit_message_text(
                chat_id = chat_id,
                message_id = response_message_id,
                text = response_message
            )

        openai_p = OpenAIParser()
        response = await openai_p.get_response_in_stream(
            update.effective_user.id,
            update.effective_chat.id,
            update.effective_message.message_id,
            message,
            chat_text_first_chunk_callback,
            chat_text_append_chunks_callback
        )

        # reply response to user
        # await update.message.reply_text(self.escape_str(response), parse_mode='MarkdownV2')
        LoggingManager.debug("Sending response to user: %s" % str(update.effective_user.id), "TelegramMessageParser")


    # command chat messages
    async def chat_text_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LoggingManager.info("Get a chat message (triggered by command) from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
        # get message
        message = " ".join(context.args)

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
        LoggingManager.debug("Sending response to user: %s" % str(update.effective_user.id), "TelegramMessageParser")
        await update.message.reply_text(response)

    # voice message in private chat, speech to text with Whisper API and process with ChatGPT
    async def chat_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LoggingManager.info("Get a voice message from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
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

        try:
            LoggingManager.debug("Downloading voice message from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
            file_id = update.effective_message.voice.file_id
            new_file = await context.bot.get_file(file_id)
            await new_file.download_to_drive(file_id + ".ogg")

            file_size = os.path.getsize(file_id + ".ogg") / 1000
            # # if < 200kB, convert to wav and send to openai
            # if file_size > 50:
            #     await update.message.reply_text("Sorry, the voice message is too long.")
            #     return

            LoggingManager.debug("Converting voice message from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
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
            LoggingManager.error("Error when processing voice message from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
            await update.message.reply_text("Sorry, something went wrong. Please try again later.")
            return

        # sending record_voice/typing action
        if ConfigLoader.get("voice_message", "tts_reply"):
            action = "record_voice"
        else:
            action = "typing"   
        await context.bot.send_chat_action(
            chat_id = update.effective_chat.id,
            action = action
        )

        # send message to openai
        response = self.message_manager.get_response(
            str(update.effective_chat.id), 
            str(update.effective_user.id), 
            transcript,
            is_voice = True
            )
        LoggingManager.debug("Sending response to user: %s" % str(update.effective_user.id), "TelegramMessageParser")

        if ConfigLoader.get("voice_message", "tts_reply"): # send voice message
            file_id = str(update.effective_user.id) + "_" + str(uuid4())
            self.azure_parser.text_to_speech(response, file_id)
            try:
                if ConfigLoader.get("voice_message", "text_as_caption"):
                    caption = "\"" + transcript + "\"\n\n" + response
                else:
                    caption = ""
                await context.bot.send_voice(
                    chat_id = update.effective_chat.id,
                    voice = open(file_id + ".wav", 'rb'),
                    caption = caption,
                    reply_to_message_id = update.effective_message.message_id,
                    allow_sending_without_reply = True
                    )
            except Exception as e: # if error, send text reply
                await context.bot.send_message(
                    chat_id = update.effective_chat.id,
                    text = "😢 Sorry, something went wrong with Azure TTS Service, contact administrator for more details." + "\n\n\"" + transcript + "\"\n\n" + response,
                    reply_to_message_id = update.effective_message.message_id,
                    allow_sending_without_reply = True
                )
            try:
                os.remove(file_id + ".wav")
            except:
                pass
        else: # send text reply
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "\"" + transcript + "\"\n\n" + response,
                reply_to_message_id = update.effective_message.message_id,
                allow_sending_without_reply = True
            )

    # image_generation command, aka DALLE
    async def image_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LoggingManager.info("Get an image generation command from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
        # remove dalle command from message
        # message = update.effective_message.text.replace("/dalle", "")
        message = " ".join(context.args)

        # send prompt to openai image generation and get image url
        image_url, prompt = self.message_manager.get_generated_image_url(
            str(update.effective_user.id), 
            message
            )

        # if exceeds use limit, send message instead
        if image_url is None:
            LoggingManager.debug("The image generation request from user %s cannot be processed due to %s." % (str(update.effective_user.id), prompt), "TelegramMessageParser")
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
            LoggingManager.debug("Sending generated image to user: %s" % str(update.effective_user.id), "TelegramMessageParser")
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=image_url,
                caption=prompt
            )

    # inline text messages
    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LoggingManager.info("Get a inline query from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
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
        LoggingManager.debug("Sending inline query back to user: %s" % str(update.effective_user.id), "TelegramMessageParser")
        await update.inline_query.answer(results, cache_time=0, is_personal=True)
    
    async def inline_query_result_chosen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LoggingManager.info("Get a inline query result chosen from user %s with message ID %s" % (str(update.effective_user.id), update.chosen_inline_result.inline_message_id), "TelegramMessageParser")
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
            LoggingManager.debug("Editing inline query result message %s from user %s" % (inline_message_id, str(update.effective_user.id)), "TelegramMessageParser")
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
        LoggingManager.info("Get a start command from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello, I'm a ChatGPT bot."
        )

    # clear context command
    async def clear_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LoggingManager.info("Get a clear context command from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
        allowed, _ = self.access_manager.check_user_allowed(str(update.effective_user.id))
        if not allowed:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return
        self.message_manager.clear_context(str(update.effective_chat.id))
        LoggingManager.debug("Context cleared for user: %s" % str(update.effective_user.id), "TelegramMessageParser")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Context cleared."
        )

    # get user id command
    async def get_user_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LoggingManager.info("Get a get user ID command from user: %s, username: %s, first_name: %s, last_name: %s" % (str(update.effective_user.id), update.effective_user.username, update.effective_user.first_name, update.effective_user.last_name), "TelegramMessageParser")

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=str(update.effective_user.id)
        )

    # set system role command
    async def set_system_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        arg_str = " ".join(context.args)
        LoggingManager.info("Set system role to %s from user: %s" % (arg_str, str(update.effective_user.id)), "TelegramMessageParser")
        allowed, _ = self.access_manager.check_user_allowed(str(update.effective_user.id))
        if not allowed:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry, you are not allowed to use this bot."
            )
            return
        reply_message = self.message_manager.set_system_role(str(update.effective_chat.id), str(update.effective_user.id), arg_str)
        await update.message.reply_text(reply_message)

    # unknown command
    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        LoggingManager.info("Get an unknown command from user: %s" % str(update.effective_user.id), "TelegramMessageParser")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, I didn't understand that command."
        )

if __name__ == "__main__":
    my_bot = TelegramMessageParser()
    my_bot.run_polling()
