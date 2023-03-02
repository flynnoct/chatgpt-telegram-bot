import time
from userContext import UserContext

class MessageManager:
    
    userDict = {}
    
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
            
        answer = self.__sendMessage(user)
        self.userDict[user].update(t, answer, "assistant")
        print(self.userDict[user])
            
    def __sendMessage(self, user):
        ans = "0.0"
        return ans
    