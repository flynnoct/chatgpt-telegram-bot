import asyncio
from openai_parser import OpenAIParser
from access_manager import AccessManager

class MessageManager:
    def __init__(self):
        self.openai_parser = OpenAIParser()
        self.access_manager = AccessManager()

        self.pending_messages = {} # key: chat_id, value: {"messages": [], "files": []}

    async def get_text_message(self, chat_id, message_text, reply_callback, send_typing_action_callback):
        await self._add_item_to_queue(chat_id, "messages", message_text, reply_callback, send_typing_action_callback)

    async def get_file_message(self, chat_id, message_text, file_bytes, reply_callback, send_typing_action_callback):
        await self._add_item_to_queue(chat_id, "messages", message_text, reply_callback, send_typing_action_callback)
        await self._add_item_to_queue(chat_id, "files", file_bytes, reply_callback, send_typing_action_callback)

    async def _add_item_to_queue(self, chat_id, item_type, item, reply_callback, send_typing_action_callback):
        assert item_type in ["messages", "files"]
        if chat_id in self.pending_messages: # existing messages to be sent
            self.pending_messages[chat_id]["timer"].cancel() # cancel the timer
        else:
            self.pending_messages[chat_id] = {"messages": [], "files": [], "timer": None}
        self.pending_messages[chat_id][item_type].append(item) # add the item to the queue
        self.pending_messages[chat_id]["timer"] = asyncio.create_task( # create a new timer, when it expires, query the response
            self._get_response_after_waiting(
                chat_id, 
                self.pending_messages[chat_id],
                reply_callback,
                send_typing_action_callback
                )
            )

    async def _get_response_after_waiting(self, chat_id, items, reply_callback, send_typing_action_callback, wait_time = 5):
        await asyncio.sleep(wait_time)
        # start task, extracting messages and files
        await send_typing_action_callback()
        messages = items["messages"]
        files = items["files"]
        self.pending_messages.pop(chat_id) # pop pending messages
        responses = self.openai_parser.get_chat_response(
            chat_id, 
            {"texts": messages, "files": files}
            )
        await reply_callback(responses)

    def new_thread(self, context_id):
        self.openai_parser.new_thread(context_id)

    async def get_vision_response(self, text, image_url):
        return self.openai_parser.get_vision_response(text, image_url)

    # def clear_context(self, chat_id):
    #     self.openai_parser.clear_context(chat_id)

    def get_generated_image_url(self, prompt, num=1):
        return self.openai_parser.get_generated_image_url(prompt, num)