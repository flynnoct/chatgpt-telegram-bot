import time
import datetime
import os
import logging
import asyncio
from access_manager import AccessManager
from chat_session import ChatSession
from openai_parser import OpenAIParser
from config_loader import ConfigLoader
from logging_manager import LoggingManager


class MessageManager:
    
    def __init__(self, access_manager):
        self.__openai_parser = OpenAIParser()
        self.__access_manager = access_manager
        self.__userDict = {}
        
    async def get_response_in_stream(self, chat_id, user_id, message_id, message, chat_text_first_chunk_callback, chat_text_append_chunks_callback, is_voice = False):
        LoggingManager.debug("Get response for user in stream mode: %s" % str(user_id), "MessageManager")
        t = time.time()
        str_id = str(chat_id)
        str_user = str(user_id)
        if str_id not in self.__userDict:
            # new user
            self.__userDict[str_id] = ChatSession(t)

        async with self.__userDict[str_id].lock:
            self.__userDict[str_id].update(t, message, "user")
                
            if is_voice == True:
                self.__userDict[str_id].set_voice()
            
            # send user info for statistics            

            (answer, usage) = await self.__sendMessage_in_stream(
                chat_id, user_id, message_id, self.__userDict[str_id].messageList, chat_text_first_chunk_callback, chat_text_append_chunks_callback)
            
            if is_voice == True:
                self.__userDict[str_id].unset_voice()
            
            self.__userDict[str_id].update(t, answer, "assistant")
            self.__access_manager.update_usage_info(str_user, usage, "chat")
          
        return {"no_context_mode": self.__get_no_context_mode_param(str_id), "response":answer}

    def __get_no_context_mode_param(self, str_id):
        return self.__userDict[str_id].no_context_mode

    async def get_response(self, chat_id, user_id, message, is_voice = False):
        LoggingManager.debug("Get response for user: %s" % str(user_id), "MessageManager")
        t = time.time()
        str_id = str(chat_id)
        str_user = str(user_id)
        if str_id not in self.__userDict:
            # new user
            self.__userDict[str_id] = ChatSession(t)

        async with self.__userDict[str_id].lock:
            self.__userDict[str_id].update(t, message, "user")
                
            if is_voice == True:
                self.__userDict[str_id].set_voice()
            
            # send user info for statistics            

            (answer, usage) = await self.__sendMessage(
                user_id, self.__userDict[str_id].messageList)
            
            if is_voice == True:
                self.__userDict[str_id].unset_voice()
            
            self.__userDict[str_id].update(t, answer, "assistant")
            self.__access_manager.update_usage_info(str_user, usage, "chat")
          
        return answer

    def continue_chat(self, chat_id, user_id):
        LoggingManager.debug("Continue chat for user: %s" % str(user_id), "MessageManager")
        t = time.time()
        str_id = str(chat_id)
        str_user = str(user_id)
        if str_id not in self.__userDict:
            # new user
            self.__userDict[str_id] = ChatSession(t)
        self.__userDict[str_id].continue_chat(t) 
         
        return
    
    def clear_context(self, id):
        LoggingManager.debug("Clear context for user: %s" % id, "MessageManager")
        try:
            self.__userDict[id].clear_all(time.time())
        except Exception as e:
            print(e)

    def get_generated_image_url(self, user, prompt, num=1):
        LoggingManager.debug("Get generated image for user: %s" % user, "MessageManager")

        if user in ConfigLoader.get("user_management", "super_users"):
            url, _ = self.__openai_parser.image_generation(user, prompt)
            return (url, "Hey boss, it's on your account. 💰")

        (permission, clue) = self.__access_manager.check_image_generation_allowed(user, num)
        if permission == False:
            return None, clue

        (url, usage) = self.__openai_parser.image_generation(user, prompt)

        self.__access_manager.update_usage_info(user, usage, "image")
        return url, clue

    def get_transcript(self, user, audio_file):
        LoggingManager.debug("Get voice transcript for user: %s" % user, "MessageManager")

        return self.__openai_parser.speech_to_text(user, audio_file)
    
    async def set_system_role(self, chat_id, user_id, message):
        LoggingManager.debug("Set system role for chat: %s" % str(user_id), "MessageManager")
        t = time.time()
        str_id = str(chat_id)
        str_user = str(user_id)
        if str_id not in self.__userDict:
            self.__userDict[str_id] = ChatSession(t)  
            
        async with self.__userDict[str_id].lock:     
            self.__userDict[str_id].set_system_role(t, message)   
            
            # send first sentence
            (answer, usage) = await self.__sendMessage(user_id, 
                    [{"role": "system", "content": message}, 
                    {"role": "user", "content":"Say hello to me."}])
            self.__access_manager.update_usage_info(str_user, usage, "chat")

        return answer
    
    async def toggle_no_context_mode(self, chat_id, user_id, target_mode):
        LoggingManager.debug("Toggle no context mode for chat: %s" % str(user_id), "MessageManager")
        t = time.time()
        str_id = str(chat_id)
        if str_id not in self.__userDict:
            self.__userDict[str_id] = ChatSession(t)  
            
        async with self.__userDict[str_id].lock:     
            mode = await self.__userDict[str_id].toggle_no_context_mode(t, target_mode)   

        return mode
    
    async def __sendMessage(self, user, messageList):
        ans = await self.__openai_parser.get_response(user, messageList)
        return ans
        
    async def __sendMessage_in_stream(self, chat_id, user_id, message_id, messageList, chat_text_first_chunk_callback, chat_text_append_chunks_callback):
        print(messageList)
        ans = await self.__openai_parser.get_response_in_stream(user_id, chat_id, message_id, messageList, chat_text_first_chunk_callback, chat_text_append_chunks_callback)
        return ans
    
    
if __name__ == "__main__":
    acm = AccessManager()
    msm = MessageManager(acm)
