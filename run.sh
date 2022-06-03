#!/bin/sh
proc_name="python3 voice.py" #进程名字
while :
do
    stillRunning=$(ps -ef|grep "$proc_name"|grep -v "grep")
    if [ "$stillRunning" ]
    then
        sleep 5
    else
        cd /root/MusicBot
        nohup python3 voice.py &
    fi
    sleep 5
 done
