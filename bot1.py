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
nest_asyncio.apply()
botid=os.path.basename(__file__).split(".")[0].replace('bot','')
with open("config.json", "r", encoding="utf-8") as f:
    configstr = f.read().replace('\\', '!')
    configtmp = json.loads(configstr)
    config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
rtcpport=botid+'234'
firstlogin=True
playtime = {}
LOCK = {}
channel = {}
duration = {}
msgid = {}
voice = {}
voiceffmpeg = {}
timeout = {}
netease_phone = config["n_phone"]
netease_passwd = config["n_passwd"]
netease_cookie = config["n_cookie"]
qq_cookie = config["q_cookie"]
qq_id = config["q_id"]
qq_enable = config["qq_enable"]
bot = Bot(token=config['token'+botid])
playlist = {'0':[]}#guild list
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
          "content": "**1.  点歌   +    (平台)    +    歌名**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将歌曲加到播放队列中\ntips:\n歌名中如果有英文引号等特殊字符，需要将歌名用英文引号括起来\n例如  **点歌 \"Rrhar'il\"**\n如果需要指定歌曲版本播放，可以在歌名后添加歌手\n例如  **点歌 勇敢勇敢-黄勇**\n现支持QQ音乐、网易云音乐、网易云音乐电台与B站，若不写平台则默认从网易云获取数据（QQ音乐需要单独安装api并在config.json中启用平台、网易云电台仅支持从节目id点播）\n例如  **点歌 qq heavensdoor**\n例如  **点歌 网易 勇敢勇敢-黄勇**\n例如  **点歌 b站 BV1qa411e7Fi**\n例如  **点歌 你看到的我**\n例如  **点歌 网易电台 2499131107**"
        }
      },
      {
        "type": "divider"
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
        "type": "divider"
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
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**4.  导入歌单       +       网易云歌单id**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将网易云歌单中的歌曲导入到播放队列\n例如  **导入歌单 977171340**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**5.  导入电台       +       网易云电台id**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将网易电台中的歌曲导入到播放队列\n例如  **导入电台 972583481**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**6.  清空歌单**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    清空播放队列"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**7.  搜索       +       歌名**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    从网易云与qq音乐搜索歌曲（qq平台需单独打开）\n例如  **搜索 海阔天空**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**8.  单曲循环**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    切换单曲循环状态"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**9.  重新连接**"
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
    data=requests.get(url).json()['data']
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
    audioUrl=requests.get(url).json()['data']['dash']['audio'][0]['baseUrl']
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
    response=requests.get(url=audioUrl, headers=headers)
    open(guild+".mp3", "wb").write(response.content)
    return bvid,cid,title,mid,name,pic

@bot.command(name='导入歌单')
async def import_netease_playlist(msg: Message, linkid : str):
    global netease_cookie
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
            url = "http://127.0.0.1:3000/playlist/track/all?id="+linkid+'&limit=1000&offset='+str(offset*1000)
            offset+=1
            async with aiohttp.ClientSession() as session:
                async with session.get(url,headers=headers) as r:
                    resp_json = await r.json() 
                    songs = resp_json.get("songs",[])
                    if len(songs)==0:
                        break
                    for song in songs:
                        playlist[msg.ctx.guild.id].append({'name':song.get('name','')+"-"+song.get('ar',[])[0].get('name','')+'-'+str(song.get('id')),'userid':msg.author.id,'type':'网易','time':int(round(time.time() * 1000))+1000000000000})
        await msg.ctx.channel.send("导入完成")
    except:
        pass
@bot.command(name='导入专辑')
async def import_netease_album(msg: Message, linkid : str):
    global netease_cookie
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
            async with session.get(url,headers=headers) as r:
                resp_json = await r.json() 
                songs = resp_json.get("songs",[])

                for song in songs:
                        playlist[msg.ctx.guild.id].append({'name':song.get('name','')+"-"+song.get('ar',[])[0].get('name','')+'-'+str(song.get('id')),'userid':msg.author.id,'type':'网易','time':int(round(time.time() * 1000))+1000000000000})
        await msg.ctx.channel.send("导入完成")
    except:
        pass

@bot.command(name='导入电台')
async def import_netease_radio(msg: Message, linkid : str):
    global netease_cookie
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
                async with session.get(url,headers=headers) as r:
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
@bot.command(name=botid+'号加入语音')
async def connect(msg: Message):
    global playlist
    global p
    global port
    global rtcpport
    global channel
    global voice
    global msgid
    if len(voice)==2:
        await msg.ctx.channel.send("播放槽位已满")
        return 
    voiceid=await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid=voiceid[0].id
    except:
        await msg.ctx.channel.send("请先进入一个语音频道或退出重进")
        return
    print(voiceid)
    singleloops[msg.ctx.guild.id]=False
    timeout[msg.ctx.guild.id]=0
    LOCK[msg.ctx.guild.id]=False
    playlist[msg.ctx.guild.id]=[]
    channel[msg.ctx.guild.id]=msg.ctx.channel.id
    playtime[msg.ctx.guild.id]=0
    msgid[msg.ctx.guild.id]="0"
    duration[msg.ctx.guild.id]=0
    port[msg.ctx.guild.id]=rtcpport
    await msg.ctx.channel.send("已加入频道")
    voice[msg.ctx.guild.id] = Voice(config['token'+botid])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(voice[msg.ctx.guild.id],voiceid,msg.ctx.guild.id))
    
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
##    while True:
##        if not voice[guild].is_exit:
##            break
##        await asyncio.sleep(0.1)
    del timeout[guild]
    del voiceffmpeg[guild]
    del voice[guild]
    del LOCK[guild]
    #del playlist[guild]
    del msgid[guild]
    del channel[guild]
    del singleloops[guild]
    del playtime[guild]
    del duration[guild]
    del port[guild]
    print(str(guild)+" disconnected")
async def disconnecthandle(guild):
    await asyncio.wait([disconnect(guild)])
@bot.command(name='绑定点歌频道')
async def connect(msg: Message):
    global channel
    await msg.ctx.channel.send("绑定频道")
    channel[msg.ctx.guild.id]=msg.ctx.channel.id
    

@bot.command(name='清空歌单')
async def clear_playlist(msg: Message):
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
        global playlist
        global playtime

        global duration
        
        kill(msg.ctx.guild.id)
        if len(playlist[msg.ctx.guild.id])==0:
            await msg.ctx.channel.send("无下一首")
            return None
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
        args=list(args)
        global playlist
        typ='网易'
        song_name=''
        if args[0]=='qq' or args[0]=='网易' or args[0]=='b站'or args[0]=='网易电台'or args[0]=='咪咕':
            typ=args[0]
            args.pop(0)
            if typ=='qq' and qq_enable == '0':
                await msg.ctx.channel.send('未启用qq点歌')
                return None
        for st in args:
            song_name = song_name + st + " "
        playlist[msg.ctx.guild.id].append({'name':song_name,'userid':msg.author.id,'type':typ,'time':int(round(time.time() * 1000))})
        await msg.ctx.channel.send("已添加")
    except:
        pass

@bot.command(name="RELOAD")
async def addmusic(msg: Message):
    global config
    global firstlogin
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            configstr = f.read().replace('\\', '!')
            configtmp = json.loads(configstr)
            config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
        firstlogin=True
        await msg.ctx.channel.send("reload成功")
    except:
        await msg.ctx.channel.send("reload失败")
        
@bot.command(name="REBOOT"+str(botid))
async def addmusic(msg: Message):
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
@bot.command(name="单曲循环")
async def singlesongloop(msg: Message):
    global singleloops
    try:
        if singleloops[msg.ctx.guild.id]==False:
            singleloops[msg.ctx.guild.id]=True
            await msg.ctx.channel.send('单曲循环已打开')
        else:
            singleloops[msg.ctx.guild.id]=False
            await msg.ctx.channel.send('单曲循环已关闭')
    except:
        pass
@bot.command(name="重新连接")
async def reconnect(msg: Message):
    global voiceffmpeg
    global voice
    global port
    global rtcpport
    voiceid=await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid=voiceid[0].id
    except:
        await msg.ctx.channel.send("请先进入一个语音频道或退出重进")
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
        del voiceffmpeg[msg.ctx.guild.id]
        await msg.ctx.channel.send("已加入频道")
        voice[msg.ctx.guild.id] = Voice(config['token'+botid])
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start(voice[msg.ctx.guild.id],voiceid,msg.ctx.guild.id))
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
    songs=requests.get(url=url,headers=headers).json()['result']['songs']
    text='网易云结果:\n'
    try:
        for song in songs:
            text+=song['name']+'-'+song['artists'][0]['name']+'-'+song['album']['name']+'-'+str(song['id'])+'\n'
    except:
        text+='无\n'

    if qq_enable== '1':
        text+='QQ结果:\n'
        url="http://127.0.0.1:3300/search?key="+song_name+"&pageSize=5"
        songs=requests.get(url=url).json()['data']['list']
        try:
            for song in songs:
                text+=song['songname']+'-'+song['singer'][0]['name']+'-'+song['albumname']+'\n'
        except:
            text+='无\n'

    text+='网易电台结果:\n'
    url="http://127.0.0.1:3000/search?keywords="+song_name+"&limit=5&type=2000"
    songs=requests.get(url=url).json()['data']['resources']
    try:
        for song in songs:
            text+=song['baseInfo']['mainSong']['name']+'-'+song['baseInfo']['mainSong']['artists'][0]['name']+'-'+song['resourceId']+'\n'
    except:
        text+='无\n'

    text+='咪咕结果:\n'
    url="http://127.0.0.1:3400/search?keyword="+song_name
    songs=requests.get(url=url).json()['data']['list']
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
    response=requests.post(url=url,json=data,headers=headers)
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
            response=requests.get(url=url,headers=headers).json()
            musicid=str(response['result']['songs'][0]['id'])

        url='http://127.0.0.1:3000/song/detail?ids='+musicid

        response=requests.get(url=url,headers=headers).json()['songs'][0]
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
        
        urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
        print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])+'&br=320000&timestamp='+str(int(round(time.time() * 1000)))
            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''

        

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        
        if urlresponse.endswith("flac"):
            async with aiohttp.ClientSession() as session:
                async with session.get(urlresponse) as r:
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
                async with session.get(urlresponse) as r:
                    with open(guild+".mp3", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild)
            p[guild] = subprocess.Popen(
                'ffmpeg -re -nostats -i "'+guild+'.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],
                shell=True
            )
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
                        Element.Button('单曲循环', 'LOOP', Types.Click.RETURN_VAL)
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
        song_name=song_name.replace(" ", "")
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
        p[guild] = subprocess.Popen(
            'ffmpeg -re -nostats -i "'+guild+'.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],
            shell=True
        )
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
                        Element.Button('单曲循环', 'LOOP', Types.Click.RETURN_VAL)
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
    except:
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
        response=requests.get(url=url,headers=headers).json()['program']
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
        urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
        print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['mainSong']['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['mainSong']['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''

        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['mainSong']['id'])+'&br=320000'
            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['mainSong']['id'])+'?timestamp='
            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
            print(urlresponse)
        if urlresponse==None:
            urlresponse=''
        if urlresponse.endswith("flac"):
            async with aiohttp.ClientSession() as session:
                async with session.get(urlresponse) as r:
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
                async with session.get(urlresponse) as r:
                    with open(guild+".mp3", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild)
            p[guild] = subprocess.Popen(
                'ffmpeg -re -nostats -i "'+guild+'.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],
                shell=True
            )



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
                        Element.Button('单曲循环', 'LOOP', Types.Click.RETURN_VAL)
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
    except:
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
        url="http://127.0.0.1:3300/search?key="+song_name+"&pageSize=1"
        response=requests.get(url=url).json()['data']['list'][0]
        song_name=response['songname']
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
        duration[guild]=response['interval']+deltatime
        song_url='https://y.qq.com/n/ryqq/songDetail/'+response['songmid']
        album_name=response['albumname']
        if album_name=='':
            album_name='无专辑'
        album_url='https://y.qq.com/n/ryqq/albumDetail/'+response['albummid']
        singer_name=response['singer'][0]['name']
        singer_url='https://y.qq.com/n/ryqq/singer/'+response['singer'][0]['mid']
        pic_url='https://y.gtimg.cn/music/photo_new/T002R300x300M000'+response['albummid']+'.jpg'
        getfile_url='http://127.0.0.1:3300/song/url?id='+response['songmid']+'&mediaId='+response['strMediaMid']+'&ownCookie=1'
        try:
            urlresponse=requests.get(url=getfile_url).json()['data']
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
            async with session.get(urlresponse) as r:
                with open(guild+".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)
        
        playtime[guild] = 0
        kill(guild)
        
        p[guild] = subprocess.Popen(
            'ffmpeg -re -nostats -i "'+guild+'.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],
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
                        Element.Button('单曲循环', 'LOOP', Types.Click.RETURN_VAL)
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
            response=requests.get(url=url).json()
            musicid=str(response['data']['cid'])

        url='http://127.0.0.1:3400/song?cid='+musicid

        response=requests.get(url=url).json()["data"]
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
            async with session.get(urlresponse) as r:
                with open(guild+".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)
        kill(guild)
        p[guild] = subprocess.Popen(
            'ffmpeg -re -nostats -i "'+guild+'.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+port[guild],
            shell=True
        )

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
                        Element.Button('单曲循环', 'LOOP', Types.Click.RETURN_VAL)
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
    if firstlogin==True:
        print("id:"+botid)
        print('login check')
        url='http://127.0.0.1:3000/login/status?timestamp='
        print(url)
        response=requests.get(url=url).json()
        print(response)
        try:
            response=response['data']['account']['status']
            if response==-10:
                url='http://127.0.0.1:3000/login/cellphone?phone='+netease_phone+'&password='+netease_passwd
                print(requests.get(url=url).json())
                print('网易云登陆成功')
        except:
            url='http://127.0.0.1:3000/login/cellphone?phone='+netease_phone+'&password='+netease_passwd
            print(requests.get(url=url).json())
            print('网易云登陆成功')
        print('网易已登录')
        url='http://127.0.0.1:3000/login/refresh'
        requests.get(url=url)
        print('刷新登录cookie')
        if qq_enable=="1":
            url='http://127.0.0.1:3300/user/setCookie'
            data={
                "data":qq_cookie
            }
            
            response=requests.post(url=url,json=data)
            print(response.text)
            url='http://127.0.0.1:3300/user/getCookie?id='+qq_id
            response=requests.get(url=url)
            print(response.text)
            print('QQ已登录')
        firstlogin=False
    deletelist=[]
    tasks=[]
    for guild, songlist in playlist.items():
        if channel.get(guild,-1)==-1:
            continue
        if len(playlist[guild]) == 0:
            timeout[guild]+=deltatime
            if timeout[guild]>60:
                delmsg(msgid[guild])
                loop = asyncio.get_event_loop()
                loop.run_until_complete(disconnecthandle(guild))
                deletelist.append(guild)
            continue
        else:
            timeout[guild]=0
            if playtime[guild] == 0:
                playlist[guild].sort(key=lambda x: list(x.values())[3])
                song_name = playlist[guild][0]['name']
                if song_name == "":
                    continue
                if playlist[guild][0]['type']=='网易':
                    if LOCK[guild]==True:
                        continue
                    tasks.append(asyncio.create_task(netease(guild,song_name)))
                    
                elif playlist[guild][0]['type']=='b站':
                    if LOCK[guild]==True:
                        continue
                    tasks.append(asyncio.create_task(bili(guild,song_name)))
                elif playlist[guild][0]['type']=='网易电台':
                    if LOCK[guild]==True:
                        continue
                    tasks.append(asyncio.create_task(neteaseradio(guild,song_name)))
                elif playlist[guild][0]['type']=='qq':
                    if LOCK[guild]==True:
                        continue
                    tasks.append(asyncio.create_task(qqmusic(guild,song_name)))
                    
                else:
                    if LOCK[guild]==True:
                        continue
                    tasks.append(asyncio.create_task(migu(guild,song_name)))
                continue
                    
            else:
                if playtime[guild] + deltatime < duration[guild]:
                    playtime[guild] += deltatime
                else:
                    playtime[guild]= 0
                    if singleloops[guild]==False:
                        playlist[guild].pop(0)
    if len(tasks)>0:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
    for guild in deletelist:
        del playlist[guild]
@bot.task.add_interval(minutes=30)
async def keep_login():
    url='http://bot.gekj.net/api/v1/online.bot'
    headers={
        "UUID": "7df0df10-2148-4090-a4d9-f4de31738bd2"
        }
    print(requests.post(headers=headers,url=url).text)
    url='http://127.0.0.1:3000/login/refresh'
    requests.get(url=url)
    url='http://127.0.0.1:3300/user/refresh'
    requests.get(url=url)
    print('刷新登录')

@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def print_btn_value(_: Bot, e: Event):
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

                return None
            playlist[guild].pop(0)
            LOCK[guild]=False
            playtime[guild]=0
            duration[guild]=0
        except:
            pass
    if e.body['value']=="CLEAR":
        try:
            if len(playlist[guild])>0:
                now=playlist[guild][0]
                playlist[guild]=[]
                playlist[guild].append(now)
            await bot.send(await bot.fetch_public_channel(channel[guild]),"清空完成")
        except:
            pass
    if e.body['value']=="LOOP":
        
        try:
            if singleloops[guild]==False:
                singleloops[guild]=True
                await bot.send(await bot.fetch_public_channel(channel[guild]),'单曲循环已打开')
            else:
                singleloops[guild]=False
                await bot.send(await bot.fetch_public_channel(channel[guild]),'单曲循环已关闭')
        except:
            pass

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
bot.run()
