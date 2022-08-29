from os import system,environ
from json import loads
with open("config.json", "r", encoding="utf-8") as f:
    configstr = f.read().replace('\\', '!')
    configtmp = loads(configstr)
    config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
    environ['QQ'] = config['q_id']
while True:
    system(r"cd QQ* && npm start && cd ..")
