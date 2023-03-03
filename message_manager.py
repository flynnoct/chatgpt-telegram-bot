import time
from user_context import UserContext
from openai_parser import OpenAIParser

class MessageManager:
    
    userDict = {}
    openai_parser = None
    
    def __init__(self):
        self.openai_parser = OpenAIParser()
    
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
            
    def get_transcript(self, user, audio_file):
        try:
            self.openai_parser.speech_to_text(user, audio_file)
        except Exception as e:
            print(e)
            
    def __sendMessage(self, user, messageList):
        ans = self.openai_parser.get_response(user, messageList)
        return ans
    