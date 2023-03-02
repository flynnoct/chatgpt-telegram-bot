import json
import copy

class UserContext:
    
    __latestTime = 0
    __messageList = []
    config_dict = {}
    
    def __init__(self, contactTime, message):
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
        return self.__messageList
    
    def update(self, contactTime, message, source):
        # check time
        if (source == "user") and (contactTime - self.__latestTime > self.config_dict["wait_time"]) :
            # refresh message list
            self.__messageList.clear()
        self.__latestTime = contactTime
        self.__messageList.append(
            {"role": source, "content": message}
        )
        
    def clear_context(self, clear_time):
        self.__latestTime = clear_time
        self.__messageList.clear()
        