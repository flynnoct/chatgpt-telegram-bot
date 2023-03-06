import json
import datetime
import os


class AccessManager:

    config_dict = {}
    user_image_generation_usage_dict = {}
    user_chat_usage_dict = {}

    def __init__(self) -> None:
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)

        if not os.path.exists("./usage"):
            os.makedirs("./usage")

        self.__update_dict("image")
        self.__update_dict("chat")

    def __get_usage_filename_and_key(self, chatORimage):
        if chatORimage == "chat":
            filename = "_chat_usage.json"
        elif chatORimage == "image":
            filename = "_image_generation_usage.json"
        return (datetime.datetime.now().strftime("%Y%m") + filename,
                datetime.datetime.now().strftime("%Y-%m-%d"))

    def __update_dict(self, chatORimage):
        (filename, now) = self.__get_usage_filename_and_key(chatORimage)
        if not os.path.exists("./usage/" + filename):
            if chatORimage == "image":
                self.user_image_generation_usage_dict = {}
            elif chatORimage == "chat":
                self.user_chat_usage_dict = {}
            return
        if chatORimage == "image" and now not in self.user_image_generation_usage_dict:
            self.user_image_generation_usage_dict[now] = {}
        elif chatORimage == "chat" and now not in self.user_chat_usage_dict:
            self.user_chat_usage_dict[now] = {}

    def __get_image_generation_usage(self, userid):
        (_, now) = self.__get_usage_filename_and_key("image")
        if now not in self.user_image_generation_usage_dict:
            self.__update_dict("image")
        if userid not in self.user_image_generation_usage_dict[now]:
            used_num = 0
        else:
            used_num = self.user_image_generation_usage_dict[now][userid]
        return used_num

    def update_usage_info(self, user, used_num, chatORimage):
        (filename, now) = self.__get_usage_filename_and_key(chatORimage)
        if now not in self.user_image_generation_usage_dict:
            self.__update_dict(chatORimage)
        if chatORimage == "image":
            self.user_image_generation_usage_dict[now][user] = used_num
            with open("./usage/" + filename, "w") as f:
                json.dump(self.user_image_generation_usage_dict, f)
        elif chatORimage == "chat":
            self.user_chat_usage_dict[now][user] = used_num
            with open("./usage/" + filename, "w") as f:
                json.dump(self.user_chat_usage_dict, f)

    def check_user_allowed(self, userid):
        with open("config.json") as f:
            config_dict = json.load(f)

        if config_dict["allow_all_users"] or (userid in config_dict["allowed_users"]):
            return (True, "")
        else:
            return (False, "Sorry, you are not allowed to use this bot. Contact the bot owner for more information.")

    def check_image_generation_allowed(self, userid):
        with open("config.json") as f:
            config_dict = json.load(f)

        if userid in config_dict["allowed_users"]:
            return self.check_image_generation_limit(userid)
        else:
            return (False, "Sorry, you are not allowed to use this bot. Contact the bot owner for more information.")

    def check_image_generation_limit(self, userid):
        used_num = self.__get_image_generation_usage(userid)

        if used_num >= self.config_dict["image_generation_limit_per_day"]:
            return (False, "You have reached the limit.")
        else:
            # self.update_usage_info(userid, used_num+1, "image")
            return (True, "You have used " + str(used_num + 1) + " / " +
                    str(self.config_dict["image_generation_limit_per_day"]) +
                    " times.")
            
            
if __name__ == "__main__":
    access_manager = AccessManager()
    
