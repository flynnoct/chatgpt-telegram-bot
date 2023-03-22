import time
import datetime
import os
import logging
from access_manager import AccessManager
from chat_session import ChatSession
from openai_parser import OpenAIParser
from config_loader import ConfigLoader


class MessageManager:

    userDict = {}
    # config_dict = {}
    openai_parser = None
    access_manager = None
    
    def __init__(self, access_manager):
        self.openai_parser = OpenAIParser()
        self.access_manager = access_manager
        # setup logger
        self.logger = logging.getLogger("MessageManager")
        
        self.access_manager = AccessManager()

    def get_response(self, id, user, message):
        self.logger.debug("Get response for user: %s" % id)
        t = time.time()

        # (permission, clue) = self.access_manager.check_user_allowed(user)
        # if permission == False:
        #     return clue

        if id not in self.userDict:
            # new user
            self.userDict[id] = ChatSession(t, message)
        else:
            self.userDict[id].update(t, message, "user")
        
        # send user info for statistics
        (answer, usage) = self.__sendMessage(
            user, self.userDict[id].messageList)
        self.userDict[id].update(t, answer, "assistant")
        self.access_manager.update_usage_info(user, usage, "chat")
        return answer

    def clear_context(self, id):
        self.logger.debug("Clear context for user: %s" % id)
        try:
            self.userDict[id].clear_context(time.time())
        except Exception as e:
            print(e)

    def get_generated_image_url(self, user, prompt, num=1):
        self.logger.debug("Get generated image for user: %s" % user)

        if user in ConfigLoader.get("super_users"):
            url, _ = self.openai_parser.image_generation(user, prompt)
            return (url, "Hey boss, it's on your account. 💰")

        (permission, clue) = self.access_manager.check_image_generation_allowed(user, num)
        if permission == False:
            return None, clue

        (url, usage) = self.openai_parser.image_generation(user, prompt)

        self.access_manager.update_usage_info(user, usage, "image")
        return url, clue

    def get_transcript(self, user, audio_file):
        self.logger.debug("Get voice transcript for user: %s" % user)
        # (permission, clue) = self.access_manager.check_user_allowed(user)
        # if permission == False:
        #     return clue

        return self.openai_parser.speech_to_text(user, audio_file)
    
    def set_system_role(self, id, user, message):
        self.logger.debug("Set system role for chat: %s" % id)
        t = time.time()
        if id not in self.userDict:
            self.userDict[id] = ChatSession(t, message)       
        self.userDict[id].set_system_role(t, message)   
        
        # send first sentence
        (answer, usage) = self.__sendMessage(user, 
                [{"role": "system", "content": message}, 
                 {"role": "user", "content":"Say hello to me."}])
        self.access_manager.update_usage_info(user, usage, "chat")
        return answer
        

    def __sendMessage(self, user, messageList):
        ans = self.openai_parser.get_response(user, messageList)
        return ans
    
    
if __name__ == "__main__":
    acm = AccessManager()
    msm = MessageManager(acm)
