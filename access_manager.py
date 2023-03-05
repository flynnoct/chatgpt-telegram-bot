import json

class AccessManager:

    def __init__(self) -> None:
        # load config
        with open("config.json") as f:
            self.config_dict = json.load(f)
        
    def check_user_allowed(self, userid):
        with open("config.json") as f:
            config_dict = json.load(f)
            if userid in config_dict["allowed_users"]:
                return True
            else:
                return False
