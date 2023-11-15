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
import os, json

import openai
from datetime import datetime

from config_loader import ConfigLoader as CL
from thread_manager import ThreadManager

class OpenAIParser:
    def __init__(self):
        self.client = openai.OpenAI(api_key = CL.get("openai", "api_key"))
        if not CL.get("openai", "assistant_id") is None: # if assistant_id is set, use it
            self.assistant = self.client.beta.assistants.retrieve(CL.get("openai", "assistant_id"))
        else:
            # with open("./src/openai_tools.json", "r") as f:
            #     tools = json.load(f)
            self.assistant = self.client.beta.assistants.create(
                name="Telesage",
                instructions = "You are an assistant helping people with their problems. Your response text will be parsed as Markdown format, so please ensure your text output is in standard Markdown.",
                model = CL.get("openai", "model"),
                # tools = tools
            )

        self.thread_manager = ThreadManager()
    
    def get_generated_image_url(self, prompt, num):

        response = openai.images.generate(
            model = CL.get("openai", "image_generation", "model"),
            prompt = prompt,
            n = num, # works only for dalle2
            size = CL.get("openai", "image_generation", "size"),
            quality = CL.get("openai", "image_generation", "quality"),
            )
        image_url = response.data[0].url
        # for debug use
        # image_url = "https://catdoctorofmonroe.com/wp-content/uploads/2020/09/iconfinder_cat_tied_275717.png"
        return image_url


    def get_vision_response(self, text, image_url):
        if text is None:
            text = "What is the image about?" # default text
        response = self.client.chat.completions.create(
            model = CL.get("openai", "vision_model"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "low"
                            }
                        },
                    ],
                }
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content


    def get_chat_response(self, chat_id, message_text):
        # TODO: Add file support
        thread = self._prepare_thread(chat_id)
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
        
        for _ in range(2 * CL.get("openai", "message_timeout")):
            run = openai.beta.threads.runs.retrieve(
                thread_id = thread.id,
                run_id = run.id
            )
            sleep(0.5)
            if run.status == "completed":
                messages = openai.beta.threads.messages.list(
                    thread_id=thread.id
                )
                new_messages = self._parse_new_messages(messages)
                return new_messages
            elif run.status == "failed" or run.status == "cancelled" or run.status == "expired":
                break

    def clear_context(self, chat_id):
        thread_id, last_used = self.thread_manager.get_thread(chat_id)
        if thread_id is None:
            return
        openai.beta.threads.delete(thread_id)
        self.thread_manager.pop_chat(chat_id)

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

    def _prepare_thread(self, chat_id):
        thread_id, last_used = self.thread_manager.get_thread(chat_id)
        if thread_id is None:
            thread = openai.beta.threads.create() # create new thread
            self.thread_manager.set_thread_id(chat_id, thread.id) # update thread id
        elif datetime.now().timestamp() - last_used > CL.get("openai", "thread_timeout"): # expired thread
            openai.beta.threads.delete(thread_id) # delete expried thread
            thread = openai.beta.threads.create() # create new thread
            self.thread_manager.set_thread_id(chat_id, thread.id) # update thread id
        else:
            thread = openai.beta.threads.retrieve(thread_id) # retrieve thread
            self.thread_manager.update_thread_last_used(chat_id) # update last used
        return thread
    

