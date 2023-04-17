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

class OpenAIParser:

    # config_dict = {}

    def __init__(self):
        # setup logger
        self.logger = logging.getLogger("OpenAIParser")

        # load config
        # with open("config.json") as f:
        #     self.config_dict = json.load(f)
        # init openai
        # openai.organization = self.config_dict["ORGANIZATION"] if "ORGANIZATION" in self.config_dict else "Personal"
        openai.api_key = ConfigLoader.get("openai_api_key")

    def _get_single_response(self, message):
        response = openai.ChatCompletion.create(model = "gpt-3.5-turbo",
                                            messages = [
                                                {"role": "system", "content": "You are a helpful assistant"},
                                                {"role": "user", "content": message}
                                            ])
        return response["choices"][0]["message"]["content"]
    
    def get_response(self, userid, context_messages):
        self.logger.debug("Get OpenAI GPT response for user: %s" % userid)
        # context_messages.insert(0, {"role": "system", "content": "You are a helpful assistant"})
        try:

            def timeout_handler(signum, frame):
                raise Exception("Timeout")
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(ConfigLoader.get("openai_timeout")))
            #### Timer ####
            response = openai.ChatCompletion.create(
                model = "gpt-3.5-turbo",
                messages = context_messages
                )
            ###############
            signal.alarm(0)
            return (response["choices"][0]["message"]["content"], response["usage"]["total_tokens"])
        except Exception as e:
            self.logger.error("OpenAI GPT request for user %s with error: %s" % (userid, str(e)))
            return ("Oops, something went wrong with OpenAI. Please try again later.", 0)

    def speech_to_text(self, userid, audio_file):
        self.logger.debug("Get OpenAI Speech to Text for user: %s" % userid)
        # transcript = openai.Audio.transcribe("whisper-1", audio_file, language="zh")
        try:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        except Exception as e:
            self.logger.error("OpenAI Speech to Text request for user %s with error: %s" % (userid, str(e)))
            return ""
        return transcript["text"]

    def image_generation(self, userid, prompt):
        self.logger.debug("Get OpenAI Image Generation for user: %s" % userid)
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