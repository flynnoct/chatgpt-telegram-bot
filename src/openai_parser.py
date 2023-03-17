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
import requests

class OpenAIParser:

    config_dict = {}

    def __init__(self):
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)
        # init openai
        # openai.organization = self.config_dict["ORGANIZATION"] if "ORGANIZATION" in self.config_dict else "Personal"
        openai.api_key = self.config_dict["openai_api_key"]

    def _get_single_response(self, message):
        response = openai.ChatCompletion.create(model = "gpt-3.5-turbo",
                                            messages = [
                                                {"role": "system", "content": "You are a helpful assistant"},
                                                {"role": "user", "content": message}
                                            ])
        return response["choices"][0]["message"]["content"]

    def get_response(self, userid, context_messages):
        context_messages.insert(0, {"role": "system", "content": "You are a helpful assistant"})
        try:
            response = openai.ChatCompletion.create(model = "gpt-3.5-turbo",
                                                messages = context_messages)
            return (response["choices"][0]["message"]["content"], response["usage"]["total_tokens"])
        except Exception as e:
            return (str(e) + "\nSorry, I am not feeling well. Please try again.", 0)

    def speech_to_text(self, userid, audio_file):
        # transcript = openai.Audio.transcribe("whisper-1", audio_file, language="zh")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

    def image_generation(self, userid, prompt):
        response = openai.Image.create(prompt = prompt, n=1, size = "512x512", user = userid)
        image_url = response["data"][0]["url"]
        # for debug use
        # image_url = "https://catdoctorofmonroe.com/wp-content/uploads/2020/09/iconfinder_cat_tied_275717.png"
        usage = 1 # reserve for future use
        return (image_url, usage)

    def get_usage(self):
        """Get the usage of the API for the last 30 days.

        Example API call:
            https://api.openai.com/dashboard/billing/usage?end_date=2023-04-01&start_date=2023-03-01

        The API call return a json with a key total_usage with contains the cents of dollar used in the specified period.

        Return the usage in dollars.
        """
        today = datetime.date.today()
        last_month = today - datetime.timedelta(days=30)
        url = "https://api.openai.com/dashboard/billing/usage?end_date={}&start_date={}".format(today, last_month)
        headers = {"Authorization": "Bearer {}".format(self.config_dict["openai_api_key"])}

        req = requests.get(url, headers=headers)
        usage = req.json()["total_usage"]/100

        return usage

if __name__ == "__main__":
    openai_parser = OpenAIParser()
    # print(openai_parser._get_single_response("Tell me a joke."))
    print(openai_parser.get_response("123", [{"role": "user", "content": "Tell me a joke."}]))
