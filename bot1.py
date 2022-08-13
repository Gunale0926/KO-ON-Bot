from os import path
import core

botid = path.basename(__file__).split(".")[0].replace('bot', '')
core.run(botid)
