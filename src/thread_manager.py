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

    # get thread if exists, else create thread, update thread last used time then return thread
    def get_thread(self, context_id):
        if context_id in self.thread_mapping_table: # get thread
            if not datetime.now().timestamp() - self.thread_mapping_table[context_id]["last_used"] > int(CL.get("openai", "thread_timeout_in_seconds")): # check if thread is expired
                thread_id = self.thread_mapping_table[context_id]["thread_id"]
                self._update_thread_mapping(context_id, thread_id) # update last_used
                thread = self.client.beta.threads.retrieve(thread_id)
                return thread
            else:
                self._clean_expired_threads(context_id)
                return self._get_thread(context_id)
        else: # create thread
            thread = self.client.beta.threads.create()
            self._update_thread_mapping(context_id, thread.id)
            return thread


    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.records, f, indent=4)