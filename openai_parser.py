#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ChatGPT Telegram Bot

Description to be added.

__author__ = Zhiquan Wang
__copyright__ = Copyright 2023
__version__ = 1.0
__maintainer__ = Zhiquan Wang
__email__ = contact@flynmail.com
__status__ = Dev
"""

import openai, json, os
import datetime

import time,sys,traceback,math

LOGLEVEL = {0:"DEBUG",1:"INFO",2:"WARN",3:"ERR",4:"FATAL"}
LOGFILE  = "bot.log"

def log(*msg,l=1,end="\n",logfile=LOGFILE):
    msg=", ".join(map(str,msg))
    st=traceback.extract_stack()[-2]
    lstr=LOGLEVEL[l]
    now_str="%s %03d"%(time.strftime("%y/%m/%d %H:%M:%S",time.localtime()),math.modf(time.time())[0]*1000)
    perfix="%s [%s,%s:%03d]"%(now_str,lstr,st.name,st.lineno)
    if l<3:
        tempstr="%s %s%s"%(perfix,str(msg),end)
    else:
        tempstr="%s %s:\n%s%s"%(perfix,str(msg),traceback.format_exc(limit=5),end)
    print(tempstr,end="")
    if l>=1:
        with open(logfile,"a") as f:
            f.write(tempstr)

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
        response = openai.ChatCompletion.create(model = "gpt-3.5-turbo-0301",
                                            messages = [
                                                {"role": "system", "content": "You are a helpful assistant"},
                                                {"role": "user", "content": message}
                                            ])
        return response["choices"][0]["message"]["content"]
    
    def get_response(self, userid, context_messages):
        context_messages.insert(0, {"role": "system", "content": "You are a helpful assistant"})
        try:
            response = openai.ChatCompletion.create(model = "gpt-3.5-turbo-0301",
                                                messages = context_messages)
            self.update_usage(response["usage"]["total_tokens"], userid)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return str(e) + "\nSorry, I am not feeling well. Please try again."

    def speech_to_text(self, userid, audio_file):
        # transcript = openai.Audio.transcribe("whisper-1", audio_file, language="zh")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

    def image_generation(self, userid, prompt):
        response = openai.Image.create(prompt = prompt, n=1, size = "512x512", user = userid)
        image_url = response["data"][0]["url"]
        # self.update_image_generation_usage(userid)
        # for debug use
        # image_url = "https://catdoctorofmonroe.com/wp-content/uploads/2020/09/iconfinder_cat_tied_275717.png"
        return image_url
    
    def update_image_generation_usage(self, userid):
        # get time
        usage_file_name = datetime.datetime.now().strftime("%Y%m") + "_image_generation_usage.json"
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        # create usage folder
        if not os.path.exists("./usage"):
            os.makedirs("./usage")
        # load usage or create new
        if os.path.exists("./usage/" + usage_file_name):
            with open("./usage/" + usage_file_name) as f:
                self.usage_dict = json.load(f)
        else:
            self.usage_dict = {}
        # update usage
        if now not in self.usage_dict:
            self.usage_dict[now] = {}
        if userid not in self.usage_dict[now]:
            self.usage_dict[now][userid] = {"requests": 0}
        self.usage_dict[now][userid]["requests"] += 1
        # save usage
        with open("./usage/" + usage_file_name, "w") as f:
            json.dump(self.usage_dict, f)

    
    def update_usage(self, total_tokens, userid):
        # get time
        usage_file_name = datetime.datetime.now().strftime("%Y%m") + "_usage.json"
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        # create usage folder
        if not os.path.exists("./usage"):
            os.makedirs("./usage")
        # load usage or create new
        if os.path.exists("./usage/" + usage_file_name):
            with open("./usage/" + usage_file_name) as f:
                self.usage_dict = json.load(f)
        else:
            self.usage_dict = {}
        # update usage
        if now not in self.usage_dict:
            self.usage_dict[now] = {}
        if userid not in self.usage_dict[now]:
            self.usage_dict[now][userid] = {"tokens": 0, "requests": 0}
        self.usage_dict[now][userid]["tokens"] += total_tokens
        self.usage_dict[now][userid]["requests"] += 1
        # save usage
        with open("./usage/" + usage_file_name, "w") as f:
            json.dump(self.usage_dict, f)

if __name__ == "__main__":
    openai_parser = OpenAIParser()
    # print(openai_parser._get_single_response("Tell me a joke."))
    print(openai_parser.get_response("123", [{"role": "user", "content": "Tell me a joke."}]))