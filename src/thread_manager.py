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
    
    def create_user(self, user_id):
        self.records[user_id] = {"tid": None, "last_used": None}

    def has_user(self, user_id):
        return user_id in self.records

    def set_thread_id(self, user_id, thread_id):
        if not self.has_user(user_id):
            self.create_user(user_id)
        self.records[user_id]["tid"] = thread_id
        self.records[user_id]["last_used"] = datetime.now().timestamp()
        self.save()
    
    def update_thread_last_used(self, user_id):
        self.records[user_id]["last_used"] = datetime.now().timestamp()
        self.save()

    # -> (thread_id, last_used)
    def get_thread(self, user_id):
        if not self.has_user(user_id):
            return (None, None)
        return (self.records[user_id]["tid"], self.records[user_id]["last_used"])


    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.records, f, indent=4)