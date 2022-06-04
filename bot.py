import json
import os
import signal
from khl import Message, Bot
from khl.card import CardMessage, Card, Module
import subprocess
import random
import base64
import binascii
import string
from urllib import parse
import requests
from Cryptodome.Cipher import AES
import re
import eyed3

LOCK = False
playtime = 0
duration = 0
p = {}
cookie = "_ntes_nnid=8ff9c3f22e64b3dbb847b71650371a61,1647935810581; _ntes_nuid=8ff9c3f22e64b3dbb847b71650371a61; NMTID=00OrOyfNUVuawDZoEZsnO6d58RRT0EAAAF_sKDmSw; WEVNSM=1.0.0; WNMCID=orzlno.1647935810851.01.0; WM_TID=AOWQjWwClPNFFUQUAQZuq54BjRS8wIPQ; lang=zh; _iuqxldmzr_=32; ntes_kaola_ad=1; __remember_me=true; MUSIC_U=6c5a3400f94b182eafbdf3ac438bfe4f11b09b8614cc41cce63af743c922f06fd1f884fb69b702f873523d0e5593273ae5cf297c1e51399c235d3316c5d2f10cee0ec6f4ed39863ca0d2166338885bd7; __csrf=f807bc54ad3c2d6833514a58e4c3aa34; WM_NI=CKXjKBtGq7FBVHKZcvUCgFoVLJWJgJviKCpTqFT9gPsP%2FpO9NrJ2rmA6P%2BmklMLq%2BDMQSefW8lZ0xtn9iWXmD82WvuR9vi7iu0YYBypgD%2FLxj%2FUHCFtmK1cW%2BGTcG1z%2BSkg%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb7c77092b38689d074f29a8ea3c84a828b9b86c85bacb586a7eb7489ece18fef2af0fea7c3b92a8195988bca4ab899bfd8c54a969885bbe27e979da9a7ee5e909699abe642b6b785a4f360b39a9cdae65cb190e191ce338eae86d3f16783eaa0ccf061b0938492aa508f8f9d86e55dfcb496d1fb80aee7a7b8db6788e8feb8f57f92e7ba8ab663b7f097bac173b4b98cd0cf74aaf19ba9c24eb8b385d2e25de9999c84c63bbaf59d8ce637e2a3; JSESSIONID-WYYY=VvhIWG%2FjjAadI8hnjXusdZABMHY%2B5jsPhwTXoBRPXihNAGPn6U1s39yFvgfI8KdCdxf8JBj9Kd5302gag%5CfqHxIMvw7lWdEhahEYeQ%5C%5CrAb8w1%5Cp0ZgK0ZEssTm%5CKVRtNH7%2BaH%5CVbzIxV%2B%2Bb%2B9e3dfFUn4%5Cu9wm8HlNsWrS7N5YQ%2FhU1%3A1654179341983"


def kill():
    global p
    try:
        p.kill()
        p.wait()
        p.terminate()
        os.killgp(os.getpgid(pid + 1), signal.SIGTERM)
    except:
        pass


def get_duration_mp3(file_path):
    mp3Info = eyed3.load(file_path)
    return mp3Info.info.time_secs


with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
pid = 0

bot = Bot(token=config["token"])

playlist=[]


# 从a-z,A-Z,0-9中随机获取16位字符
def get_random():
    random_str = "".join(random.sample(string.ascii_letters + string.digits, 16))
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
    iv = b"0102030405060708"
    text = len_change(text)
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(text)
    encrypt = base64.b64encode(encrypted).decode()
    return encrypt


# js中的 b 函数，调用两次 AES 加密
# text 为需要加密的文本， str 为生成的16位随机数
def b(text, str):
    first_data = aes(text, "0CoJUm6Qyw8W8jud")
    second_data = aes(first_data, str)
    return second_data


# 这就是那个巨坑的 c 函数
def c(text):
    e = "010001"
    f = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    text = text[::-1]
    result = pow(int(binascii.hexlify(text.encode()), 16), int(e, 16), int(f, 16))
    return format(result, "x").zfill(131)


# 获取最终的参数 params 和 encSecKey 的方法
def get_final_param(text, str):
    params = b(text, str)
    encSecKey = c(str)
    return {"params": params, "encSecKey": encSecKey}


# 通过参数获取搜索歌曲的列表
def get_music_list(params, encSecKey):
    url = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token="
    payload = "params=" + parse.quote(params) + "&encSecKey=" + parse.quote(encSecKey)
    headers = {
            "authority": "music.163.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded",
            "accept": "*/*",
            "origin": "https://music.163.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://music.163.com/search/",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": cookie,
            }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


# 通过歌曲的id获取播放链接
def get_reply(params, encSecKey):
    url = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token="
    payload = "params=" + parse.quote(params) + "&encSecKey=" + parse.quote(encSecKey)
    headers = {
            "authority": "music.163.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded",
            "accept": "*/*",
            "origin": "https://music.163.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://music.163.com/",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": cookie,
            }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


@bot.command(name="下一首")
async def nextmusic(msg: Message):
    global playlist
    global playtime
    global LOCK
    flag=True
    for role in msg.author.roles:
        if role == config["skiper"]:
            flag=False
    if flag:
        await msg.ctx.channel.send("无权限")
        return
    playlist.pop(0)
    playtime=0
    LOCK=False
    await msg.ctx.channel.send("切换成功")


@bot.command(name="点歌")
async def addmusic(msg: Message, *args):
    if msg.ctx.channel.id != config["channel"]:
        await msg.ctx.channel.send('请在指定频道中点歌')
        return
    global playlist
    song_name = ""
    for st in args:
        song_name = song_name + st + " "
    playlist.append({'name':song_name,'userid':msg.author.id})
    await msg.ctx.channel.send("已添加")


# @bot.command(name='导入歌单')
async def listen(msg: Message, linkid: str):
    global playlist
    url = "https://music.163.com/playlist/?id=" + linkid
    headers = {
            "authority": "music.163.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded",
            "accept": "*/*",
            "origin": "https://music.163.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://music.163.com/search/",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": cookie,
            }
    response = requests.request("GET", url, headers=headers)
    pattern = '\<li>\<a href="/song\?id=(.*?)">(.*?)</a></li>'
    matches = re.findall(pattern, response.text)
    # print(matches)
    for item in matches:
        playlist.append(item[1])
    await msg.ctx.channel.send("导入完成")


@bot.command(name="歌单")
async def prtlist(msg: Message):
    global playlist
    cm = CardMessage()
    c = Card()
    c.append(Module.Header('正在播放：'))
    for item in playlist:
        c.append(Module.Section(item['name']))
    cm.append(c)
    await msg.ctx.channel.send(cm)


@bot.task.add_interval(seconds=5)
async def update_played_time_and_change_music():
    global playtime
    global playlist
    global LOCK
    global duration
    if LOCK:
        return None
    else:
        LOCK = True
        if len(playlist) == 0:
            LOCK = False
            return None
        else:
            if playtime == 0:
                kill()
                song_name = playlist[0]['name']
                if song_name == "":
                    LOCK = False
                    return
                d = {
                        "hlpretag": '<span class="s-fc7">',
                        "hlposttag": "</span>",
                        "s": song_name,
                        "type": "1",
                        "offset": "0",
                        "total": "true",
                        "limit": "30",
                        "csrf_token": "",
                        }
                d = json.dumps(d)
                random_param = get_random()
                param = get_final_param(d, random_param)
                song_list = get_music_list(param["params"], param["encSecKey"])
                try:
                    json.loads(song_list)
                except:
                    LOCK = False
                    return
                if len(str(json.loads(song_list))) > 0:
                    if json.loads(song_list)["result"]["songCount"] > 0:
                        song_list = json.loads(song_list)["result"]["songs"]
                        for i,item in enumerate(song_list):
                            item = json.dumps(item)
                            d = {
                                    "ids": "[" + str(json.loads(str(item))["id"]) + "]",
                                    "level": "standard",
                                    "encodeType": "",
                                    "csrf_token": "",
                                    }
                            d = json.dumps(d)
                            param = get_final_param(d, random_param)
                            song_info = get_reply(param["params"], param["encSecKey"])
                            if len(song_info) > 0:
                                song_info = json.loads(song_info)
                                if song_info["data"][0]["code"] == -110:
                                    continue
                                else:
                                    song_url = json.dumps(
                                            song_info["data"][0]["url"], ensure_ascii=False
                                            )
                                    print(song_url)
                                    musicfile = requests.get(eval(song_url))
                                    open("tmp.mp3", "wb").write(musicfile.content)
                                    playtime = 0
                                    duration = get_duration_mp3("tmp.mp3")
                                    p = subprocess.Popen(
                                            'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:1234',
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            )
                                    cm = [ { "type": "card", "theme": "secondary", "color": "#DD001B", "size": "lg", "modules": [ { "type": "header", "text": { "type": "plain-text", "content": "正在播放：" + str( json.loads(str(item))[ "name" ]), }, }, { "type": "section", "text": { "type": "kmarkdown", "content":"(met)" +playlist[0]['userid']+"(met)", }, }, { "type": "context", "elements": [ { "type": "kmarkdown", "content": "歌手： [" + str( json.loads(str(item))[ "ar" ][0]["name"]) + "](https://music.163.com/#/artist?id=" + str( json.loads(str(item))[ "ar" ][0]["id"]) + ")  —出自专辑 [" + str( json.loads(str(item))[ "al" ]["name"]) + "](https://music.163.com/#/album?id=" + str( json.loads(str(item))[ "al" ]["id"]) + ")", } ], }, { "type": "audio", "title": str( json.loads(str(item))["name"]), "src": eval(song_url), "cover": str( json.loads(str(item))["al"][ "picUrl" ]), }, {"type": "divider"}, { "type": "context", "elements": [ { "type": "image", "src": "https://img.kaiheila.cn/assets/2022-05/UmCnhm4mlt016016.png", }, { "type": "kmarkdown", "content": "网易云音乐  [在网页查看](https://music.163.com/#/song?id=" + str( json.loads(str(item))[ "id" ]) + ")", }, ], }, ], } ]
                                    await bot.send(
                                            await bot.fetch_public_channel(
                                                config["channel"]
                                                ),
                                            cm,
                                            )
                                    break
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


bot.command.update_prefixes("", "/")
bot.run()
