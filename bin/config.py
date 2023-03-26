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
             "9": "image_generation_limit_per_day", "10": "enable_inline",
             "11": "openai_timeout", "12": "enable_custom_system_role",
             "13": "system_role"}


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

        for i in range(1, 14):
            if i == 4 or i == 8:
                update_user_list(str(i), "Config all items")
            else:
                update_item(str(i), "Config all items")

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
        print("10. enable_inline")
        print("11. openai_timeout")
        print("12. enable_custom_system_role")
        print("13. system_role")
        print("Input the item number (1-13):")

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

    def do_11(self, args):
        update_item("11")

    def do_12(self, args):
        update_item("12")

    def do_13(self, args):
        update_item("13")

    def do_4(self, args):
        update_user_list("4")

    def do_8(self, args):
        update_user_list("8")

    def do_exit(self, args):
        print("Exit configuration. Run the Bot now!")
        return True

    def postloop(self) -> None:
        with open("../config.json", "w") as f:
            json.dump(config_dict, f, indent=4)
        print("The config.json file is saved.")
        return super().postloop()


def update_user_list(index, type="Update one item"):
    print("\nHow do you want to config <", item_dict[index], "> list?")
    print("a. add a new user")
    print("b. remove a user")
    print("c. clear the list")
    print("d. back")

    while True:
        print("Input 'a', 'b', 'c' or 'd':")
        data = sys.stdin.readline().strip('\n')

        if data == 'a':
            print("Input ID of the new user:")
            userid = sys.stdin.readline().strip('\n')

            if index == "4":
                allowed_users.append(str(userid))
            else:
                super_users.append(str(userid))

            print("New user is added to the list.\n")
            break

        elif data == 'b':
            print("Input ID of the user:")
            userid = sys.stdin.readline().strip('\n')

            if index == "4":
                if not allowed_users.count(str(userid)):
                    print("*** Error. The user is not in the list.")
                else:
                    allowed_users.remove(str(userid))
                    print("The user is removed from the list.")
                    break
            else:
                if not super_users.count(str(userid)):
                    print("*** Error. The user is not in the list.")
                else:
                    super_users.remove(str(userid))
                    print("The user is removed from the list.")
                    break

        elif data == 'c':
            if index == "4":
                allowed_users.clear()
            else:
                super_users.clear()
            print("The list is cleared.\n")
            break

        elif data == 'd':
            print("")
            break
        else:
            print("*** Invalid input!")

    if type == "Update one item":
        print(
            "\nInput (1-13) to update another item or type 'exit' to finish configuration.\n")


def update_item(index, type="Update one item"):
    if index == "3" or index == "5" or index == "7" or index == "10" or index == "12":
        print("Set <", item_dict[index], "> to 'true' or 'false':")

        while True:
            data = sys.stdin.readline().strip('\n')
            if not (data == 'true' or data == 'false'):
                print("*** Invalid input! Please input 'true' or 'false':")
            else:
                break
    elif index == "6" or index == "9" or index == "11":
        print("Input your <", item_dict[index], ">:")
        while True:
            data = sys.stdin.readline().strip('\n')

            for i in range(len(data)):
                if ord(data[i]) > 57 or ord(data[i]) < 48:
                    print("*** Invalid input! Please input a number:")
                    flag = 0
                    break
                else:
                    flag = 1

            if flag == 1:
                break
    else:
        print("Input your <", item_dict[index], ">:")
        data = sys.stdin.readline().strip('\n')

    config_dict[item_dict[index]] = data
    print("<", item_dict[index], "> is updated.\n")

    if type == "Update one item":
        print(
            "\nInput (1-13) to update another item or type 'exit' to finish configuration.\n")
    if index == "13" and type == "Config all items":
        config.postloop()
        config.do_exit()


if __name__ == "__main__":
    if os.path.exists("../config.json"):
        with open("../config.json") as f:
            config_dict = json.load(f)

            allowed_users = config_dict["allowed_users"]
            super_users = config_dict["super_users"]

            if "<USER_ID_1>" in allowed_users:
                allowed_users.clear()

            if "<SUPER_USER_ID_1>" in super_users:
                super_users.clear()

    try:
        os.system('cls')
        config = ConfigShell()
        config.cmdloop()
    except:
        exit()
