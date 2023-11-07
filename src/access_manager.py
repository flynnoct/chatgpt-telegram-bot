from config_loader import ConfigLoader

class AccessManager():

    @staticmethod
    def is_allowed(user_id, action):
        user_id = str(user_id)
        if action == "chat":
            return ConfigLoader.get("user_management", "allow_all_users_chat") or (user_id in ConfigLoader.get("user_management", "allowed_chat_users"))
        elif action == "image_generation":
            return ConfigLoader.get("user_management", "allow_all_users_image_generation") or (user_id in ConfigLoader.get("user_management", "allowed_image_generation_users"))