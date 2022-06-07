import requests
import json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
netease_phone = config["n_phone"]
netease_passwd = config["n_passwd"]
url='http://127.0.0.1:3000/login/cellphone?phone='+netease_phone+'&password='+netease_passwd
print(requests.get(url=url))
print('login successful')
a=input('')
