import json
from khl import Message, Bot
from khl.card import CardMessage, Card, Module
import subprocess
import requests
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
import psutil
import re
import urllib
import urllib3
import time

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
firstloginlock=True
LOCK = False
playtime = 0
duration = 0
netease_phone = config["n_phone"]
netease_passwd = config["n_passwd"]
qq_cookie = config["q_cookie"]
qq_enable = config["qq_enable"]
ostype = config["ostype"]
bot = Bot(token=config["token"])
playlist = []


def kill():
    global p
    try:
        process = psutil.Process(p.pid + ostype) #Linux 需要 +1，MacOS和Windows不需要
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
                    "content": "功能:    将歌曲加到播放队列中\ntips:\n歌名中如果有英文引号等特殊字符，需要将歌名用英文引号括起来\n例如  **点歌 \"Rrhar'il\"**\n如果需要指定歌曲版本播放，可以在歌名后添加歌手\n例如  **点歌 勇敢勇敢-黄勇**\n现支持QQ音乐、网易云音乐与B站，若不写平台则默认从网易云获取数据\n例如  **点歌 qq heavensdoor**\n例如  **点歌 网易 勇敢勇敢-黄勇**\n例如  **点歌 b站 BV1qa411e7Fi**"
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
def getCidAndTitle(bvid,p=1):
    global duration
    
    url='https://api.bilibili.com/x/web-interface/view?bvid='+bvid
    data=requests.get(url).json()['data']
    title=data['title']
    cid=data['pages'][p-1]['cid']
    duration=data['pages'][p-1]['duration']
    mid=str(data['owner']['mid'])
    name=data['owner']['name']
    pic=data['pic']
    print(cid,title,mid)
    return str(cid),title,mid,name,pic

def getInformation(bvid):
    bvid=bvid.replace("?p=", " ")
    item=[]
    if len(bvid) == 12:

        cid,title,mid=getCidAndTitle(bvid)
        item.append(bvid)
    else:

        cid,title,mid,name,pic=getCidAndTitle(bvid[:12],int(bvid[13:]))
        item.append(bvid[:12])
    item.append(cid)
    item.append(title)
    item.append(mid)
    item.append(name)
    item.append(pic)

    return item

def getAudio(item):
    baseUrl='http://api.bilibili.com/x/player/playurl?fnval=16&'
    bvid,cid,title,mid,name,pic=item[0],item[1],item[2],item[3],item[4],item[5]
    url=baseUrl+'bvid='+bvid+'&cid='+cid
    audioUrl=requests.get(url).json()['data']['dash']['audio'][0]['baseUrl']
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
        ('Accept', '*/*'),
        ('Accept-Language', 'en-US,en;q=0.5'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Range', 'bytes=0-'),
        ('Referer', 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid),  # 注意修改referer,必须要加的!
        ('Origin', 'https://www.bilibili.com'),
        ('Connection', 'keep-alive'),
    ]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url=audioUrl, filename='tmp.mp3')
    return bvid,cid,title,mid,name,pic

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
    global qq_enable
    try:
        args=list(args)
        if msg.ctx.channel.id != config["channel"]:
            await msg.ctx.channel.send('请在指定频道中点歌')
            return
        global playlist
        typ='网易'
        song_name=''
        if args[0]=='qq' or args[0]=='网易' or args[0]=='b站': 
            typ=args[0]
            args.pop(0)
            if typ=='qq' and qq_enable == 0:
                await msg.ctx.channel.send('未启用qq点歌')
                return None
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
    global netease_phone
    global netease_passwd
    global firstloginlock
    if firstloginlock==True:
        url='http://127.0.0.1:3000/login/status'
        response=requests.get(url=url).json()['data']['account']
        if response==None:
            url='http://127.0.0.1:3000/login/cellphone?phone='+netease_phone+'&password='+netease_passwd
            print(requests.get(url=url).json())
            print('登陆成功')
        print('已登录')
        firstloginlock=False
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
                if playlist[0]['type']=='网易':
                    url="http://127.0.0.1:3000/search?keywords="+song_name+"&limit=1"

                    musicid=str(requests.get(url=url).json()['result']['songs'][0]['id'])
                    url='http://127.0.0.1:3000/song/detail?ids='+musicid

                    response=requests.get(url=url).json()['songs'][0]
                    song_name=response['name']
                    ban=re.compile('惊雷')
                    resu=ban.findall(song_name)
                    if len(resu)>0:
                        LOCK=False
                        await bot.send(
                            await bot.fetch_public_channel(
                                config["channel"]
                            ),
                            '吃了吗，没吃吃我一拳',
                        )
                    song_url='https://music.163.com/#/song?id='+str(response['id'])
                    album_name=response['al']['name']
                    if album_name=='':
                        album_name='无专辑'
                    album_url='https://music.163.com/#/album?id='+str(response['al']['id'])
                    singer_name=response['ar'][0]['name']
                    singer_url='https://music.163.com/#/artist?id='+str(response['ar'][0]['id'])
                    pic_url=response['al']['picUrl']
                    getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])
                    urlresponse=requests.get(url=getfile_url).json()['data'][0]['url']
                    print(urlresponse)
                    if urlresponse==None:
                        urlresponse=''
                    if urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0:
                        getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])
                        urlresponse=requests.get(url=getfile_url).json()['data']['url']
                        print(urlresponse)
                    if urlresponse==None:
                        urlresponse=''
                    
                    if urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0:
                        getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])+'&br=2000000'
                        urlresponse=requests.get(url=getfile_url).json()['data'][0]['url']
                        print(urlresponse)
                    if urlresponse==None:
                        urlresponse=''
                    
                    if urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0:
                        getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])+'&br=2000000'
                        urlresponse=requests.get(url=getfile_url).json()['data']['url']
                        print(urlresponse)
                    if urlresponse==None:
                        urlresponse=''
                    musicfile = requests.get(urlresponse)
                    if urlresponse.endswith("flac"):
                        open("tmp.flac", "wb").write(musicfile.content)
                        duration = FLAC("tmp.flac").info.length
                        p = subprocess.Popen(
                            'ffmpeg -re -nostats -i "tmp.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                            shell=True
                        )
                    else:
                        open("tmp.mp3", "wb").write(musicfile.content)
                        duration = MP3("tmp.mp3").info.length
                        p = subprocess.Popen(
                            'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                            shell=True
                        )
                    
                    starttime=int(round(time.time() * 1000))
                    endtime=starttime+int(duration*1000)
                    playtime = 0
                    
                    cm = [ { "type": "card", "theme": "secondary", "color": "#DD001B", "size": "lg", "modules": [ { "type": "header", "text": { "type": "plain-text", "content": "正在播放：" + song_name, }, }, { "type": "section", "text": { "type": "kmarkdown", "content":"(met)" +playlist[0]['userid']+"(met)", }, }, { "type": "context", "elements": [ { "type": "kmarkdown", "content": "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")", } ], }, { "type": "audio", "title": song_name, "src": urlresponse, "cover": pic_url, }, {"type": "countdown","mode": "second","startTime": starttime,"endTime": endtime},{"type": "divider"}, { "type": "context", "elements": [ { "type": "image", "src":  "https://img.kaiheila.cn/assets/2022-05/UmCnhm4mlt016016.png", }, { "type": "kmarkdown", "content": "网易云音乐  [在网页查看](" + song_url + ")", }, ], }, ], } ]
                    await bot.send(
                        await bot.fetch_public_channel(
                            config["channel"]
                        ),
                        cm,
                    )
                elif playlist[0]['type']=='b站':
                    song_name=song_name.replace(" ", "")
                    bvid,cid,title,mid,name,pic=getAudio(getInformation(song_name))
                    starttime=int(round(time.time() * 1000))
                    endtime=starttime+int(duration*1000)
                    cm=[{"type": "card","theme": "secondary", "color": "#DD001B", "size": "lg","modules": [{"type": "section","text": {"type": "kmarkdown","content": "**标题:        ["+title+"](https://www.bilibili.com/video/"+song_name+"/)**"}},{"type": "section","text": {"type": "kmarkdown","content": "UP:         ["+name+"](https://space.bilibili.com/"+mid+"/)"}},{"type": "container","elements": [{"type": "image","src": pic}]},{"type": "countdown","mode": "second","startTime": starttime,"endTime": endtime}]}]
                    print(duration)
                    playtime = 0
                    p = subprocess.Popen(
                        'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                        shell=True
                    )
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
                    getfile_url='http://127.0.0.1:3300/song/url?id='+response['songmid']+'&mediaId='+response['strMediaMid']+'&ownCookie=1'
                    headers={
                        'cookie':qq_cookie
                    }
                    if len(qq_cookie)>0:
                        response=requests.get(url=getfile_url,headers=headers).json()['data']
                    else:
                        response=requests.get(url=getfile_url).json()['data']
                    musicfile = requests.get(response)
                    open("tmp.mp3", "wb").write(musicfile.content)
                    duration = MP3("tmp.mp3").info.length
                    starttime=int(round(time.time() * 1000))
                    endtime=starttime+int(duration*1000)
                    playtime = 0
                    p = subprocess.Popen(
                        'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                        shell=True
                    )
                    cm = [ { "type": "card", "theme": "secondary", "color": "#DD001B", "size": "lg", "modules": [ { "type": "header", "text": { "type": "plain-text", "content": "正在播放：" + song_name }, }, { "type": "section", "text": { "type": "kmarkdown", "content":"(met)" +playlist[0]['userid']+"(met)", }, }, { "type": "context", "elements": [ { "type": "kmarkdown", "content": "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")", } ], }, { "type": "audio", "title": song_name, "src": response, "cover": pic_url, }, {"type": "countdown","mode": "second","startTime": starttime,"endTime": endtime},{"type": "divider"}, { "type": "context", "elements": [ { "type": "image", "src": "https://img.kaiheila.cn/assets/2022-06/cqzmClO3Sq07s07x.png/ld", }, { "type": "kmarkdown", "content": "QQ音乐  [在网页查看](" + song_url + ")", }, ], }, ], } ]
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

@bot.task.add_interval(hours=2)
async def keep_login():
    url='http://127.0.0.1:3000/login/refresh'
    requests.get(url=url)
    print('刷新登录')

bot.command.update_prefixes("")
bot.run()
