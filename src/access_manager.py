import json

class AccessManager:

    config_dict = {}

    def __init__(self) -> None:
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)

    # FIXME: In case of granting users different authority between text, voice and file,
    # the <chat_type> field is currently reserved for future use.
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
                return True
            else:
                return False
