import json
from datetime import datetime, timedelta
from voiceAPI import Voice
from khl import Message, Bot, api, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct
import subprocess
import requests
import psutil
import re
import time
import aiohttp
import asyncio
import nest_asyncio
import os
import signal
import random
from pytube import YouTube
eventloop=asyncio.new_event_loop()
asyncio.set_event_loop(eventloop)
try:
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    print("platform:linux")
except:
    print("platform:windows")
nest_asyncio.apply()
botid=os.path.basename(__file__).split(".")[0].replace('bot','')
with open("config.json", "r", encoding="utf-8") as f:
    configstr = f.read().replace('\\', '!')
    configtmp = json.loads(configstr)
    config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
rtcpport=botid+'234'
firstlogin=True
load=True
JOINLOCK=False
playtime = {}
LOCK = {}
channel = {}
duration = {}
msgid = {}
voice = {}
voicechannelid = {}
voiceffmpeg = {}
timeout = {}
netease_phone = config["n_phone"]
netease_passwd = config["n_passwd"]
netease_cookie = config["n_cookie"]
qq_cookie = config["q_cookie"]
qq_id = config["q_id"]
qq_enable = config["qq_enable"]
bot = Bot(token=config['token'+botid])
playlist = {}#guild list
port={}#guild port
p={}#guild process
deltatime=7
singleloops={}
def kill(guild):
    global p
    try:
        process = psutil.Process(p[guild].pid)
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
          "content": "**0.  "+botid+"号加入语音**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    让机器人进到你在的语音频道"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**1.  点歌   +    (平台)    +    歌名    +    (--置顶)**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将歌曲加到播放队列中\n**[Warning]**:\n歌名中如果有英文引号等特殊字符，需要将歌名用英文引号括起来\n例如  **点歌 \"Rrhar'il\"**\n**[Feature and Tips]**:\n现支持QQ音乐、全民k歌、咪咕音乐、网易云音乐、网易云音乐电台与B站，若不写平台则默认从网易云获取数据\n**1.**B站支持分P\n**2.**咪咕音乐全会员\n**3.**QQ音乐，全民K歌需要单独安装api并在config.json中启用平台\n**4.**网易云电台仅支持从节目id点播，b站仅支持从BV号与链接点播，全民k歌仅支持从链接点播\n**5.**在指令最后带上“--置顶”会将歌曲添加到播放队列最前端\n**6.**如果需要指定歌曲版本播放，可以在歌名后添加歌手\n例如  **点歌 勇敢勇敢-黄勇**\n例如  **点歌 qq heavensdoor**\n例如  **点歌 勇敢勇敢-黄勇 --置顶**\n例如  **点歌 网易 勇敢勇敢-黄勇**\n例如  **点歌 b站 BV1qa411e7Fi**\n例如  **点歌 你看到的我**\n例如  **点歌 网易电台 2499131107**\n例如  **点歌 咪咕 青花瓷**\n例如  **点歌 b站 https://www.bilibili.com/video/BV1kT4y1X7UW?p=4**\n例如  **点歌 k歌 https://node.kg.qq.com/play?s=R2M-Y3Rux5IKPRyf**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**2.  导入歌单       +       QQ或网易云的歌单id或链接**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将网易云或QQ歌单中的歌曲导入到播放队列\n例如  **导入歌单 977171340**\n例如  **导入歌单 8374280842**\n例如  **导入歌单 https://music.163.com/#/playlist?id=977171340**\n例如  **导入歌单 https://y.qq.com/n/ryqq/playlist/8374280842**\n例如  **导入歌单 https://c.y.qq.com/base/fcgi-bin/u?__=Juyj4pTo4rxn**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**3.  导入电台       +       网易云电台id/链接**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将网易电台中的歌曲导入到播放队列\n例如  **导入电台 972583481**\n例如  **导入电台 https://music.163.com/#/djradio?id=972583481**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**4.  导入专辑       +       网易云专辑id/链接**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将网易云专辑中的歌曲导入到播放队列\n例如  **导入专辑 37578031**\n例如  **导入专辑 https://music.163.com/#/album?id=37578031**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**5.  搜索       +       歌名**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    从网易云、网易电台、咪咕音乐与qq音乐搜索歌曲（qq平台需单独打开）\n例如  **搜索 海阔天空**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**6.  重新连接**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    当机器人意外掉出语音后可使用该命令重新连接至语音"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**7.  循环模式**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    切换循环模式，目前支持四种模式:**关闭,单曲循环,列表循环,随机播放**（**推荐使用按钮调用**）"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**8.  下一首**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    跳过当前正播放的歌曲（**推荐使用按钮调用**）"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**9.  清空歌单**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    清空播放队列（**推荐使用按钮调用**）"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**10.  歌单**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    展示播放队列内剩余的歌曲（**播放消息中已自带**）"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "context",
        "elements": [
          {
            "type": "plain-text",
            "content": "如有其他问题、bug或反馈建议，请私信开发人员：\nnick-haoran#0722      Gunale#2333\n特别鸣谢:        k1nbo#0001"
          }
        ]
      }
    ]
  }
]

def getCidAndTitle(guild,bvid,p=1):
    global duration
    global deltatime
    url='https://api.bilibili.com/x/web-interface/view?bvid='+bvid
    data=requests.get(url,timeout=5).json()['data']
    title=data['title']
    cid=data['pages'][p-1]['cid']
    duration[guild]=data['pages'][p-1]['duration']+deltatime
    mid=str(data['owner']['mid'])
    name=data['owner']['name']
    pic=data['pic']
    print(cid,title,mid)
    return str(cid),title,mid,name,pic

def getInformation(bvid,guild):
    bvid=bvid.replace("?p=", " ")
    item=[]
    if len(bvid) == 12:

        cid,title,mid,name,pic=getCidAndTitle(guild,bvid[:12],1)
        item.append(bvid)
    else:

        cid,title,mid,name,pic=getCidAndTitle(guild,bvid[:12],int(bvid[13:]))
        item.append(bvid[:12])
    item.append(cid)
    item.append(title)
    item.append(mid)
    item.append(name)
    item.append(pic)

    return guild,item

def getAudio(guild,item):
    baseUrl='http://api.bilibili.com/x/player/playurl?fnval=16&'
    bvid,cid,title,mid,name,pic=item[0],item[1],item[2],item[3],item[4],item[5]
    url=baseUrl+'bvid='+bvid+'&cid='+cid
    audioUrl=requests.get(url,timeout=5).json()['data']['dash']['audio'][0]['baseUrl']
    headers =  {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Range': 'bytes=0-',
        'Referer': 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid,
        'Origin': 'https://www.bilibili.com',
        'Connection': 'keep-alive'
    }
    response=requests.get(url=audioUrl, headers=headers,timeout=5)
    open(guild+"_"+botid+".mp3", "wb").write(response.content)
    return bvid,cid,title,mid,name,pic

def parse_kmd_to_url(link):
    try:
        pattern=r'(?<=\[)(.*?)(?=\])'
        link=re.search(pattern,link).group()
        return link
    except:
        return link

def start_play(guild):
    global botid
    global port
    return subprocess.Popen('ffmpeg -re -nostats -i "'+guild+"_"+botid+'.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],shell=True)
@bot.command(name='导入歌单')
async def import_playlist(msg: Message, linkid : str):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid=await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid=voiceid[0].id
        if voiceid != voicechannelid[msg.ctx.guild.id]:
            await msg.ctx.channel.send("请先进入听歌频道或退出重进")
            return
    except:
        await msg.ctx.channel.send("请先进入听歌频道或退出重进")
        return
    global playlist
    global netease_cookie
    try:
        if "fcgi-bin" in linkid:
            linkid=parse_kmd_to_url(linkid)
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'cookie': qq_cookie,
                'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': "Windows",
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
                }
            linkid=requests.get(url=linkid,headers=headers,timeout=5).text
        pattern=r'(?<=[^user]id=)[0-9]+|(?<=playlist/)[0-9]+'
        linkid=re.search(pattern,linkid).group()
    except Exception as e:
        print(e)
    print(linkid)
    headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': netease_cookie,
        'Host': '127.0.0.1:3000',
        'Referer': 'https://music.163.com',
        'If-None-Match': 'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
    }
    try:
        
        offset=0
        while True:
            url = "http://127.0.0.1:3000/playlist/track/all?id="+linkid+'&limit=1000&offset='+str(offset*1000)
            offset+=1
            async with aiohttp.ClientSession() as session:
                async with session.get(url,headers=headers,timeout=aiohttp.ClientTimeout(total=5)) as r:
                    resp_json = await r.json()
                    print
                    songs = resp_json.get("songs",[])
                    if len(songs)==0:
                        break
                    for song in songs:
                        playlist[msg.ctx.guild.id].append({'name':song.get('name','')+"-"+song.get('ar',[])[0].get('name','')+'-'+str(song.get('id')),'userid':msg.author.id,'type':'网易','time':int(round(time.time() * 1000))+1000000000000})
    except:
        pass
    try:
        url = "http://127.0.0.1:3300/songlist?id="+linkid
        async with aiohttp.ClientSession() as session:
            async with session.get(url,timeout=aiohttp.ClientTimeout(total=5)) as r:
                resp_json = await r.json() 
                songs = resp_json.get("data",{}).get("songlist",[])
                for song in songs:
                    playlist[msg.ctx.guild.id].append({'name':song.get('songname','')+"-"+song.get('singer',[])[0].get('name','')+'-'+str(song.get('songmid')),'userid':msg.author.id,'type':'qq','time':int(round(time.time() * 1000))+1000000000000})
    except:
        pass
    await msg.ctx.channel.send("导入完成")
@bot.command(name='导入专辑')
async def import_netease_album(msg: Message, linkid : str):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid=await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid=voiceid[0].id
        if voiceid != voicechannelid[msg.ctx.guild.id]:
            await msg.ctx.channel.send("请先进入听歌频道或退出重进")
            return
    except:
        await msg.ctx.channel.send("请先进入听歌频道或退出重进")
        return
    global netease_cookie
    try:
        pattern=r'(?<=[^user]id=)[0-9]+'
        linkid=re.search(pattern,linkid).group()
    except:
        pass
    headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': netease_cookie,
        'Host': '127.0.0.1:3000',
        'Referer': 'https://music.163.com',
        'If-None-Match': 'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
    }
    try:
        global playlist
        
        url = "http://127.0.0.1:3000/album?id="+linkid
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers,timeout=aiohttp.ClientTimeout(total=5)) as r:
                resp_json = await r.json() 
                songs = resp_json.get("songs",[])

                for song in songs:
                        playlist[msg.ctx.guild.id].append({'name':song.get('name','')+"-"+song.get('ar',[])[0].get('name','')+'-'+str(song.get('id')),'userid':msg.author.id,'type':'网易','time':int(round(time.time() * 1000))+1000000000000})
        await msg.ctx.channel.send("导入完成")
    except:
        pass

@bot.command(name='导入电台')
async def import_netease_radio(msg: Message, linkid : str):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid=await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid=voiceid[0].id
        if voiceid != voicechannelid[msg.ctx.guild.id]:
            await msg.ctx.channel.send("请先进入听歌频道或退出重进")
            return
    except:
        await msg.ctx.channel.send("请先进入听歌频道或退出重进")
        return
    global netease_cookie
    try:
        pattern=r'(?<=[^user]id=)[0-9]+'
        linkid=re.search(pattern,linkid).group()
    except:
        pass
    headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': netease_cookie,
        'Host': '127.0.0.1:3000',
        'Referer': 'https://music.163.com',
        'If-None-Match': 'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
    }
    try:
        global playlist
        offset=0
        while True:
            url = "http://127.0.0.1:3000/dj/program?rid="+linkid+"&limit=1000&offset="+str(offset*1000)
            offset+=1
            async with aiohttp.ClientSession() as session:
                async with session.get(url,headers=headers,timeout=aiohttp.ClientTimeout(total=5)) as r:
                    resp_json = await r.json() 
                    programs = resp_json.get("programs",[])
                    if len(programs)==0:
                        break
                    for program in programs:
                        playlist[msg.ctx.guild.id].append({'name':program.get('mainSong',{}).get('name','')+'-'+str(program.get('id')),'userid':msg.author.id,'type':'网易电台','time':int(round(time.time() * 1000))+1000000000000})
        await msg.ctx.channel.send("导入完成")
    except:
        pass
async def start(voice,voiceid,guild):
    await asyncio.wait([
        voice_Engine(voice,voiceid,guild),
        voice.handler()
    ])
async def status_active_music():
    print("已用槽位:"+str(len(voice)))
    url="https://www.kookapp.cn/api/v3/game/activity"
    headers={'Authorization': "Bot "+config['token'+botid]}
    params = {"data_type":2,"software":"qqmusic","singer":"KO-ON","music_name":"已用槽位:"+str(len(voice))}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params,headers=headers) as response:
            return json.loads(await response.text())
@bot.command(name=botid+'号加入语音')
async def connect(msg: Message):
    global playlist
    global p
    global port
    global rtcpport
    global channel
    global voice
    global voicechannelid
    global msgid
    global JOINLOCK
    while JOINLOCK:
        await asyncio.sleep(0.1)
    JOINLOCK=True
    if len(voice)>=2 and channel.get(msg.ctx.guild.id,-1)==-1:
        await msg.ctx.channel.send("播放槽位已满,请加入交流服务器获取备用机 https://kook.top/vyAPVw")
        JOINLOCK=False
        return
    voiceid=await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid=voiceid[0].id
    except:
        await msg.ctx.channel.send("请先进入一个语音频道或退出重进")
        JOINLOCK=False
        return
    print(voiceid)
    singleloops[msg.ctx.guild.id]=0
    timeout[msg.ctx.guild.id]=0
    LOCK[msg.ctx.guild.id]=False
    playlist[msg.ctx.guild.id]=[]
    voicechannelid[msg.ctx.guild.id]=voiceid
    channel[msg.ctx.guild.id]=msg.ctx.channel.id
    playtime[msg.ctx.guild.id]=0
    msgid[msg.ctx.guild.id]="0"
    duration[msg.ctx.guild.id]=0
    port[msg.ctx.guild.id]=rtcpport
    await msg.ctx.channel.send("已加入频道")
    voice[msg.ctx.guild.id] = Voice(config['token'+botid])
    event_loop = asyncio.get_event_loop()
    asyncio.ensure_future(start(voice[msg.ctx.guild.id],voiceid,msg.ctx.guild.id),loop=event_loop)
    print(await status_active_music())
    JOINLOCK=False
    
async def disconnect(guild):
    global voiceffmpeg
    try:
        process = psutil.Process(voiceffmpeg[guild].pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    except Exception as e:
        print(e)
    voice[guild].is_exit = True
    del timeout[guild]
    del voiceffmpeg[guild]
    del voice[guild]
    del LOCK[guild]
    #del playlist[guild]
    del msgid[guild]
    del voicechannelid[guild]
    del channel[guild]
    del singleloops[guild]
    del playtime[guild]
    del duration[guild]
    del port[guild]
    print(await status_active_music())
    print(str(guild)+" disconnected")
@bot.command(name='绑定点歌频道')
async def connect(msg: Message):
    global channel
    await msg.ctx.channel.send("绑定频道")
    channel[msg.ctx.guild.id]=msg.ctx.channel.id
    

@bot.command(name='清空歌单')
async def clear_playlist(msg: Message):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    try:
        global playlist
        if len(playlist[msg.ctx.guild.id])>0:
            now=playlist[msg.ctx.guild.id][0]
            playlist[msg.ctx.guild.id]=[]
            playlist[msg.ctx.guild.id].append(now)
        await msg.ctx.channel.send("清空完成")
    except:
        pass

@bot.command(name="下一首")
async def nextmusic(msg: Message):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    try:
        global playlist
        global playtime

        global duration
        
        kill(msg.ctx.guild.id)
        if len(playlist[msg.ctx.guild.id])==0:
            await msg.ctx.channel.send("无下一首")
            return None
        if singleloops[msg.ctx.guild.id]==2:
                playlist[msg.ctx.guild.id].append(playlist[msg.ctx.guild.id].pop(0))
        else:
            playlist[msg.ctx.guild.id].pop(0)
        LOCK[msg.ctx.guild.id]=False
        playtime[msg.ctx.guild.id]=0
        duration[msg.ctx.guild.id]=0
        await msg.ctx.channel.send("切换成功")
    except:
        pass

@bot.command(name="点歌")
async def addmusic(msg: Message,*args):
    global helpcm
    global qq_enable
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid=await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid=voiceid[0].id
        if voiceid != voicechannelid[msg.ctx.guild.id]:
            await msg.ctx.channel.send("请先进入听歌频道或退出重进")
            return
    except:
        await msg.ctx.channel.send("请先进入听歌频道或退出重进")
        return
    try:
        args=list(args)
        global playlist
        typ='网易'
        song_name=''
        coefficient=1
        platform = {'网易','netease','Netease','网易云','网易云音乐','网易音乐','qq','qq音乐','QQ','QQ音乐','网易电台','电台','咪咕','咪咕音乐','bili','b站','bilibili','Bili','Bilibili','B站','k歌','K歌','全民k歌','全民K歌','ytb','YTB','youtube','Youtube','油管'}
        if args[0] in platform:
            typ=args[0]
            args.pop(0)
            if typ in {'qq','qq音乐','QQ','QQ音乐','k歌','K歌','全民k歌','全民K歌'} and qq_enable == '0':
                await msg.ctx.channel.send('未启用QQ音乐与全民k歌点歌')
                return None
        if args[-1] in {"--置顶","-置顶","--top","-top","/置顶","/top"}:
            args.pop()
            coefficient=-1
        for st in args:
            song_name = song_name + st + " "
        playlist[msg.ctx.guild.id].append({'name':song_name,'userid':msg.author.id,'type':typ,'time':int(round(time.time() * 1000))*coefficient})
        await msg.ctx.channel.send("已添加")
    except:
        pass
@bot.command(name="RELOAD")
async def reload(msg: Message):
    global config
    global firstlogin
    global netease_phone
    global netease_passwd
    global netease_cookie
    global qq_cookie
    global qq_id
    global qq_enable
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            configstr = f.read().replace('\\', '!')
            configtmp = json.loads(configstr)
            config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
        netease_phone = config["n_phone"]
        netease_passwd = config["n_passwd"]
        netease_cookie = config["n_cookie"]
        qq_cookie = config["q_cookie"]
        qq_id = config["q_id"]
        qq_enable = config["qq_enable"]
        firstlogin=True
        await msg.ctx.channel.send("reload成功")
    except:
        await msg.ctx.channel.send("reload失败")
        
@bot.command(name="REBOOT"+str(botid))
async def reboot(msg: Message):
    os._exit(0)
    
def get_playlist(guild):
    c = Card()
    c.append(Module.Header('播放队列：'))
    if len(playlist[guild]) == 0:
        c.append(Module.Section('无'))
    i=0
    for item in playlist[guild]:
        if i==10:
            break
        c.append(Module.Section(item['name']))
        i+=1
    c.append(Module.Header('共有'+str(len(playlist[guild]))+'首歌'))
    return c

@bot.command(name="歌单")
async def prtlist(msg: Message):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    try:
        global playlist
        cm = CardMessage()
        c=get_playlist(msg.ctx.guild.id)
        cm.append(c)
        await msg.ctx.channel.send(cm)
    except:
        pass

@bot.command(name="帮助")
async def help(msg: Message):
    global helpcm
    await msg.ctx.channel.send(helpcm)

@bot.command(name="状态")
async def status(msg: Message):
    global helpcm
    await msg.ctx.channel.send("已用槽位:"+str(len(voice)))
@bot.command(name="循环模式")
async def singlesongloop(msg: Message):
    global singleloops
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    try:
        if singleloops[msg.ctx.guild.id]==0:
            singleloops[msg.ctx.guild.id]=1
            await msg.ctx.channel.send('循环模式已调整为:单曲循环')
        elif singleloops[msg.ctx.guild.id]==1:
            singleloops[msg.ctx.guild.id]=2
            await msg.ctx.channel.send('循环模式已调整为:列表循环')
        elif singleloops[msg.ctx.guild.id]==2:
            singleloops[msg.ctx.guild.id]=3
            await msg.ctx.channel.send('循环模式已调整为:随机播放')
        else :
            singleloops[msg.ctx.guild.id]=0
            await msg.ctx.channel.send('循环模式已调整为:关闭')
    except:
        pass
@bot.command(name="重新连接")
async def reconnect(msg: Message):
    global voiceffmpeg
    global voice
    global port
    global rtcpport
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid=await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid=voiceid[0].id
    except:
        await msg.ctx.channel.send("请先进入一个语音频道或退出重进")
        return
    try:
        try:
            process = psutil.Process(voiceffmpeg[msg.ctx.guild.id].pid)
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()
        except Exception as e:
            print(e)
        voice[msg.ctx.guild.id].is_exit = True
        del voice[msg.ctx.guild.id]
        voicechannelid[msg.ctx.guild.id]=voiceid
        del voiceffmpeg[msg.ctx.guild.id]
        await msg.ctx.channel.send("已加入频道")
        voice[msg.ctx.guild.id] = Voice(config['token'+botid])
        event_loop = asyncio.get_event_loop()
        asyncio.ensure_future(start(voice[msg.ctx.guild.id],voiceid,msg.ctx.guild.id),loop=event_loop)
    except Exception as e:
        print(e)
@bot.command(name="搜索")
async def search(msg: Message,*args):
    global netease_cookie
    global botid
    if botid != "1":
        return
    headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': netease_cookie,
        'Host': '127.0.0.1:3000',
        'Referer': 'https://music.163.com',
        'If-None-Match': 'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
    }
    song_name=''
    for st in args:
            song_name = song_name + st + " "
    url="http://127.0.0.1:3000/search?keywords="+song_name+"&limit=5"
    songs=requests.get(url=url,timeout=5,headers=headers).json()['result']['songs']
    text='网易云结果:\n'
    try:
        for song in songs:
            text+=song['name']+'-'+song['artists'][0]['name']+'-'+song['album']['name']+'-'+str(song['id'])+'\n'
    except:
        text+='无\n'

    if qq_enable== '1':
        text+='QQ结果:\n'
        url="http://127.0.0.1:3300/search/quick?key="+song_name
        songs=requests.get(url=url,timeout=5).json()['data']['song']['itemlist']
        try:
            for song in songs:
                text+=song['name']+'-'+song['singer']+'\n'
        except:
            text+='无\n'

    text+='网易电台结果:\n'
    url="http://127.0.0.1:3000/search?keywords="+song_name+"&limit=5&type=2000"
    songs=requests.get(url=url,timeout=5).json()['data']['resources']
    try:
        for song in songs:
            text+=song['baseInfo']['mainSong']['name']+'-'+song['baseInfo']['mainSong']['artists'][0]['name']+'-'+song['resourceId']+'\n'
    except:
        text+='无\n'

    text+='咪咕结果:\n'
    url="http://127.0.0.1:3400/search?keyword="+song_name
    songs=requests.get(url=url,timeout=5).json()['data']['list']
    try:
        i=0
        for song in songs:
            i+=1
            text+=song['name']+'-'+song['artists'][0]['name']+'-'+song['album']['name']+'-'+song['cid']+'\n'
            if i==5:
                break
    except:
        text+='无\n'
    await msg.ctx.channel.send(text)

def delmsg(msg_id):
    print(msg_id)
    global config
    global botid
    url='https://www.kookapp.cn/api/v3/message/delete'
    data={
        "msg_id":str(msg_id)
    }
    headers={
        "Authorization": "Bot "+config['token'+botid]
        }
    response=requests.post(url=url,timeout=5,json=data,headers=headers)
    print(response.text)

async def netease(guild,song_name):
    global deltatime
    global playtime
    global playlist
    global duration
    global p
    global netease_phone
    global netease_passwd
    global firstlogin
    global neteasecookie
    global LOCK
    LOCK[guild]=True
    try:
        headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Cookie': netease_cookie,
                'Host': '127.0.0.1:3000',
                'Referer': 'https://music.163.com',
                'If-None-Match': 'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': "Windows",
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
            }
        if playlist[guild][0]['time']>int(round(time.time() * 1000)):
            song_name=song_name.split('-')[-1]
            musicid=song_name
        else:   
            url="http://127.0.0.1:3000/cloudsearch?keywords="+song_name+"&limit=1"
            response=requests.get(url=url,timeout=5,headers=headers).json()
            musicid=str(response['result']['songs'][0]['id'])

        url='http://127.0.0.1:3000/song/detail?ids='+musicid

        response=requests.get(url=url,timeout=5,headers=headers).json()['songs'][0]
        duration[guild]=int(response['dt']/1000)+deltatime
        song_name=response['name']
        ban=re.compile('(惊雷)|(Lost Rivers)')
        resu=ban.findall(song_name)
        print(resu)
        if len(resu)>0:

            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    config["channel"]
                ),
                '吃了吗，没吃吃我一拳',
            )
            duration[guild]=0
            playtime[guild]=0
            LOCK[guild]=False
            return 
        song_url='https://music.163.com/#/song?id='+str(response['id'])
        album_name=response['al']['name']
        if album_name=='':
            album_name='无专辑'
        album_url='https://music.163.com/#/album?id='+str(response['al']['id'])
        singer_name=response['ar'][0]['name']
        singer_url='https://music.163.com/#/artist?id='+str(response['ar'][0]['id'])
        pic_url=response['al']['picUrl']
        getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])+'&br=320000&timestamp='+str(int(round(time.time() * 1000)))
        
        urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data'][0]['url']
        print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])+'&br=320000&timestamp='+str(int(round(time.time() * 1000)))
            urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data']['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''

        

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data'][0]['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data']['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        
        if urlresponse.endswith("flac"):
            async with aiohttp.ClientSession() as session:
                async with session.get(urlresponse,timeout=aiohttp.ClientTimeout(total=5)) as r:
                    with open(guild+"_"+botid+".flac", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild)
            p[guild] = subprocess.Popen(
                'ffmpeg -re -nostats -i "'+guild+"_"+botid+'.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],
                shell=True
            )
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(urlresponse,timeout=aiohttp.ClientTimeout(total=5)) as r:
                    with open(guild+"_"+botid+".mp3", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild)
            p[guild] = start_play(guild)
        playtime[guild] = 0
        if len(song_name)>50:
            song_name=song_name[:50]
        delmsg(msgid[guild])
        cm = CardMessage()
        c=get_playlist(guild)
        cm.append(c)
        c=Card(
                    Module.Header("正在播放： "+ song_name),
                    Module.Context(
                        Element.Text("歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")",Types.Text.KMD)
                        ),
                    
                    Module.File(Types.File.AUDIO, src=urlresponse, title=song_name, cover=pic_url),
                    Module.Countdown(datetime.now() + timedelta(seconds=duration[guild]), mode=Types.CountdownMode.SECOND),
                    Module.Divider(),
                    Module.Context(
                        Element.Image(src="https://img.kookapp.cn/assets/2022-05/UmCnhm4mlt016016.png"),
                        Element.Text("网易云音乐  [在网页查看](" + song_url + ")",Types.Text.KMD)),
                    Module.ActionGroup(
                        Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                        Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                        Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)
                        )
                    
                )
        cm.append(c)
        msgid[guild]=(await bot.send(
            await bot.fetch_public_channel(
                channel[guild]
            ),
            cm
            ))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e)=="'songs'":
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '未检索到此歌曲',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '发生错误，正在重试',
            )
        playlist[guild].pop(0)
        duration[guild]=0
        playtime[guild]=0
        LOCK[guild]=False
        return
    LOCK[guild]=False
    return

async def bili(guild,song_name):
    global deltatime
    global playtime
    global playlist
    global duration
    global p
    global netease_phone
    global netease_passwd
    global firstlogin
    global neteasecookie
    global LOCK
    LOCK[guild]=True
    try:
        pattern=r'BV\w{10}(\?p=[0-9]+)*'
        song_name=re.search(pattern,song_name).group()
        guild,item=getInformation(song_name,guild)
        bvid,cid,title,mid,name,pic=getAudio(guild,item)
        starttime=int(round(time.time() * 1000))
        endtime=starttime+int(duration[guild]*1000)
        print(duration[guild])
        ban=re.compile('(惊雷)|(Lost Rivers)')
        resu=ban.findall(title)
        if len(resu)>0:
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '吃了吗，没吃吃我一拳',
            )
            duration[guild]=0
            playtime[guild]=0
            LOCK[guild]=False
            return
        playtime[guild] = 0
        kill(guild)
        p[guild] = start_play(guild)
        playlist[guild][0]['name']=title
        delmsg(msgid[guild])
        cm = CardMessage()
        c=get_playlist(guild)
        cm.append(c)
        c=Card(
                    Module.Context(
                        Element.Text("**标题:        ["+title+"](https://www.bilibili.com/video/"+song_name+"/)**",Types.Text.KMD)
                        ),
                    Module.Context(
                        Element.Text("UP:         ["+name+"](https://space.bilibili.com/"+mid+"/)",Types.Text.KMD)
                        ),
                    
                    Module.Container(
                        Element.Image(src=pic)
                        ),
                    Module.Countdown(datetime.now() + timedelta(seconds=duration[guild]), mode=Types.CountdownMode.SECOND),

                    Module.ActionGroup(
                        Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                        Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                        Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)
                        )
                    
                )
        cm.append(c)
        msgid[guild]=(await bot.send(
            await bot.fetch_public_channel(
                channel[guild]
            ),
            cm
            ))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e)=="'data'":
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '未检索到此歌曲',
            )
        elif str(e)=="'NoneType' object has no attribute 'group'":
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                'BV号或链接输入有误',
            )
        else:    
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '发生错误，正在重试',
            )
        duration[guild]=0
        playtime[guild]=0
        LOCK[guild]=False
        return
    LOCK[guild]=False
    return

async def neteaseradio(guild,song_name):
    global deltatime
    global playtime
    global playlist
    global duration
    global p
    global netease_phone
    global netease_passwd
    global firstlogin
    global neteasecookie
    global LOCK
    LOCK[guild]=True
    try:
        headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Cookie': netease_cookie,
                'Host': '127.0.0.1:3000',
                'Referer': 'https://music.163.com',
                'If-None-Match': 'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': "Windows",
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
            }
        song_name=song_name.replace(" ", "")
        song_name=song_name.split('-')[-1]
        print(song_name)
        url='http://127.0.0.1:3000/dj/program/detail?id='+song_name
        response=requests.get(url=url,timeout=5,headers=headers).json()
        print(response['code'])
        if response['code']==404 or response['code']==400:
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '未检索到此歌曲',
            )
            playlist[guild].pop(0)
            duration[guild]=0
            playtime[guild]=0
            LOCK[guild]=False
            return
        response=response['program']
        duration[guild]=int(response['duration']/1000)+deltatime
        song_url='https://music.163.com/#/program?id='+song_name
        song_name=response['mainSong']['name']

        ban=re.compile('(惊雷)|(Lost Rivers)')
        resu=ban.findall(song_name)
        print(resu)
        if len(resu)>0:
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '吃了吗，没吃吃我一拳',
            )
            duration[guild]=0
            playtime[guild]=0
            LOCK[guild]=False
            return

        album_name=response['radio']['name']
        if album_name=='':
            album_name='无专辑'
        album_url='https://music.163.com/#/djradio?id='+str(response['radio']['id'])

        singer_name=response['dj']['nickname']
        singer_url='https://music.163.com/#/user/home?id='+str(response['dj']['userId'])
        pic_url=response['radio']['picUrl']
        getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['mainSong']['id'])+'&br=320000'
        urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data'][0]['url']
        print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['mainSong']['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data']['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['mainSong']['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data'][0]['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['mainSong']['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data']['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['mainSong']['id'])+'?timestamp='
            urlresponse=requests.get(url=getfile_url,headers=headers,timeout=5).json()['data'][0]['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        if urlresponse.endswith("flac"):
            async with aiohttp.ClientSession() as session:
                async with session.get(urlresponse,timeout=aiohttp.ClientTimeout(total=5)) as r:
                    with open(guild+".flac", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild)
            p[guild] = subprocess.Popen(
                'ffmpeg -re -nostats -i "'+guild+'.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],
                shell=True
            )
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(urlresponse,timeout=aiohttp.ClientTimeout(total=5)) as r:
                    with open(guild+"_"+botid+".mp3", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild)
            p[guild] = start_play(guild)



        playtime[guild] = 0

        
        delmsg(msgid[guild])
        cm = CardMessage()
        c=get_playlist(guild)
        cm.append(c)
        c=Card(
                    Module.Header("正在播放： "+ song_name),
                    Module.Context(
                        Element.Text("歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")",Types.Text.KMD)
                        ),
                    
                    Module.File(Types.File.AUDIO, src=urlresponse, title=song_name, cover=pic_url),
                    Module.Countdown(datetime.now() + timedelta(seconds=duration[guild]), mode=Types.CountdownMode.SECOND),
                    Module.Divider(),
                    Module.Context(
                        Element.Image(src="https://img.kookapp.cn/assets/2022-05/UmCnhm4mlt016016.png"),
                        Element.Text("网易云音乐  [在网页查看](" + song_url + ")",Types.Text.KMD)),
                    Module.ActionGroup(
                        Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                        Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                        Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)
                        )
                    
                )
        cm.append(c)
        print(json.dumps(cm))
        msgid[guild]=(await bot.send(
            await bot.fetch_public_channel(
                channel[guild]
            ),
            cm
            ))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        await bot.send(
            await bot.fetch_public_channel(
                channel[guild]
            ),
            '发生错误，请重试',
        )
        playlist[guild].pop(0)
        duration[guild]=0
        playtime[guild]=0
        LOCK[guild]=False
        return
    LOCK[guild]=False
    return

async def qqmusic(guild,song_name):
    global deltatime
    global playtime
    global playlist
    global duration
    global p
    global netease_phone
    global netease_passwd
    global firstlogin
    global neteasecookie
    global LOCK
    LOCK[guild]=True
    try:
        if playlist[guild][0]['time']>int(round(time.time() * 1000)):
            song_name=song_name.split('-')[-1]
            musicid=song_name
        else:
            url="http://127.0.0.1:3300/search/quick?key="+song_name
            response=requests.get(url=url,timeout=5).json()['data']['song']['itemlist'][0]
            musicid=response['mid']
            
        
        url="http://127.0.0.1:3300/song?songmid="+musicid
        response=requests.get(url=url,timeout=5).json()['data']['track_info']
        song_name=response['name']
        duration[guild]=response['interval']+deltatime
        song_url='https://y.qq.com/n/ryqq/songDetail/'+response['mid']
        album_name=response['album']['name']
        if album_name=='':
            album_name='无专辑'
        album_url='https://y.qq.com/n/ryqq/albumDetail/'+response['album']['mid']
        singer_name=response['singer'][0]['name']
        singer_url='https://y.qq.com/n/ryqq/singer/'+response['singer'][0]['mid']
        pic_url='https://y.gtimg.cn/music/photo_new/T002R300x300M000'+response['album']['mid']+'.jpg'
        getfile_url='http://127.0.0.1:3300/song/url?id='+response['mid']+'&mediaId='+response['file']['media_mid']+'&ownCookie=1'
        ban=re.compile('(惊雷)|(Lost Rivers)')
        resu=ban.findall(song_name)
        if len(resu)>0:
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '吃了吗，没吃吃我一拳',
            )
            duration[guild]=0
            playtime[guild]=0
            LOCK[guild]=False
            return
        try:
            urlresponse=requests.get(url=getfile_url,timeout=5).json()['data']
        except:
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                'api cookie失效',
            )
            playlist[guild].pop(0)
            duration[guild]=0
            playtime[guild]=0
            LOCK[guild]=False
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(urlresponse,timeout=aiohttp.ClientTimeout(total=5)) as r:
                with open(guild+"_"+botid+".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)
        
        playtime[guild] = 0
        kill(guild)
        
        p[guild] = subprocess.Popen(
            'ffmpeg -re -nostats -i "'+guild+"_"+botid+'.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],
            shell=True
        )
        delmsg(msgid[guild])
        cm = CardMessage()
        c=get_playlist(guild)
        cm.append(c)
        c=Card(
                    Module.Header("正在播放： "+ song_name),
                    Module.Context(
                        Element.Text("歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")",Types.Text.KMD)
                        ),
                    
                    Module.File(Types.File.AUDIO, src=urlresponse, title=song_name, cover=pic_url),
                    Module.Countdown(datetime.now() + timedelta(seconds=duration[guild]), mode=Types.CountdownMode.SECOND),
                    Module.Divider(),
                    Module.Context(
                        Element.Image(src="https://img.kookapp.cn/assets/2022-06/cqzmClO3Sq07s07x.png"),
                        Element.Text("QQ音乐  [在网页查看](" + song_url + ")",Types.Text.KMD)),
                    Module.ActionGroup(
                        Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                        Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                        Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)
                        )
                    
                )
        cm.append(c)
        msgid[guild]=(await bot.send(
            await bot.fetch_public_channel(
                channel[guild]
            ),
            cm
            ))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e)=="list index out of range":
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '未检索到此歌曲',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '发生错误，正在重试',
            )
        duration[guild]=0
        playtime[guild]=0
        LOCK[guild]=False
        return
    LOCK[guild]=False
    return

async def migu(guild,song_name):
    global deltatime
    global playtime
    global playlist
    global duration
    global p
    global LOCK
    LOCK[guild]=True
    try:
        if playlist[guild][0]['time']>int(round(time.time() * 1000)):
            song_name=song_name.split('-')[-1]
            musicid=song_name
        else:   
            
            url="http://127.0.0.1:3400/song/find?keyword="+song_name
            response=requests.get(url=url,timeout=5).json()
            musicid=str(response['data']['cid'])

        url='http://127.0.0.1:3400/song?cid='+musicid

        response=requests.get(url=url,timeout=5).json()["data"]
        duration[guild]=response["duration"]+deltatime
        song_name=response["name"]
        
        ban=re.compile('(惊雷)|(Lost Rivers)')
        resu=ban.findall(song_name)
        print(resu)
        if len(resu)>0:

            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    config["channel"]
                ),
                '吃了吗，没吃吃我一拳',
            )
            duration[guild]=0
            playtime[guild]=0
            LOCK[guild]=False
            return
        
        song_url='https://music.migu.cn/v3/music/song/'+response['cid']
        album_name=response['album']['name']
        if album_name=='':
            album_name='无专辑'
        album_url='https://music.migu.cn/v3/music/album/'+response['album']['id']
        singer_name=response['artists'][0]['name']
        singer_url='https://music.migu.cn/v3/music/artist/'+response['artists'][0]['id']
        pic_url=response["picUrl"]
        
        urlresponse=response["320"]
        
        
        async with aiohttp.ClientSession() as session:
            async with session.get(urlresponse,timeout=aiohttp.ClientTimeout(total=5)) as r:
                with open(guild+"_"+botid+".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)
        kill(guild)
        p[guild] = start_play(guild)
        playtime[guild] = 0
        if len(song_name)>50:
            song_name=song_name[:50]
        delmsg(msgid[guild])
        cm = CardMessage()
        c=get_playlist(guild)
        cm.append(c)
        c=Card(
                    Module.Header("正在播放： "+ song_name),
                    Module.Context(
                        Element.Text("歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")",Types.Text.KMD)
                        ),
                    
                    Module.File(Types.File.AUDIO, src=urlresponse, title=song_name, cover=pic_url),
                    Module.Countdown(datetime.now() + timedelta(seconds=duration[guild]), mode=Types.CountdownMode.SECOND),
                    Module.Divider(),
                    Module.Context(
                        Element.Image(src="https://img.kookapp.cn/assets/2022-07/dhSP597xJ502s02r.png"),
                        Element.Text("咪咕音乐  [在网页查看](" + song_url + ")",Types.Text.KMD)),
                    Module.ActionGroup(
                        Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                        Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                        Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)
                        )
                    
                )
        cm.append(c)
        msgid[guild]=(await bot.send(
            await bot.fetch_public_channel(
                channel[guild]
            ),
            cm
            ))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e)=="'songs'":
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '未检索到此歌曲',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '发生错误，正在重试',
            )
        playlist[guild].pop(0)
        duration[guild]=0
        playtime[guild]=0
        LOCK[guild]=False
        return
    LOCK[guild]=False
    return
async def kmusic(guild,song_name):
    global deltatime
    global playtime
    global playlist
    global duration
    global p
    global LOCK
    LOCK[guild]=True
    try:
        try:
            
            pattern=r'(?<=\[)(.*?)(?=\])'
            song_name=re.search(pattern,song_name).group()
        except Exception as e:
            print(e)
        response=requests.get(url=song_name,timeout=5).text
        
        pattern=r'(?<=window.__DATA__ = ).*?(?=; </script>)'
        response=json.loads(re.search(pattern,response).group())
        
        song_name=response['detail']['song_name']
        
        song_url='https://node.kg.qq.com/play?s='+response['shareid']
        
        singer_name=response['detail']['nick']
        singer_url='https://node.kg.qq.com/personal?uid='+response['detail']['uid']
        pic_url=response['detail']['cover']
        urlresponse=response['detail']['playurl']
        ban=re.compile('(惊雷)|(Lost Rivers)')
        resu=ban.findall(song_name)
        if len(resu)>0:
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '吃了吗，没吃吃我一拳',
            )
            duration[guild]=0
            playtime[guild]=0
            LOCK[guild]=False
            return
        if response['detail']['segment_end']!=0:
            duration[guild]=int(response['detail']['segment_end']/1000)+deltatime
        else:
            url="http://127.0.0.1:3300/song?songmid="+re.search(r'(?<=songmid=)[0-9|a-z|A-Z]+',response['songinfo']['data']['song_url']).group()
            response=requests.get(url=url,timeout=5).json()['data']['track_info']
            duration[guild]=response['interval']+deltatime
        async with aiohttp.ClientSession() as session:
            async with session.get(urlresponse,timeout=aiohttp.ClientTimeout(total=5)) as r:
                with open(guild+"_"+botid+".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)
        
        playtime[guild] = 0
        kill(guild)
        
        p[guild] = start_play(guild)
        playlist[guild][0]['name']=song_name
        delmsg(msgid[guild])
        cm = CardMessage()
        c=get_playlist(guild)
        cm.append(c)
        c=Card(
                    Module.Header("正在播放： "+ song_name),
                    Module.Context(
                        Element.Text("歌手： [" + singer_name + "](" + singer_url + ")",Types.Text.KMD)
                        ),
                    
                    Module.File(Types.File.AUDIO, src=urlresponse, title=song_name, cover=pic_url),
                    Module.Countdown(datetime.now() + timedelta(seconds=duration[guild]), mode=Types.CountdownMode.SECOND),
                    Module.Divider(),
                    Module.Context(
                        Element.Image(src="https://img.kookapp.cn/assets/2022-07/BP8vZb06hs0a409n.png"),
                        Element.Text("全民K歌  [在网页查看](" + song_url + ")",Types.Text.KMD)),
                    Module.ActionGroup(
                        Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                        Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                        Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)
                        )
                    
                )
        cm.append(c)
        msgid[guild]=(await bot.send(
            await bot.fetch_public_channel(
                channel[guild]
            ),
            cm
            ))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e)=="'songs'":
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '未检索到此歌曲',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '发生错误，正在重试',
            )
        playlist[guild].pop(0)
        duration[guild]=0
        playtime[guild]=0
        LOCK[guild]=False
        return
    LOCK[guild]=False
    return
async def ytb(guild,song_name):
    global deltatime
    global playtime
    global playlist
    global duration
    global p
    global LOCK
    LOCK[guild]=True
    try:
        song_name=parse_kmd_to_url(song_name)
        result = YouTube(song_name)
        title=result.title.replace("[","【").replace("]","】")
        name=result.author
        duration[guild]=result.length
        playtime[guild] = 0
        result.streams.get_by_itag(251).download(output_path='.',filename=guild+"_"+botid+".mp3")
        kill(guild)
        p[guild] = start_play(guild)
        playlist[guild][0]['name']=title
        delmsg(msgid[guild])
        cm = CardMessage()
        c=get_playlist(guild)
        cm.append(c)
        c=Card(
                    Module.Context(
                        Element.Text("**标题:        ["+title+"]("+song_name+")**",Types.Text.KMD)
                        ),
                    Module.Context(
                        Element.Text("UP:         "+name,Types.Text.KMD)
                        ),
                    Module.Countdown(datetime.now() + timedelta(seconds=duration[guild]), mode=Types.CountdownMode.SECOND),

                    Module.ActionGroup(
                        Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                        Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                        Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)
                        )
                    
                )
        cm.append(c)
        msgid[guild]=(await bot.send(
            await bot.fetch_public_channel(
                channel[guild]
            ),
            cm
            ))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if 'is unavailable' in str(e):
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '未检索到此视频',
            )
        elif str(e)==r"regex_search: could not find match for (?:v=|\/)([0-9A-Za-z_-]{11}).*":
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '链接输入有误',
            )
        else:    
            await bot.send(
                await bot.fetch_public_channel(
                    channel[guild]
                ),
                '发生错误，正在重试',
            )   
        duration[guild]=0
        playtime[guild]=0
        LOCK[guild]=False
        return
    LOCK[guild]=False
    return
        
def save_cache():
    global playlist
    with open(botid+'playlistcache', 'w',encoding='utf-8') as f:
        f.write(str(playlist))
    global voicechannelid
    with open(botid+'voiceidcache', 'w',encoding='utf-8') as f:
        f.write(str(voicechannelid))
    global msgid
    with open(botid+'msgidcache', 'w',encoding='utf-8') as f:
        f.write(str(msgid))
    global channel
    with open(botid+'channelidcache', 'w',encoding='utf-8') as f:
        f.write(str(channel))
def load_cache():
    try:
        print('loading cache')
        global playlist
        global p
        global port
        global rtcpport
        global channel
        global voice
        global voicechannelid
        global msgid
        global channel
        
        with open(botid+'playlistcache', 'r',encoding='utf-8') as f:
            playlist=eval(f.read())
        with open(botid+'voiceidcache', 'r',encoding='utf-8') as f:
            voicechannelid=eval(f.read())
        with open(botid+'msgidcache', 'r',encoding='utf-8') as f:
            msgid=eval(f.read())
        with open(botid+'channelidcache', 'r',encoding='utf-8') as f:
            channel=eval(f.read())
        for guild, voiceid in voicechannelid.items():
            print(voiceid)
            singleloops[guild]=0
            timeout[guild]=0
            LOCK[guild]=False
            playtime[guild]=0
            duration[guild]=0
            port[guild]=rtcpport
            voice[guild] = Voice(config['token'+botid])
            event_loop = asyncio.get_event_loop()
            asyncio.ensure_future(start(voice[guild],voiceid,guild),loop=event_loop)
            time.sleep(0.3)
    except:
        print('load cache fail')
@bot.task.add_interval(seconds=deltatime)
async def update_played_time_and_change_music():
    global deltatime
    global playtime
    global playlist
    global duration
    global p
    global netease_phone
    global netease_passwd
    global firstlogin
    global neteasecookie
    global timeout
    global voice
    global LOCK
    global singleloops
    global load
    print("STEP1")
    if firstlogin==True:
        firstlogin=False
        print("id:"+botid)
        print('login check')
        print(await status_active_music())
        url='http://127.0.0.1:3000/login/status?timestamp='
        print(url)
        response=requests.get(url=url,timeout=5).json()
        print(response)
        try:
            response=response['data']['account']['status']
            if response==-10:
                url='http://127.0.0.1:3000/login/cellphone?phone='+netease_phone+'&password='+netease_passwd
                print(requests.get(url=url,timeout=5).json())
                print('网易云登陆成功')
        except:
            url='http://127.0.0.1:3000/login/cellphone?phone='+netease_phone+'&password='+netease_passwd
            print(requests.get(url=url,timeout=5).json())
            print('网易云登陆成功')
        print('网易已登录')
        url='http://127.0.0.1:3000/login/refresh'
        requests.get(url=url,timeout=5)
        print('刷新登录cookie')
        if qq_enable=="1":
            url='http://127.0.0.1:3300/user/setCookie'
            data={
                "data":qq_cookie
            }
            
            response=requests.post(url=url,timeout=5,json=data)
            print(response.text)
            url='http://127.0.0.1:3300/user/getCookie?id='+qq_id
            response=requests.get(url=url,timeout=5)
            print(response.text)
            print('QQ已登录')
    if load==True:
        load=False
        load_cache()
    print("STEP2")
    
    deletelist=[]
    tasks=[]
    for guild, songlist in playlist.items():
        if LOCK[guild]==True:
            continue
        if channel.get(guild,-1)==-1 or timeout.get(guild,-1)==-1 or voiceffmpeg.get(guild,-1)==-1:
            continue
        if len(playlist[guild]) == 0:
            timeout[guild]+=deltatime
            if timeout[guild]>60:
                delmsg(msgid[guild])
                await disconnect(guild)
                deletelist.append(guild)
            continue
        else:
            timeout[guild]=0
            if playtime[guild] == 0:
                if singleloops[guild]==3:
                    random.shuffle(playlist[guild])
                else:
                    playlist[guild].sort(key=lambda x: list(x.values())[3])
                
                song_name = playlist[guild][0]['name']
                if song_name == "":
                    continue
                if playlist[guild][0]['type'] in {'网易','netease','Netease','网易云','网易云音乐','网易音乐'}: 
                    event_loop = asyncio.get_event_loop()
                    asyncio.ensure_future(netease(guild,song_name),loop=event_loop)
                elif playlist[guild][0]['type'] in {'bili','b站','bilibili','Bili','Bilibili','B站'}:
                    event_loop = asyncio.get_event_loop()
                    asyncio.ensure_future(bili(guild,song_name),loop=event_loop)
                elif playlist[guild][0]['type'] in {'网易电台','电台'}:
                    event_loop = asyncio.get_event_loop()
                    asyncio.ensure_future(neteaseradio(guild,song_name),loop=event_loop)
                elif playlist[guild][0]['type'] in {'qq','qq音乐','QQ','QQ音乐'}:
                    event_loop = asyncio.get_event_loop()
                    asyncio.ensure_future(qqmusic(guild,song_name),loop=event_loop)
                elif playlist[guild][0]['type'] in {'k歌','K歌','全民k歌','全民K歌'}:
                    event_loop = asyncio.get_event_loop()
                    asyncio.ensure_future(kmusic(guild,song_name),loop=event_loop)
                elif playlist[guild][0]['type'] in {'ytb','YTB','youtube','Youtube','油管'}:
                    event_loop = asyncio.get_event_loop()
                    asyncio.ensure_future(ytb(guild,song_name),loop=event_loop)
                else:
                    asyncio.ensure_future(migu(guild,song_name))
            else:
                if playtime[guild] + deltatime < duration[guild]:
                    playtime[guild] += deltatime
                else:
                    playtime[guild]= 0
                    if singleloops[guild]==0:
                        playlist[guild].pop(0)
                    if singleloops[guild]==1:
                        pass
                    if singleloops[guild]==2:
                        playlist[guild].append(playlist[guild].pop(0))
    print("STEP3")
    if len(tasks)>0:
        event_loop = asyncio.get_event_loop()
        asyncio.ensure_future(asyncio.wait(tasks),loop=event_loop)
        save_cache()
    tmpflag=0
    for guild in deletelist:
        tmpflag=1
        del playlist[guild]
    if tmpflag==1:
        save_cache()
@bot.task.add_interval(minutes=30)
async def keep_login():
    url='http://127.0.0.1:3000/login/refresh'
    requests.get(url=url,timeout=5)
    if qq_enable == '1':
        url='http://127.0.0.1:3300/user/refresh'
        requests.get(url=url,timeout=5)
    print('刷新登录')

@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def on_btn_clicked(_: Bot, e: Event):
    print(f'''{e.body['user_info']['nickname']} took the {e.body['value']} pill''')
    print(e.body["guild_id"])
    global playlist
    global playtime
    global duration
    global singleloops
    guild=e.body["guild_id"]
    if e.body['value']=="NEXT":
        try:
            kill(guild)
            if len(playlist[guild])==0:
                return
            if singleloops[guild]==2:
                playlist[guild].append(playlist[guild].pop(0))
            else:
                playlist[guild].pop(0)
            LOCK[guild]=False
            playtime[guild]=0
            duration[guild]=0
            await bot.send(await bot.fetch_public_channel(channel[guild]),"来自"+e.body['user_info']['nickname']+"的操作:已切换下一首")
        except:
            pass
    if e.body['value']=="CLEAR":
        try:
            if len(playlist[guild])>0:
                now=playlist[guild][0]
                playlist[guild]=[]
                playlist[guild].append(now)
            await bot.send(await bot.fetch_public_channel(channel[guild]),"来自"+e.body['user_info']['nickname']+"的操作:清空完成")
        except:
            pass
    if e.body['value']=="LOOP":
        
        try:
            if singleloops[guild]==0:
                singleloops[guild]=1
                await bot.send(await bot.fetch_public_channel(channel[guild]),"来自"+e.body['user_info']['nickname']+"的操作:循环模式已调整为:单曲循环")
            elif singleloops[guild]==1:
                singleloops[guild]=2
                await bot.send(await bot.fetch_public_channel(channel[guild]),"来自"+e.body['user_info']['nickname']+"的操作:循环模式已调整为:列表循环")
            elif singleloops[guild]==2:
                singleloops[guild]=3
                await bot.send(await bot.fetch_public_channel(channel[guild]),"来自"+e.body['user_info']['nickname']+"的操作:循环模式已调整为:随机播放")
            else :
                singleloops[guild]=0
                await bot.send(await bot.fetch_public_channel(channel[guild]),"来自"+e.body['user_info']['nickname']+"的操作:循环模式已调整为:关闭")
        except:
            pass

@bot.on_event(EventTypes.EXITED_CHANNEL)
async def on_exit_voice(_: Bot, e: Event):
    try:
        global playlist
        print(e.body)
        guild=e.target_id
        now=playlist[guild][0]
        tmp=[song for song in playlist[guild] if song['userid'] != e.body['user_id']]
        tmp.insert(0,now)
        playlist[guild]=tmp  
    except Exception as e:
        print(str(e))

async def voice_Engine(voice,voiceid:str,guild):
    global rtcpport
    global voiceffmpeg
    print(voiceid)
    rtp_url=''
    voice.channel_id = voiceid
    while True:
        if len(voice.rtp_url) != 0:
            rtp_url = voice.rtp_url
            comm="ffmpeg -re -loglevel level+info -nostats -stream_loop -1 -i zmq:tcp://127.0.0.1:"+port[guild]+" -map 0:a:0 -acodec libopus -ab 128k -filter:a volume=0.15 -ac 2 -ar 48000 -f tee [select=a:f=rtp:ssrc=1357:payload_type=100]"+rtp_url
            print(comm)
            voiceffmpeg[guild]=subprocess.Popen(comm,shell=True)
            rtcpport=str(int(rtcpport)+1)
            break
        await asyncio.sleep(0.1)

bot.command.update_prefixes("")

event_loop = asyncio.get_event_loop()
asyncio.ensure_future(bot.start(), loop=event_loop)
event_loop.run_forever()
