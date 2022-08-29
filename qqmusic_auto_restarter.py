from os import system
from json import loads
with open("config.json", "r", encoding="utf-8") as f:
    configstr = f.read().replace('\\', '!')
    configtmp = loads(configstr)
    config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
    q_id=config['q_id']
while True:
    system(f"cd QQ* && QQ={q_id} npm start && cd ..")
