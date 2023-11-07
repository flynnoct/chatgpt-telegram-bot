from openai_parser import OpenAIParser
from access_manager import AccessManager

class MessageManager:
    def __init__(self):
        self.openai_parser = OpenAIParser()
        self.access_manager = AccessManager()

    async def get_chat_response(self, user_id, message_text):
        return self.openai_parser.get_chat_response(user_id, message_text)
