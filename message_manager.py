import time
import datetime
import os
import json
from user_context import UserContext
from openai_parser import OpenAIParser

class MessageManager:
    
    userDict = {}
    openai_parser = None
    config_dict = {}
    user_image_generation_usage_dict = {}
    user_chat_usage_dict = {}
    # Fixed by @Flynn
    usage_dict = {}
    
    def __init__(self):
        self.openai_parser = OpenAIParser()
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)
        
        (image_usage_file_name, now) = self.__get_usage_filename_and_key("image")
        if not os.path.exists("./usage"):
            os.makedirs("./usage")
        if os.path.exists("./usage/" + image_usage_file_name):
            with open("./usage/" + image_usage_file_name) as f:
                self.user_image_generation_usage_dict = json.load(f)
        else:
            self.user_image_generation_usage_dict = {}
            
        # Fixed by @Flynn
        if now not in self.user_image_generation_usage_dict:
            self.user_image_generation_usage_dict[now] = {}

    
    def get_response(self, id, user, message):

        t = time.time()
        
        if id not in self.userDict:
            # new user
            self.userDict[id] = UserContext(t, message)
        else:
            self.userDict[id].update(t, message, "user")
           
        # send user info for statistics 
        answer = self.__sendMessage(user, self.userDict[id].messageList)
        self.userDict[id].update(t, answer, "assistant")
        return answer
    
    def clear_context(self, id):
        try:
            self.userDict[id].clear_context(time.time())
        except Exception as e:
            print(e)
            
    def get_generated_image_url(self, user, prompt):

        # Temporary fix by @Flynn, will be fixed in the next version
        with open("config.json") as f:
            super_users = json.load(f)["super_users"]
        if user in super_users:
            url = self.openai_parser.image_generation(user, prompt)
            return (url, "Boss, it's on your account. 💰")
        ############################


        used_num = self.__check_image_generation_limit(user)
        if used_num >= self.config_dict["image_generation_limit_per_day"]:
            return (None, "You have reached the limit.")
        else:
            self.__update_usage_info(user, used_num+1, "image")
            url = self.openai_parser.image_generation(user, prompt)
            # Temporary fix by @Flynn
            return (url, "You have used " + str(used_num + 1) + " / " + 
                    str(self.config_dict["image_generation_limit_per_day"]) + 
                    " times.")
            
    def get_transcript(self, user, audio_file):
        try:
            return self.openai_parser.speech_to_text(user, audio_file)
        except Exception as e:
            print(e)
            return ""
        
    def __get_usage_filename_and_key(self, chatORimage):
        if chatORimage == "chat":
            filename = "_char_usage.json"
        elif chatORimage == "image":
            filename = "_image_generation_usage.json"
        return (datetime.datetime.now().strftime("%Y%m") + filename, 
                datetime.datetime.now().strftime("%Y-%m-%d"))
            
    def __sendMessage(self, user, messageList):
        ans = self.openai_parser.get_response(user, messageList)
        return ans
    
    def __check_image_generation_limit(self, user):
        (_, now) = self.__get_usage_filename_and_key("image")
        if now not in self.user_image_generation_usage_dict:
            self.__update_dict("image")
        if user not in self.user_image_generation_usage_dict[now]:
            used_num = 0
        else:
            used_num = self.user_image_generation_usage_dict[now][user]
        return used_num
    
    def __update_dict(self, chatORimage):
        (filename, now) = self.__get_usage_filename_and_key(chatORimage)
        if not os.path.exists("./usage/" + filename):
            if chatORimage == "image":
                self.user_image_generation_usage_dict = {}
            elif chatORimage == "chat":
                self.user_chat_usage_dict = {}
            return  
        if chatORimage == "image" and now not in self.user_image_generation_usage_dict:
            self.user_image_generation_usage_dict[now] = {}
        elif chatORimage == "chat" and now not in self.user_chat_usage_dict:
            self.user_chat_usage_dict[now] = {}       
    
    def __update_usage_info(self, user, used_num, chatORimage):
        (filename, now) = self.__get_usage_filename_and_key(chatORimage)
        if now not in self.user_image_generation_usage_dict:
            self.__update_dict(chatORimage)
        if chatORimage == "image":
            self.user_image_generation_usage_dict[now][user] = used_num
            with open("./usage/" + filename, "w") as f:
                json.dump(self.user_image_generation_usage_dict, f)
        elif chatORimage == "chat":
            self.user_chat_usage_dict[now][user] = used_num
            # with open("./usage/" + filename, "w") as f:
            #     json.dump(self.user_chat_usage_dict, f)