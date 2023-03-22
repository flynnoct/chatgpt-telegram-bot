import copy
import logging
from config_loader import ConfigLoader

class ChatSession:
    
    # __latestTime = 0
    # __messageList = []
    
    def __init__(self, contactTime, message):
        # setup logger
        self.logger = logging.getLogger("ChatSession")
        # first message
        self.__messageList = []
        self.__system_role = ConfigLoader.get('system_role')
        self.__latestTime = contactTime
        self.__messageList.append(
            {"role": "user", "content": message}
        )
            
    def __repr__(self):
        return str(self.messageList) + '\n'
    
    @property
    def messageList(self):
        return [{"role": "system", "content": self.__system_role}] + self.__messageList
    
    def set_system_role(self, contactTime, message):
        self.clear_context(contactTime)
        self.__system_role = message
    
    def update(self, contactTime, message, source):
        # check time
        if (source == "user") and (contactTime - self.__latestTime > ConfigLoader.get("wait_time")) :
            # refresh message list
            self.logger.info("Context expired, clear context.")
            self.__messageList.clear()
            self.__system_role = ConfigLoader.get('system_role')
        self.__latestTime = contactTime
        self.__messageList.append(
            {"role": source, "content": message}
        )
        
    def clear_context(self, clear_time):
        self.__latestTime = clear_time
        self.__messageList.clear()
        self.__system_role = ConfigLoader.get('system_role')
        
if __name__ == "__main__":
    chatA = ChatSession(1, "a")
    chatB = ChatSession(2, "b")
    print(chatA)
    print(chatB)
    chatA.update(3, "c", "user")
    print(chatA)
    print(chatB)
        