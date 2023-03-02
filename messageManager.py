import time
from userContext import UserContext
from openai_parser import OpenAIParser

class MessageManager:
    
    userDict = {}
    openai_parser = None
    
    def __init__(self):
        pass
    
    def recvMessage(self, user, message):
        t = time.time()
        
        if user not in self.userDict:
            # new user
            print("here is new user")
            self.userDict[user] = UserContext(t, message)
        else:
            self.userDict[user].update(t, message, "user")
            
        answer = self.__sendMessage(user, self.userDict[user].messageList)
        self.userDict[user].update(t, answer, "assistant")
        return answer
            
    def __sendMessage(self, user, messageList):
        ans = openai_parser.get_response(user, messageList)
        return ans
    