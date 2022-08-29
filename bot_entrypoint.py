from subprocess import Popen
from sys import argv
argv.pop(0)
if len(argv)==0:
    print("至少需要指定一个botid")
for botid in argv:
    print(f"正在启动bot{botid}")
    if botid.isdigit():
        if int(botid)>=1 and int(botid)<=64:
            Popen(f"start /MIN python.exe core.py {botid}",shell=True)
            print("启动成功")
        else:
            print("botid需是1到64之间的整数，启动失败")
    else:
        print("botid需是1到64之间的整数，启动失败")