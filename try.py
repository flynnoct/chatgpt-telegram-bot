import json

my_dict = {}

with open("t.json", mode="a") as f:
    my_dict = json.load(f)
    
print(my_dict)