import json
import copy

class UserContext:
    
    latestTime = 0
    messageList = []
    config_dict = {}
    
    def __init__(self, contactTime, message):
        # first message
        self.messageList = copy.deepcopy([])
        self.latestTime = contactTime
        self.messageList.append(
            {"role": "user", "content": message}
        )
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)
            
    def __repr__(self):
        return str(self.messageList) + '\n'
    
    def update(self, contactTime, message, source):
        # check time
        if (source == "user") and (contactTime - self.latestTime > self.config_dict["wait_time"]) :
            # refresh message list
            self.messageList.clear()
        self.latestTime = contactTime
        self.messageList.append(
            {"role": source, "content": message}
        )
        