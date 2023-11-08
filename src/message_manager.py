from openai_parser import OpenAIParser
from access_manager import AccessManager

class MessageManager:
    def __init__(self):
        self.openai_parser = OpenAIParser()
        self.access_manager = AccessManager()

    async def get_chat_response(self, chat_id, message_text):
        return self.openai_parser.get_chat_response(chat_id, message_text)
    
    async def get_vision_response(self, text, image_url):
        return self.openai_parser.get_vision_response(text, image_url)

    def clear_context(self, chat_id):
        self.openai_parser.clear_context(chat_id)

    def get_generated_image_url(self, prompt, num=1):
        return self.openai_parser.get_generated_image_url(prompt, num)