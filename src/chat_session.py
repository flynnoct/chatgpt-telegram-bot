import json
import copy
import logging

class ChatSession:
    
    __latestTime = 0
    __messageList = []
    config_dict = {}
    
    def __init__(self, contactTime, message):
        # setup logger
        self.logger = logging.getLogger("ChatSession")
        # first message
        self.__messageList = copy.deepcopy([])
        self.__latestTime = contactTime
        self.__messageList.append(
            {"role": "user", "content": message}
        )
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)
            
    def __repr__(self):
        return str(self.messageList) + '\n'
    
    @property
    def messageList(self):
        return str(self.__latestTime) + " " +  str(self.__messageList)
    
    def update(self, contactTime, message, source):
        # check time
        if (source == "user") and (contactTime - self.__latestTime > self.config_dict["wait_time"]) :
            # refresh message list
            self.logger.info("Context expired, clear context.")
            self.__messageList.clear()
        self.__latestTime = contactTime
        self.__messageList.append(
            {"role": source, "content": message}
        )
        
    def clear_context(self, clear_time):
        self.__latestTime = clear_time
        self.__messageList.clear()
        
if __name__ == "__main__":
    chatA = ChatSession(1, "a")
    chatB = ChatSession(2, "b")
    print(chatA)
    print(chatB)
    chatA.update(3, "c", "user")
    print(chatA)
    print(chatB)
        