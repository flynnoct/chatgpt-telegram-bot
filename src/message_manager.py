import time
import datetime
import os
import logging
from access_manager import AccessManager
from chat_session import ChatSession
from openai_parser import OpenAIParser
from config_loader import ConfigLoader
from logging_manager import LoggingManager


class MessageManager:
    
    def __init__(self, access_manager):
        self.__openai_parser = OpenAIParser()
        self.__access_manager = access_manager
        self.__userDict = {}

    def get_response(self, id, user, message, is_voice = False):
        LoggingManager.debug("Get response for user: %s" % id, "MessageManager")
        t = time.time()

        if id not in self.__userDict:
            # new user
            self.__userDict[id] = ChatSession(t, message)
        else:
            self.__userDict[id].update(t, message, "user")
            
        if is_voice == True:
            self.__userDict[id].set_voice()
        
        # send user info for statistics
        (answer, usage) = self.__sendMessage(
            user, self.__userDict[id].messageList)
        
        if is_voice == True:
            self.__userDict[id].unset_voice()
        
        self.__userDict[id].update(t, answer, "assistant")
        self.__access_manager.update_usage_info(user, usage, "chat")
        return answer

    def clear_context(self, id):
        LoggingManager.debug("Clear context for user: %s" % id, "MessageManager")
        try:
            self.__userDict[id].clear_context(time.time())
        except Exception as e:
            print(e)

    def get_generated_image_url(self, user, prompt, num=1):
        LoggingManager.debug("Get generated image for user: %s" % user, "MessageManager")

        if user in ConfigLoader.get("user_management", "super_users"):
            url, _ = self.__openai_parser.image_generation(user, prompt)
            return (url, "Hey boss, it's on your account. 💰")

        (permission, clue) = self.__access_manager.check_image_generation_allowed(user, num)
        if permission == False:
            return None, clue

        (url, usage) = self.__openai_parser.image_generation(user, prompt)

        self.__access_manager.update_usage_info(user, usage, "image")
        return url, clue

    def get_transcript(self, user, audio_file):
        LoggingManager.debug("Get voice transcript for user: %s" % user, "MessageManager")

        return self.__openai_parser.speech_to_text(user, audio_file)
    
    def set_system_role(self, id, user, message):
        LoggingManager.debug("Set system role for chat: %s" % id, "MessageManager")
        t = time.time()
        if id not in self.__userDict:
            self.__userDict[id] = ChatSession(t, message)       
        self.__userDict[id].set_system_role(t, message)   
        
        # send first sentence
        (answer, usage) = self.__sendMessage(user, 
                [{"role": "system", "content": message}, 
                 {"role": "user", "content":"Say hello to me."}])
        self.__access_manager.update_usage_info(user, usage, "chat")
        return answer
        

    def __sendMessage(self, user, messageList):
        ans = self.__openai_parser.get_response(user, messageList)
        return ans
    
    
if __name__ == "__main__":
    acm = AccessManager()
    msm = MessageManager(acm)
