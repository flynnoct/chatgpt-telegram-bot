import os, json
from datetime import datetime


class ThreadManager():
    def __init__(self, file_path="./openai_threads_records.json"):
        self.file_path = file_path
        # records existed
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.records = json.load(f)
        else:
            self.records = {}
    
    def create_chat(self, chat_id):
        chat_id = str(chat_id)
        self.records[chat_id] = {"tid": None, "last_used": None}
    
    def pop_chat(self, chat_id):
        chat_id = str(chat_id)
        self.records.pop(chat_id)
        self.save()

    def has_chat(self, chat_id):
        chat_id = str(chat_id)
        return chat_id in self.records

    def set_thread_id(self, chat_id, thread_id):
        chat_id = str(chat_id)
        if not self.has_chat(chat_id):
            self.create_chat(chat_id)
        self.records[chat_id]["tid"] = thread_id
        self.records[chat_id]["last_used"] = datetime.now().timestamp()
        self.save()
    
    def update_thread_last_used(self, chat_id):
        chat_id = str(chat_id)
        self.records[chat_id]["last_used"] = datetime.now().timestamp()
        self.save()

    # -> (thread_id, last_used)
    def get_thread(self, chat_id):
        chat_id = str(chat_id)
        if not self.has_chat(chat_id):
            return (None, None)
        return (self.records[chat_id]["tid"], self.records[chat_id]["last_used"])


    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.records, f, indent=4)