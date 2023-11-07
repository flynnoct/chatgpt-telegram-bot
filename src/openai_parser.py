"""OpenAI Request Parser

Description to be added.

__author__ = Zhiquan Wang
__copyright__ = Copyright 2023
__version__ = 2.0.0
__maintainer__ = Zhiquan Wang
__email__ = contact@flynnoct.com
__status__ = Dev
"""

from time import sleep

import openai
from datetime import datetime

from config_loader import ConfigLoader
from thread_manager import ThreadManager

class OpenAIParser:
    def __init__(self):
        openai.api_key = ConfigLoader.get("openai", "api_key")
        self.assistant = openai.beta.assistants.create(
            name = "Chat Bot",
            instructions = ConfigLoader.get("openai", "assistant_instructions"),
            tools = [],
            model = ConfigLoader.get("openai", "chat_model"),
        )

        self.thread_manager = ThreadManager()

    def get_chat_response(self, user_id, message_text):
        # TODO: Add file support
        thread = self._prepare_thread(user_id)
        message = openai.beta.threads.messages.create(
            thread_id = thread.id,
            role = "user",
            content = message_text
        )
    
        # TODO: Implement instructions
        run = openai.beta.threads.runs.create(
            thread_id = thread.id,
            assistant_id = self.assistant.id
        )
        
        for _ in range(ConfigLoader.get("openai", "message_timeout")):
            run = openai.beta.threads.runs.retrieve(
                thread_id = thread.id,
                run_id = run.id
            )
            sleep(1)
            if run.status == "completed":
                messages = openai.beta.threads.messages.list(
                    thread_id=thread.id
                )
                new_messages = self._parse_new_messages(messages)
                return new_messages
            elif run.status == "failed" or run.status == "cancelled" or run.status == "expired":
                break

    def _parse_new_messages(self, messages):
        new_messages = []
        for message in messages.data:
            if message.role == "assistant":
                assert len(message.content) == 1
                content = message.content[0]
                if content.type == "text":
                    text = content.text.value
                    for annotation in content.text.annotations:
                        if annotation["type"] == "file_citation":
                            pass #FIXME
                        if annotation["type"] == "file_path":
                            pass #FIXME
                elif content.type == "image_file":
                    pass #FIXME
                new_messages.append({"type": "text", "value": text})
            else:
                break
        return new_messages



    def _prepare_thread(self, user_id):
        thread_id, last_used = self.thread_manager.get_thread(user_id)
        if thread_id is None:
            thread = openai.beta.threads.create() # create new thread
            self.thread_manager.set_thread_id(user_id, thread.id) # update thread id
        elif datetime.now().timestamp() - last_used > ConfigLoader.get("openai", "thread_timeout"): # expired thread
            openai.beta.threads.delete(thread_id) # delete expried thread
            thread = openai.beta.threads.create() # create new thread
            self.thread_manager.set_thread_id(user_id, thread.id) # update thread id
        else:
            thread = openai.beta.threads.retrieve(thread_id) # retrieve thread
            self.thread_manager.update_thread_last_used(user_id) # update last used
        return thread
    

