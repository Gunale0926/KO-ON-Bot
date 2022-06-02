import json
import logging
import os
from khl import Message, Bot
import subprocess
import random
import time
import base64
import binascii
import string
from urllib import parse
import requests
from Crypto.Cipher import AES
import psutil
import re
starttime=0
pausetime=0
playtime=0
p = subprocess.Popen('echo',shell=True)

logging.basicConfig(level='INFO')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
pid = 0

bot = Bot(token=config['token'])

playlist=[""]
listid=0

# 从a-z,A-Z,0-9中随机获取16位字符
def get_random():
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    return random_str


# AES加密要求加密的文本长度必须是16的倍数，密钥的长度固定只能为16,24或32位，因此我们采取统一转换为16位的方法
def len_change(text):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    text = text.encode("utf-8")
    return text


# AES加密方法
def aes(text, key):
    # 首先对加密的内容进行位数补全，然后使用 CBC 模式进行加密
    iv = b'0102030405060708'
    text = len_change(text)
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(text)
    encrypt = base64.b64encode(encrypted).decode()
    return encrypt


# js中的 b 函数，调用两次 AES 加密
# text 为需要加密的文本， str 为生成的16位随机数
def b(text, str):
    first_data = aes(text, '0CoJUm6Qyw8W8jud')
    second_data = aes(first_data, str)
    return second_data


# 这就是那个巨坑的 c 函数
def c(text):
    e = '010001'
    f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    text = text[::-1]
    result = pow(int(binascii.hexlify(text.encode()), 16), int(e, 16), int(f, 16))
    return format(result, 'x').zfill(131)


# 获取最终的参数 params 和 encSecKey 的方法
def get_final_param(text, str):
    params = b(text, str)
    encSecKey = c(str)
    return {'params': params, 'encSecKey': encSecKey}


# 通过参数获取搜索歌曲的列表
def get_music_list(params, encSecKey):
    url = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token="

    payload = 'params=' + parse.quote(params) + '&encSecKey=' + parse.quote(encSecKey)
    headers = {
        'authority': 'music.163.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'origin': 'https://music.163.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://music.163.com/search/',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


# 通过歌曲的id获取播放链接
def get_reply(params, encSecKey):
    url = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token="
    payload = 'params=' + parse.quote(params) + '&encSecKey=' + parse.quote(encSecKey)
    headers = {
        'authority': 'music.163.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'origin': 'https://music.163.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://music.163.com/',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text





@bot.command(name='echo')
async def echo(msg: Message,*args):
    cm=[
  {
    "type": "card",
    "theme": "secondary",
    "size": "lg",
    "modules": [
      {
        "type": "section",
        "text": {
          "type": "plain-text",
          "content": ''.join(args)
        }
      }
    ]
  }
]
    await msg.ctx.channel.send(cm)

@bot.command(name='roll')
async def roll(msg: Message, *args):
    if len(args)>=2:
        t_min=int(args[0])
        t_max=int(args[1])
        n=1
        if len(args)==3:
            n=int(args[2])
        result = [random.randint(t_min, t_max) for i in range(n)]
        await msg.reply(f'you got: {result}')
    else:
        await msg.reply(cm)

@bot.command(name='search')
async def search(msg: Message, song_name: str):

    d = {"hlpretag": "<span class=\"s-fc7\">", "hlposttag": "</span>", "s": song_name, "type": "1", "offset": "0",
         "total": "true", "limit": "30", "csrf_token": ""}
    d = json.dumps(d)

    random_param =get_random()

    param =get_final_param(d, random_param)

    song_list =get_music_list(param['params'], param['encSecKey'])

    fmsg=""

    if len(song_list) > 0:
        song_list = json.loads(song_list)['result']['songs']
        for i, item in enumerate(song_list):
            item = json.dumps(item)
            fmsg = fmsg + str(i) + "：" + str(json.loads(str(item))['name'])+"      "+str(json.loads(str(item))['ar'][0]['name'])+"      "+str(json.loads(str(item))['al']['name'])+"      "+str(json.loads(str(item))['id'])+"\n"
            #fmsg = fmsg + str(i) + "：" + str(json.loads(str(item))['name'])+"\n"
        await msg.ctx.channel.send(fmsg)
    else:
        await msg.ctx.channel.send("未能搜索到相关歌曲信息")

@bot.command(name='getmusic-id')
async def getmusicfromid(msg: Message, song_id: str):

    d = {"ids": "[" + song_id + "]", "level": "standard", "encodeType": "","csrf_token": ""}
    d = json.dumps(d)
    random_param =get_random()
    param =get_final_param(d, random_param)
    song_info =get_reply(param['params'], param['encSecKey'])
    if len(song_info) > 0:
        song_info = json.loads(song_info)
        song_url = json.dumps(song_info['data'][0]['url'], ensure_ascii=False)
        print(song_url)
        cm=[
  {
    "type": "card",
    "theme": "danger",
    "size": "lg",
    "modules": [
      {
        "type": "audio",
        "title": "",
        "src": eval(song_url),
        "cover": ""
      }
    ]
  }
]
        if song_info['data'][0]['code']==-110:
            await msg.ctx.channel.send("需要会员或无版权，无法播放")
        else:
            await msg.ctx.channel.send(cm)
    else:
        await msg.ctx.channel.send("未能搜索到相关歌曲信息")
@bot.command(name='music')
async def getmusicfromname(msg: Message, *args):
    song_name=""
    for st in args:
        song_name=song_name+st+" "
    print(song_name)
    d = {"hlpretag": "<span class=\"s-fc7\">", "hlposttag": "</span>", "s": song_name, "type": "1", "offset": "0",
         "total": "true", "limit": "30", "csrf_token": ""}
    d = json.dumps(d)
    random_param = get_random()
    param = get_final_param(d, random_param)
    song_list = get_music_list(param['params'], param['encSecKey'])
    print(song_list)
    if json.loads(song_list)['result']['songCount'] > 0:
        song_list = json.loads(song_list)['result']['songs']
        for i, item in enumerate(song_list):
            item = json.dumps(item)
            print(str(i) + "：" + str(json.loads(str(item))['name']))
            d = {"ids": "[" + str(json.loads(str(item))['id']) + "]", "level": "standard", "encodeType": "",
                 "csrf_token": ""}
            d = json.dumps(d)
            param = get_final_param(d, random_param)
            song_info = get_reply(param['params'], param['encSecKey'])
            if len(song_info) > 0:
                song_info = json.loads(song_info)
                if song_info['data'][0]['code']==-110:
                    continue
                else:
                    print(str(song_info))
                    song_url = json.dumps(song_info['data'][0]['url'], ensure_ascii=False)
                    print(song_url)
                    cm=[
  {
    "type": "card",
    "theme": "secondary",
    "color": "#DD001B",
    "size": "lg",
    "modules": [
      {
        "type": "header",
        "text": {
          "type": "plain-text",
          "content": "歌名："+str(json.loads(str(item))['name']),
        }
      },
      {
        "type": "context",
        "elements": [
          {
            "type": "kmarkdown",
            "content": "歌手： ["+str(json.loads(str(item))['ar'][0]['name'])+"](https://music.163.com/#/artist?id="+str(json.loads(str(item))['ar'][0]['id'])+")  —出自专辑 ["+str(json.loads(str(item))['al']['name'])+"](https://music.163.com/#/album?id="+str(json.loads(str(item))['al']['id'])+")"
          }
        ]
      },
      {
        "type": "audio",
        "title": str(json.loads(str(item))['name']),
        "src": eval(song_url),
        "cover": str(json.loads(str(item))['al']['picUrl'])
      },
      {
        "type": "divider"
      },
      {
        "type": "context",
        "elements": [
          {
            "type": "image",
            "src": "https://img.kaiheila.cn/assets/2022-05/UmCnhm4mlt016016.png"
          },
          {
            "type": "kmarkdown",
            "content": "网易云音乐  [在网页查看](https://music.163.com/#/song?id="+str(json.loads(str(item))['id'])+")"
          }
        ]
      }
    ]
  }
]

                    print(cm)
                    await msg.ctx.channel.send(cm)
                    break

            else:
                await msg.ctx.channel.send("该首歌曲解析失败，可能是因为歌曲格式问题")
    else:
        await msg.ctx.channel.send("很抱歉，未能搜索到相关歌曲信息")




@bot.command(name='点歌')
async def listen(msg: Message, *args):
    song_name=""
    for st in args:
        song_name=song_name+st+" "
    global p
    global playtime
    global starttime
    subprocess.Popen("kill %d"%int(p.pid)+1 ,shell=True)
    print(song_name)
    await msg.ctx.channel.send("即将播放请稍等")
    d = {"hlpretag": "<span class=\"s-fc7\">", "hlposttag": "</span>", "s": song_name, "type": "1", "offset": "0",
         "total": "true", "limit": "30", "csrf_token": ""}
    d = json.dumps(d)
    random_param = get_random()
    param = get_final_param(d, random_param)
    song_list = get_music_list(param['params'], param['encSecKey'])
    print(song_list)
    if len(str(json.loads(song_list))) >0:
        if json.loads(song_list)['result']['songCount'] > 0:
            song_list = json.loads(song_list)['result']['songs']
            for i, item in enumerate(song_list):
                item = json.dumps(item)
                print(str(i) + "：" + str(json.loads(str(item))['name']))
                d = {"ids": "[" + str(json.loads(str(item))['id']) + "]", "level": "standard", "encodeType": "",
                 "csrf_token": ""}
                d = json.dumps(d)
                param = get_final_param(d, random_param)
                song_info = get_reply(param['params'], param['encSecKey'])
                if len(song_info) > 0:

                    song_info = json.loads(song_info)
                    if song_info['data'][0]['code']==-110:
                        continue
                    else:
                        print(str(song_info))
                        song_url = json.dumps(song_info['data'][0]['url'], ensure_ascii=False)
                        print(song_url)
                        musicfile=requests.get(eval(song_url))
                        open("tmp.mp3","wb").write(musicfile.content)
                        starttime=time.time()
                        playtime=0
                        p = subprocess.Popen('ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:1234',shell=True)
                        break

                else:
                    await msg.ctx.channel.send("该首歌曲解析失败，可能是因为歌曲格式问题")
        else:
            await msg.ctx.channel.send("很抱歉，未能搜索到相关歌曲信息")
    else:
        await msg.ctx.channel.send("ERROR 稍后重试")




@bot.command(name='暂停播放')
async def paus(msg: Message):
    #f=open("tmp.mp3","wb")
    #f.truncate();
    global p
    print(p)
    global pausetime
    subprocess.Popen("kill %d"%int(p.pid)+1 ,shell=True) #通过pid来杀进程，在window上有效
    pausetime=time.time()
    #subprocess.Popen("khl-voice --token 1/MTExNDc=/XskugJgHwEKRz+RLipoqOw== --input tmp.mp3 --channel 7395538237423185")
    await msg.ctx.channel.send("已暂停播放")

@bot.command(name='继续播放')
async def conti(msg: Message):
    #f=open("tmp.mp3","wb")
    #f.truncate();
    global playtime
    global starttime
    global pausetime
    global p
    playtime=playtime+pausetime-starttime
    print(starttime)
    print(pausetime)
    print(playtime)
    s='ffmpeg -re -nostats -ss '+str(playtime)+' -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:1234'
    print(s)
    p = subprocess.Popen(s,shell=True)
    starttime=time.time()
    #subprocess.Popen("khl-voice --token 1/MTExNDc=/XskugJgHwEKRz+RLipoqOw== --input tmp.mp3 --channel 7395538237423185")
    await msg.ctx.channel.send("已开始播放")

@bot.command(name='添加歌曲')
async def addmusic(msg: Message,*args):
    #f=open("tmp.mp3","wb")
    #f.truncate();
    global playlist

    song_name=""
    for st in args:
        song_name=song_name+st+" "
    playlist.append(song_name)

    await msg.ctx.channel.send("已添加成功")
    print(playlist)

@bot.command(name='下一首')
async def nextmusic(msg: Message):
    global playlist
    global listid
    listid=listid+1
    if listid==len(playlist):
        listid=1
    global p
    global playtime
    global starttime
    subprocess.Popen("kill %d"%int(p.pid)+1 ,shell=True)
    song_name=playlist[listid]
    await msg.ctx.channel.send("即将播放: "+song_name)
    d = {"hlpretag": "<span class=\"s-fc7\">", "hlposttag": "</span>", "s": song_name, "type": "1", "offset": "0",
         "total": "true", "limit": "30", "csrf_token": ""}
    d = json.dumps(d)
    random_param = get_random()
    param = get_final_param(d, random_param)
    song_list = get_music_list(param['params'], param['encSecKey'])
    print(song_list)
    if len(str(json.loads(song_list))) >0:
        if json.loads(song_list)['result']['songCount'] > 0:
            song_list = json.loads(song_list)['result']['songs']
            for i, item in enumerate(song_list):
                item = json.dumps(item)
                print(str(i) + "：" + str(json.loads(str(item))['name']))
                d = {"ids": "[" + str(json.loads(str(item))['id']) + "]", "level": "standard", "encodeType": "",
                 "csrf_token": ""}
                d = json.dumps(d)
                param = get_final_param(d, random_param)
                song_info = get_reply(param['params'], param['encSecKey'])
                if len(song_info) > 0:

                    song_info = json.loads(song_info)
                    if song_info['data'][0]['code']==-110:
                        continue
                    else:
                        print(str(song_info))
                        song_url = json.dumps(song_info['data'][0]['url'], ensure_ascii=False)
                        print(song_url)
                        musicfile=requests.get(eval(song_url))
                        open("tmp.mp3","wb").write(musicfile.content)
                        starttime=time.time()
                        playtime=0
                        p = subprocess.Popen('ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:1234',shell=True)
                        break

                else:
                    await msg.ctx.channel.send("该首歌曲解析失败，可能是因为歌曲格式问题")
        else:
            await msg.ctx.channel.send("很抱歉，未能搜索到相关歌曲信息")
    else:
        await msg.ctx.channel.send("ERROR 稍后重试")
        listid=listid-1

@bot.command(name='导入歌单')
async def listen(msg: Message, linkid : str):
    global playlist
    url = "https://music.163.com/playlist/?id="+linkid


    headers = {
        'authority': 'music.163.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'origin': 'https://music.163.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://music.163.com/search/',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    response = requests.request("GET", url, headers=headers)
    pattern = '\<li>\<a href="/song\?id=(.*?)">(.*?)</a></li>'
    matches = re.findall(pattern,response.text)
    print(matches)

    for item in matches:
        playlist.append(item[1])
    await msg.ctx.channel.send("导入完成")

@bot.command(name='复位')
async def reset(msg: Message):
    #f=open("tmp.mp3","wb")
    #f.truncate();
    global playtime
    global starttime
    global pausetime
    global p
    playtime=0
    pausetime=0
    starttime=0
    print(starttime)
    print(pausetime)
    print(playtime)
    subprocess.Popen("kill %d"%int(p.pid)+1 ,shell=True)
    p = subprocess.Popen('echo',shell=True)
    #subprocess.Popen("khl-voice --token 1/MTExNDc=/XskugJgHwEKRz+RLipoqOw== --input tmp.mp3 --channel 7395538237423185")
    await msg.ctx.channel.send("复位完成")
# everything done, go ahead now!
bot.run()
