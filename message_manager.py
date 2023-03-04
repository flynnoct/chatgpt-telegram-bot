import time
import json
from user_context import UserContext
from openai_parser import OpenAIParser

class MessageManager:
    
    userDict = {}
    openai_parser = None
    config_dict = {}
    
    def __init__(self):
        self.openai_parser = OpenAIParser()
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)
    
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
        use_num = self.__check_image_generation_limit(user)
        if use_num >= self.config_dict["image_generation_limit_per_day"]:
            return (None, "You have reached the limit.")
        else:
            url = self.openai_parser.image_generation(user, prompt)
            return (url, "You have used " + str(use_num) + " / " + 
                    str(self.config_dict["image_generation_limit_per_day"]) + 
                    " times.")
            
    def get_transcript(self, user, audio_file):
        try:
            return self.openai_parser.speech_to_text(user, audio_file)
        except Exception as e:
            print(e)
            return ""
            
    def __sendMessage(self, user, messageList):
        ans = self.openai_parser.get_response(user, messageList)
        return ans
    
    def __check_image_generation_limit(self, user):
        return 0
    