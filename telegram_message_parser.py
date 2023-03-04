#!/usr/bin/env python3
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
import json, os
from message_manager import MessageManager

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

        # init MessageManager
        self.message_manager = MessageManager()

        # start bot
        self.bot.run_polling()

    def add_handlers(self):
        self.bot.add_handler(CommandHandler("start", self.start))
        self.bot.add_handler(CommandHandler("clear", self.clear_context))
        self.bot.add_handler(CommandHandler("getid", self.get_user_id))
        if self.config_dict["enable_voice"]:
            self.bot.add_handler(MessageHandler(filters.VOICE, self.chat_voice))
        if self.config_dict["enable_dalle"]:
            self.bot.add_handler(CommandHandler("dalle", self.image_generation))
        self.bot.add_handler(MessageHandler(filters.PHOTO | filters.AUDIO | filters.VIDEO, self.chat_file))
        self.bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.chat_text))
        self.bot.add_handler(MessageHandler(filters.COMMAND, self.unknown))

    # chat messages
    async def chat_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # get message
        message = update.effective_message.text
        # group chat without @username
        if update.effective_chat.type == "group" or update.effective_chat.type == "supergroup":
            if not ("@" + context.bot.username) in message:
                return
            else:
                # remove @username
                message = message.replace("@" + context.bot.username, "")

        # check if user is allowed to use this bot
        if not self.check_user_allowed(str(update.effective_user.id)):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, you are not allowed to use this bot. Contact the bot owner for more information."
            )
            return

        # sending typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        # send message to openai
        response = self.message_manager.get_response(str(update.effective_chat.id), str(update.effective_user.id), message)
        # reply response to user
        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id,
        #     text=response
        # )
        await update.message.reply_text(response)

    # voice message in private chat, speech to text with Whisper API and process with ChatGPT
    async def chat_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # check if it's a private chat
        if not update.effective_chat.type == "private":
            return
        
        # check if user is allowed to use this bot
        if not self.check_user_allowed(str(update.effective_user.id)):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, you are not allowed to use this bot. Contact the bot owner for more information."
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

            subprocess.call(['ffmpeg', '-i', file_id + '.ogg', file_id + '.wav'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with open(file_id + ".wav", "rb") as audio_file:
                transcript = self.message_manager.get_transcript(str(update.effective_user.id), audio_file)
            os.remove(file_id + ".ogg")
            os.remove(file_id + ".wav")
            
        except Exception as e:
            await update.message.reply_text("Sorry, something went wrong. Please try again later.")
            return

        response = self.message_manager.get_response(str(update.effective_chat.id), str(update.effective_user.id), transcript)
        await update.message.reply_text("\"" + transcript + "\"\n\n" + response)

    # image_generation command, aka DALLE
    async def image_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # remove dalle command from message
        message = update.effective_message.text.replace("/dalle", "")

        # send prompt to openai image generation and get image url
        image_url, prompt = self.message_manager.get_generated_image_url(str(update.effective_user.id), message)

        # send image to user
        # await context.bot.send_photo(
        #     chat_id=update.effective_chat.id,
        #     photo=image_url,
        #     caption=prompt,
        # )

        # if exceeds use limit, send message instead
        if image_url is None:
            # sending typing action
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
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
                chat_id = update.effective_chat.id,
                document = image_url,
                caption = prompt
            )


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
        if not self.check_user_allowed(str(update.effective_user.id)):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, you are not allowed to use this bot. Contact the bot owner for more information."
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
    


