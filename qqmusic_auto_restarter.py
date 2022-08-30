from os import system,environ
import status_manage
config = status_manage.load_config()
environ['QQ'] = config['q_id']
while True:
    system(r"cd QQ* && npm start && cd ..")
