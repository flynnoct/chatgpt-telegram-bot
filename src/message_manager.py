import time
import datetime
import os
import json
from access_manager import AccessManager
from chat_session import ChatSession
from openai_parser import OpenAIParser

class MessageManager:
    
    userDict = {}
    config_dict = {}
    openai_parser = None
    access_manager = None
    
    def __init__(self):
        self.openai_parser = OpenAIParser()
        self.access_manager = AccessManager()
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)

    
    def get_response(self, id, user, message):

        t = time.time()
        
        (permission, clue) = self.access_manager.check_user_allowed(user)
        if permission == False:
            return clue
          
        if id not in self.userDict:
            # new user
            self.userDict[id] = ChatSession(t, message)
        else:
            self.userDict[id].update(t, message, "user")
           
        # send user info for statistics 
        (answer, usage) = self.__sendMessage(user, self.userDict[id].messageList)
        self.userDict[id].update(t, answer, "assistant")
        self.access_manager.update_usage_info(user, usage, "chat")
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
            return (url, "Hey boss, it's on your account. 💰")
        ############################

        (permission, clue) = self.access_manager.check_image_generation_allowed(user)
        if permission == False:
            return clue

        (url, usage) = self.openai_parser.image_generation(user, prompt)
        
        self.access_manager.update_usage_info(user, usage, "image")
        return (url, clue)
            
    def get_transcript(self, user, audio_file):
        try:
            return self.openai_parser.speech_to_text(user, audio_file)
        except Exception as e:
            print(e)
            return ""
        
           
    def __sendMessage(self, user, messageList):
        ans = self.openai_parser.get_response(user, messageList)
        return ans