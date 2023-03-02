import time
from user_context import UserContext
from openai_parser import OpenAIParser

class MessageManager:
    
    userDict = {}
    openai_parser = None
    
    def __init__(self):
        self.openai_parser = OpenAIParser()
    
    def get_response(self, user, message):
        t = time.time()
        
        if user not in self.userDict:
            # new user
            self.userDict[user] = UserContext(t, message)
        else:
            self.userDict[user].update(t, message, "user")
            
        answer = self.__sendMessage(user, self.userDict[user].messageList)
        self.userDict[user].update(t, answer, "assistant")
        return answer
    
    def clear_context(self, user):
        try:
            self.userDict[user].clear_context()
        except Exception as e:
            print(e)
            
    def __sendMessage(self, user, messageList):
        ans = self.openai_parser.get_response(user, messageList)
        return ans
    