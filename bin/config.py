import json
import os
import sys
from cmd import Cmd
import argparse as aps


config_dict = {}
allowed_users = []
super_users = []

item_dict = {"1": "openai_api_key", "2": "telegram_bot_token",
             "3": "allow_all_users", "4": "allowed_users",
             "5": "enable_voice", "6": "wait_time",
             "7": "enable_dalle", "8": "super_users",
             "9": "image_generation_limit_per_day", "10": "enable_inline"}


class ConfigShell (Cmd):
    def __init__(self) -> None:
        super().__init__()
        self.prompt = '>> '

        print("Start to update the config.json file ...\n")

    def preloop(self) -> None:
        print("How do you want to update the file?")
        print("A. Update all from the beginning.")
        print("B. Update one configuration item.\n")
        print("Input 'A' or 'B':")
        return super().preloop()

    def do_A(self, args):
        print("Start to config the file ... \n")

        for i in range(1, 11):
            if i == 4 or i == 8:
                update_user_list(str(i))
            else:
                update_item(str(i))

    def do_B(self, args):
        print("\nWhich item do you want to config?")
        print("1. openai_api_key")
        print("2. telegram_bot_token")
        print("3. allow_all_users")
        print("4. allowed_users list")
        print("5. enable_voice")
        print("6. wait_time")
        print("7. enable_dalle")
        print("8. super_users list")
        print("9. image_generation_limit_per_day")
        print("10. enable_inline\n")
        print("Input the item number (1-10):")

    def do_1(self, args):
        update_item("1")

    def do_2(self, args):
        update_item("2")

    def do_3(self, args):
        update_item("3")

    def do_5(self, args):
        update_item("5")

    def do_6(self, args):
        update_item("6")

    def do_7(self, args):
        update_item("7")

    def do_9(self, args):
        update_item("9")

    def do_10(self, args):
        update_item("10")

    def do_4(self, args):
        update_user_list("4")

    def do_8(self, args):
        update_user_list("8")

    def do_exit(self, args):
        print("Exit configuration.")
        return True

    def postloop(self) -> None:
        with open("./config.json", "w") as f:
            json.dump(config_dict, f)
        print("Config.json file is saved.")
        return super().postloop()


def update_user_list(index):
    print("\nHow do you want to config <", item_dict[index], "> list?")
    print("a. add a new user")
    print("b. remove a user")
    print("c. clear the list")
    print("Input 'a', 'b' or 'c':")
    data = sys.stdin.readline().strip('\n')

    if data == 'a':
        print("Input ID of the new user:")
        userid = sys.stdin.readline().strip('\n')
        allowed_users.append(str(userid))
        print("New user is added to the allowed list.")
    elif data == 'b':
        print("Input ID of the user:")
        userid = sys.stdin.readline().strip('\n')
        if not allowed_users.count(str(userid)):
            print("Error. The user is not in the allow list.")
            return
        else:
            allowed_users.remove(str(userid))
            print("The user is removed from the allowed list.")
    else:
        allowed_users.clear()
        print("The allowed list is cleared.")

    print("Input (1-10) to update another item or type 'exit' to finsh configuration.\n")


def update_item(index):
    if index == "3" or index == "5" or index == "7" or index == "10":
        print("Set <", item_dict[index], "> to 'true' or 'false':")

        while True:
            data = sys.stdin.readline().strip('\n')
            if not (data == 'true' or data == 'false'):
                print("Invalid input! please input 'true' or 'false':")
            else:
                break
    else:
        print("Input your <", item_dict[index], ">:")
        data = sys.stdin.readline().strip('\n')

    config_dict[item_dict[index]] = data
    print("<", item_dict[index], "> is updated.\n")
    print("Input (1-10) to update another item or type 'exit' to finsh configuration.\n")


if __name__ == "__main__":
    if os.path.exists("./config.json"):
        with open("./config.json") as f:
            config_dict = json.load(f)
            allowed_users = config_dict["allowed_users"]
            super_users = config_dict["super_users"]

    try:
        os.system('cls')
        config = ConfigShell()
        config.cmdloop()
    except:
        exit()
