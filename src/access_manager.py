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

        # load usage info
        (filename, _) = self.__get_usage_filename_and_key("chat")
        if os.path.exists("./usage/" + filename):
            with open("./usage/" + filename) as f:
                self.user_chat_usage_dict = json.load(f)

        (filename, _) = self.__get_usage_filename_and_key("image")
        if os.path.exists("./usage/" + filename):
            with open("./usage/" + filename) as f:
                self.user_image_generation_usage_dict = json.load(f)

    # generate filename & dict key (based on datetime)

    def __get_usage_filename_and_key(self, chatORimage):
        if chatORimage == "chat":
            filename = "_chat_usage.json"
        elif chatORimage == "image":
            filename = "_image_generation_usage.json"
        return (datetime.datetime.now().strftime("%Y%m") + filename,
                datetime.datetime.now().strftime("%Y-%m-%d"))

    # everytime update dict, should check date here first
    def __update_dict(self, chatORimage):
        (filename, now) = self.__get_usage_filename_and_key(chatORimage)
        # new month
        if not os.path.exists("./usage/" + filename):
            if chatORimage == "image":
                self.user_image_generation_usage_dict = {}
            elif chatORimage == "chat":
                self.user_chat_usage_dict = {}

        # new day
        if chatORimage == "image" and now not in self.user_image_generation_usage_dict:
            self.user_image_generation_usage_dict[now] = {}
        elif chatORimage == "chat" and now not in self.user_chat_usage_dict:
            self.user_chat_usage_dict[now] = {}

    def __get_image_generation_usage(self, userid):
        (_, now) = self.__get_usage_filename_and_key("image")
        # always check date
        if now not in self.user_image_generation_usage_dict:
            self.__update_dict("image")

        if userid not in self.user_image_generation_usage_dict[now]:
            used_num = 0
            self.user_image_generation_usage_dict[now][userid] = 0
        else:
            used_num = self.user_image_generation_usage_dict[now][userid]
        return used_num

    # update dict & do json dump
    def update_usage_info(self, user, num, chatORimage):
        (filename, now) = self.__get_usage_filename_and_key(chatORimage)
        self.__update_dict(chatORimage)

        if chatORimage == "image":
            # if now not in self.user_image_generation_usage_dict:
            #     self.__update_dict("image")
            if user not in self.user_image_generation_usage_dict[now]:
                self.user_image_generation_usage_dict[now][user] = 0
            self.user_image_generation_usage_dict[now][user] += num
            with open("./usage/" + filename, "w") as f:
                json.dump(self.user_image_generation_usage_dict, f)

        elif chatORimage == "chat":
            if user not in self.user_chat_usage_dict[now]:
                self.user_chat_usage_dict[now][user] = 0
            self.user_chat_usage_dict[now][user] += num
            with open("./usage/" + filename, "w") as f:
                json.dump(self.user_chat_usage_dict, f)

    # only check user in allowed_list or not
    def check_user_allowed(self, userid):
        # before check, update config
        with open("config.json") as f:
            config_dict = json.load(f)

        if config_dict["allow_all_users"] or (userid in config_dict["allowed_users"]):
            return (True, "")
        else:
            return (False, "Sorry, you are not allowed to use this bot. Contact the bot owner for more information.")

    # check user in allowed_list or not & check image limit
    def check_image_generation_allowed(self, userid, num):
        # before check, update config
        with open("config.json") as f:
            config_dict = json.load(f)

        if userid in config_dict["allowed_users"]:
            return self.__check_image_generation_limit(userid, num)
        else:
            return (False, "Sorry, you are not allowed to use this bot. Contact the bot owner for more information.")

    def __check_image_generation_limit(self, userid, num):
        used_num = self.__get_image_generation_usage(userid)

        if num + used_num > self.config_dict["image_generation_limit_per_day"]:
            return (False, "Sorry. You have generated " + str(used_num) + " pictures today and the limit is "
                    + str(self.config_dict["image_generation_limit_per_day"]) + " per day.")
        else:
            # self.update_usage_info(userid, used_num+1, "image")
            return (True, "You have used " + str(used_num + num) + " / " +
                    str(self.config_dict["image_generation_limit_per_day"]) +
                    " times.")


if __name__ == "__main__":
    access_manager = AccessManager()
    access_manager.check_user_allowed("8423190")
    access_manager.check_image_generation_allowed("8423190", 1)
    access_manager.update_usage_info("8423190", 2, "image")
    access_manager.update_usage_info("8423190", 2, "chat")
