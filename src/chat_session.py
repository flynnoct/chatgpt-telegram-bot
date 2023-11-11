import copy
import logging
import asyncio
from config_loader import ConfigLoader
from logging_manager import LoggingManager

class ChatSession:
    
    # __latestTime = 0
    # __messageList = []
    
    def __init__(self, contactTime):
        # first message
        self.__messageList = []
        self.__system_role = ConfigLoader.get("openai", "default_system_role")
        self.__latestTime = contactTime
        self.no_context_mode = False
        self.lock = asyncio.Lock()
            
    def __repr__(self):
        return str(self.messageList) + '\n'
    
    @property
    def messageList(self):
        return [{"role": "system", "content": self.__system_role}] + self.__messageList
    
    def set_system_role(self, contactTime, message):
        self.clear_all(contactTime)
        self.__system_role = message
    
    def update(self, contactTime, message, source):
        # check time
        if (source == "user") and (contactTime - self.__latestTime > ConfigLoader.get("telegram", "context_expiration_time")) :
            # refresh message list
            LoggingManager.info("Context expired, clear context.", "ChatSession")
            self.__messageList.clear()
            self.__system_role = ConfigLoader.get("openai", "default_system_role")
        self.__latestTime = contactTime
        
        if self.no_context_mode == True and source == "user":
            self.clear_context(contactTime)
        
        self.__messageList.append(
            {"role": source, "content": message}
        )
        
    def set_voice(self):
        voiceSetStr = "Your response will be converted to speech, so please keep your response concise and use language that mimics human speech. "
        self.__system_role = voiceSetStr + self.__system_role
        
    def unset_voice(self):
        self.__system_role = self.__system_role.replace("Your response will be converted to speech, so please keep your response concise and use language that mimics human speech. ", "")     
        
    def clear_context(self, clear_time):
        self.__latestTime = clear_time
        self.__messageList.clear()
        
    def clear_all(self, clear_time):
        self.__latestTime = clear_time
        self.__messageList.clear()
        self.no_context_mode = False
        self.__system_role = ConfigLoader.get("openai", "default_system_role")
        
    async def toggle_no_context_mode(self, contactTime, target_mode):
        if self.no_context_mode == True:
            self.clear_context(contactTime)
        if target_mode == None:
            self.no_context_mode = not self.no_context_mode
        else:
            self.no_context_mode = target_mode
        return self.no_context_mode
        
if __name__ == "__main__":
    chatA = ChatSession(1, "a")
    chatB = ChatSession(2, "b")
    print(chatA)
    print(chatB)
    chatA.update(3, "c", "user")
    print(chatA)
    print(chatB)
        