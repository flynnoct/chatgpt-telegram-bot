#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""ChatGPT Telegram Bot

Description to be added.

__author__ = Zhiquan Wang
__copyright__ = Copyright 2023
__version__ = 1.2.2
__maintainer__ = Zhiquan Wang
__email__ = contact@flynmail.com
__status__ = Dev
"""

import openai, json, os
import datetime
import logging
import signal
from config_loader import ConfigLoader
from logging_manager import LoggingManager
from helpers import num_tokens_from_messages

class OpenAIParser:

    # config_dict = {}

    def __init__(self):

        # load config
        # with open("config.json") as f:
        #     self.config_dict = json.load(f)
        # init openai
        # openai.organization = self.config_dict["ORGANIZATION"] if "ORGANIZATION" in self.config_dict else "Personal"
        openai.api_key = ConfigLoader.get("openai", "api_key")

    async def _get_single_response(self, message):
        response = await openai.ChatCompletion.acreate(model = ConfigLoader.get("openai", "chat_model"),
                                                messages = [
                                                    {"role": "system", "content": "You are a helpful assistant"},
                                                    {"role": "user", "content": message}
                                                    ]
                                                )
        return response["choices"][0]["message"]["content"]

    async def get_response(self, userid, context_messages):
        LoggingManager.debug("Get OpenAI GPT response for user: %s" % userid, "OpenAIParser")
        # context_messages.insert(0, {"role": "system", "content": "You are a helpful assistant"})
        try:

            def timeout_handler(signum, frame):
                raise Exception("Timeout")
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(ConfigLoader.get("openai", "api_timeout")))
            #### Timer ####
            response = await openai.ChatCompletion.acreate(
                model = ConfigLoader.get("openai", "chat_model"),
                messages = context_messages
                )
            ###############
            signal.alarm(0)
            return (response["choices"][0]["message"]["content"], response["usage"]["total_tokens"])
        except Exception as e:
            LoggingManager.error("OpenAI GPT request for user %s with error: %s" % (userid, str(e)), "OpenAIParser")
            return ("Oops, something went wrong with OpenAI. Please try again later.", 0)

    async def get_response_in_stream(self, userid, chat_id, original_message_id, context_messages, send_message_callback, edit_message_callback):
        LoggingManager.debug("Get OpenAI GPT response in stream for user: %s" % userid, "OpenAIParser")
        response = await openai.ChatCompletion.acreate(
            model = ConfigLoader.get("openai", "chat_model"),
            messages = context_messages,
            stream = True
            )
        collected_messages = ""
        response_message_id = ""
        first_chunk = True
        increased_len = 0
        async for chunk in response:
            chunk_delta = chunk['choices'][0]['delta']
            chunk_finish_reason = chunk['choices'][0]['finish_reason']
            if chunk_finish_reason == "stop":
                if first_chunk:
                    await send_message_callback(
                        collected_messages,
                        chat_id,
                        original_message_id,
                        finished = True
                        )
                else:
                    await edit_message_callback(
                        collected_messages,
                        chat_id,
                        response_message_id,
                        finished = True
                        )
                context_messages.append({"role": "assistant", "content": collected_messages})
                token_used = num_tokens_from_messages(context_messages, ConfigLoader.get("openai", "chat_model"))
                return (collected_messages, token_used)
            else:
                if "content" in chunk_delta:
                    increased_len += 1
                    collected_messages += chunk_delta["content"]
                    if first_chunk and increased_len > 32:
                        first_chunk = False
                        response_message_id = await send_message_callback(
                            collected_messages,
                            chat_id,
                            original_message_id
                            )
                        increased_len = 0
                    elif increased_len > 64:
                        await edit_message_callback(
                            collected_messages,
                            chat_id,
                            response_message_id,
                            )
                        increased_len = 0
        # TODO: handle usage and timeout
        context_messages.append({"role": "assistant", "content": collected_messages})
        token_used = num_tokens_from_messages(context_messages, ConfigLoader.get("openai", "chat_model"))
        return (collected_messages, token_used)


    def speech_to_text(self, userid, audio_file):
        LoggingManager.debug("Get OpenAI Speech to Text for user: %s" % userid, "OpenAIParser")
        # transcript = openai.Audio.transcribe("whisper-1", audio_file, language="zh")
        try:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        except Exception as e:
            LoggingManager.error("OpenAI Speech to Text request for user %s with error: %s" % (userid, str(e)), "OpenAIParser")
            return ""
        return transcript["text"]

    def image_generation(self, userid, prompt):
        LoggingManager.debug("Get OpenAI Image Generation for user: %s" % userid, "OpenAIParser")
        response = openai.Image.create(prompt = prompt, n=1, size = "512x512", user = userid)
        image_url = response["data"][0]["url"]
        # for debug use
        # image_url = "https://catdoctorofmonroe.com/wp-content/uploads/2020/09/iconfinder_cat_tied_275717.png"
        usage = 1 # reserve for future use
        return (image_url, usage)

if __name__ == "__main__":
    openai_parser = OpenAIParser()
    # print(openai_parser._get_single_response("Tell me a joke."))
    print(openai_parser.get_response("123", [{"role": "system", "content": "You are a cat and only can say Meaw"}, {"role": "user", "content": "Say something to me."}]))