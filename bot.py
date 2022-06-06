import json
from khl import Message, Bot
from khl.card import CardMessage, Card, Module
import subprocess
import requests
import eyed3
import psutil

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

LOCK = False
playtime = 0
duration = 0
netease_cookie = config["n_cookie"]
qq_cookie = config["q_cookie"]
bot = Bot(token=config["token"])
playlist = []


def kill():
    global p
    try:
        process = psutil.Process(p.pid) #Linux 需要 +1，MacOS和Windows不需要
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    except Exception as e:
        print(e)

helpcm=[
    {
        "type": "card",
        "theme": "secondary",
        "size": "lg",
        "modules": [
            {
                "type": "header",
                "text": {
                    "type": "plain-text",
                    "content": "点歌机操作指南"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "kmarkdown",
                    "content": "**1.  点歌   +    (平台)    +    歌名**"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "kmarkdown",
                    "content": "功能:    将歌曲加到播放队列中\ntips:\n歌名中如果有英文引号等特殊字符，需要将歌名用英文引号括起来\n例如  **点歌 \"Rrhar'il\"**\n如果需要指定歌曲版本播放，可以在歌名后添加歌手\n例如  **点歌 勇敢勇敢-黄勇**\n现支持QQ音乐与网易云音乐，若不写平台则默认从网易云获取数据\n例如  **点歌 qq heavensdoor**\n例如  **点歌 netease 勇敢勇敢-黄勇**"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "kmarkdown",
                    "content": "**2.  下一首**"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "kmarkdown",
                    "content": "功能:    跳过当前正播放的歌曲，仅限**有特定角色的用户**使用"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "kmarkdown",
                    "content": "**3.  歌单**"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "kmarkdown",
                    "content": "功能:    展示播放队列内剩余的歌曲"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "kmarkdown",
                    "content": "\n如有其他问题、bug或反馈建议，请私信开发人员：\nnick-haoran#0722      Gunale#2333"
                }
            }
        ]
    }
]


@bot.command(name="下一首")
async def nextmusic(msg: Message):
    global playlist
    global playtime
    global LOCK
    global duration
    flag=True
    for role in msg.author.roles:
        print(role)
        if role == config["skipper"]:
            flag=False
    if flag:
        await msg.ctx.channel.send("无权限")
        return None

    kill()
    if len(playlist)==0:
        await msg.ctx.channel.send("无下一首")
        LOCK=False
        return None
    playlist.pop(0)
    LOCK=False
    playtime=0
    if len(playlist) != 0:
        duration=0
    await msg.ctx.channel.send("切换成功")


@bot.command(name="点歌")
async def addmusic(msg: Message,*args):
    global helpcm
    try:
        args=list(args)
        if msg.ctx.channel.id != config["channel"]:
            await msg.ctx.channel.send('请在指定频道中点歌')
            return
        global playlist
        typ='netease'
        song_name=''
        if args[0]=='qq' or args[0]=='netease':
            typ=args[0]
            args.pop(0)
        for st in args:
            song_name = song_name + st + " "
        playlist.append({'name':song_name,'userid':msg.author.id,'type':typ})
        await msg.ctx.channel.send("已添加")
    except:
        await msg.ctx.channel.send(helpcm)


@bot.command(name="歌单")
async def prtlist(msg: Message):
    global playlist
    cm = CardMessage()
    c = Card()
    c.append(Module.Header('正在播放：'))
    if len(playlist) == 0:
        c.append(Module.Section('无'))
    for item in playlist:
        c.append(Module.Section(item['name']))
    cm.append(c)
    await msg.ctx.channel.send(cm)


@bot.command(name="帮助")
async def help(msg: Message):
    global helpcm
    await msg.ctx.channel.send(helpcm)


@bot.task.add_interval(seconds=5)
async def update_played_time_and_change_music():
    global playtime
    global playlist
    global LOCK
    global duration
    global p
    if LOCK:
        return
    else:
        LOCK = True
        if len(playlist) == 0:
            LOCK = False
            return None
        else:
            if playtime == 0:
                song_name = playlist[0]['name']
                if song_name == "":
                    LOCK = False
                    return
                if playlist[0]['type']=='netease':
                    url="http://127.0.0.1:3000/search?keywords="+song_name+"&limit=1&cookie="+netease_cookie
                    musicid=str(requests.get(url=url).json()['result']['songs'][0]['id'])
                    url='http://127.0.0.1:3000/song/detail?ids='+musicid+"&cookie="+netease_cookie
                    response=requests.get(url=url).json()['songs'][0]
                    song_name=response['name']
                    song_url='https://music.163.com/#/song?id='+str(response['id'])
                    album_name=response['al']['name']
                    if album_name=='':
                        album_name='无专辑'
                    album_url='https://music.163.com/#/album?id='+str(response['al']['id'])
                    singer_name=response['ar'][0]['name']
                    singer_url='https://music.163.com/#/artist?id='+str(response['ar'][0]['id'])
                    pic_url=response['al']['picUrl']
                    getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])+"&cookie="+netease_cookie
                    response=requests.get(url=getfile_url).json()['data'][0]['url']
                    musicfile = requests.get(response)
                    open("tmp.mp3", "wb").write(musicfile.content)
                    duration = eyed3.load("tmp.mp3").info.time_secs
                    playtime = 0
                    p = subprocess.Popen(
                        'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                        shell=True
                    )
                    cm = [ { "type": "card", "theme": "secondary", "color": "#DD001B", "size": "lg", "modules": [ { "type": "header", "text": { "type": "plain-text", "content": "正在播放：" + song_name, }, }, { "type": "section", "text": { "type": "kmarkdown", "content":"(met)" +playlist[0]['userid']+"(met)", }, }, { "type": "context", "elements": [ { "type": "kmarkdown", "content": "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")", } ], }, { "type": "audio", "title": song_name, "src": response, "cover": pic_url, }, {"type": "divider"}, { "type": "context", "elements": [ { "type": "image", "src":  "https://img.kaiheila.cn/assets/2022-05/UmCnhm4mlt016016.png", }, { "type": "kmarkdown", "content": "网易云音乐  [在网页查看](" + song_url + ")", }, ], }, ], } ]
                    await bot.send(
                        await bot.fetch_public_channel(
                            config["channel"]
                        ),
                        cm,
                    )
                else:
                    url="http://127.0.0.1:3300/search?key="+song_name+"&pageSize=1"
                    response=requests.get(url=url).json()['data']['list'][0]
                    song_name=response['songname']
                    song_url='https://y.qq.com/n/ryqq/songDetail/'+response['songmid']
                    album_name=response['albumname']
                    if album_name=='':
                        album_name='无专辑'
                    album_url='https://y.qq.com/n/ryqq/albumDetail/'+response['albummid']
                    singer_name=response['singer'][0]['name']
                    singer_url='https://y.qq.com/n/ryqq/singer/'+response['singer'][0]['mid']
                    pic_url='https://y.gtimg.cn/music/photo_new/T002R300x300M000'+response['albummid']+'.jpg'
                    getfile_url='http://127.0.0.1:3300/song/url?id='+response['songmid']+'&mediaId='+response['strMediaMid']
                    headers={
                        'cookie':qq_cookie
                    }
                    response=requests.get(url=getfile_url,headers=headers).json()['data']
                    musicfile = requests.get(response)
                    open("tmp.mp3", "wb").write(musicfile.content)
                    duration = eyed3.load("tmp.mp3").info.time_secs
                    playtime = 0
                    p = subprocess.Popen(
                        'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                        shell=True
                    )
                    cm = [ { "type": "card", "theme": "secondary", "color": "#DD001B", "size": "lg", "modules": [ { "type": "header", "text": { "type": "plain-text", "content": "正在播放：" + song_name, }, }, { "type": "section", "text": { "type": "kmarkdown", "content":"(met)" +playlist[0]['userid']+"(met)", }, }, { "type": "context", "elements": [ { "type": "kmarkdown", "content": "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")", } ], }, { "type": "audio", "title": song_name, "src": response, "cover": pic_url, }, {"type": "divider"}, { "type": "context", "elements": [ { "type": "image", "src": "https://img.kaiheila.cn/assets/2022-06/cqzmClO3Sq07s07x.png/ld", }, { "type": "kmarkdown", "content": "QQ音乐  [在网页查看](" + song_url + ")", }, ], }, ], } ]
                    await bot.send(
                        await bot.fetch_public_channel(
                            config["channel"]
                        ),
                        cm,
                    )
                playtime += 5
                LOCK = False
                return None
            else:
                if playtime + 5 < duration:
                    playtime += 5
                    LOCK = False
                    return None
                else:
                    playtime = 0
                    playlist.pop(0)
                    LOCK = False
                    return None


bot.command.update_prefixes("")
bot.run()
