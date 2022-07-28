import json
import subprocess
import aiohttp
import asyncio
import psutil
import re
from voiceAPI import Voice
from khl import Bot, Event, EventTypes, Message, api
from khl.card import Card, CardMessage, Element, Module, Struct, Types


def get_helpcm(botid):
    helpcm = [{
        "type":
        "card",
        "theme":
        "secondary",
        "size":
        "lg",
        "modules": [{
            "type": "header",
            "text": {
                "type": "plain-text",
                "content": "点歌机操作指南"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**0.  " + botid + "号加入语音**"
            }
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "功能:    让机器人进到你在的语音频道"
            }
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**1.  点歌   +    (平台)    +    歌名    +    (--置顶)**"
            }
        }, {
            "type": "section",
            "text": {
                "type":
                "kmarkdown",
                "content":
                "功能:    将歌曲加到播放队列中\n**[Warning]**:\n歌名中如果有英文引号等特殊字符，需要将歌名用英文引号括起来\n例如  **点歌 \"Rrhar'il\"**\n**[Feature and Tips]**:\n现支持QQ音乐、全民k歌、咪咕音乐、网易云音乐、网易云音乐电台、Youtube、蜻蜓Fm广播电台与B站，若不写平台则默认从网易云获取数据\n**1.**B站支持分P\n**2.**咪咕音乐全会员\n**3.**QQ音乐，全民K歌需要单独安装api并在config.json中启用平台\n**4.**网易云电台仅支持从节目id点播，b站仅支持从BV号与链接点播，全民k歌、蜻蜓Fm广播电台与Youtube仅支持从链接点播\n**5.**在指令最后带上“--置顶”会将歌曲添加到播放队列最前端\n**6.**如果需要指定歌曲版本播放，可以在歌名后添加歌手\n例如  **点歌 勇敢勇敢-黄勇**\n例如  **点歌 qq heavensdoor**\n例如  **点歌 勇敢勇敢-黄勇 --置顶**\n例如  **点歌 网易 勇敢勇敢-黄勇**\n例如  **点歌 b站 BV1qa411e7Fi**\n例如  **点歌 你看到的我**\n例如  **点歌 网易电台 2499131107**\n例如  **点歌 咪咕 青花瓷**\n例如  **点歌 b站 https://www.bilibili.com/video/BV1kT4y1X7UW?p=4**\n例如  **点歌 k歌 https://node.kg.qq.com/play?s=R2M-Y3Rux5IKPRyf**\n例如  **点歌 ytb https://www.youtube.com/watch?v=WMgYcBvw0dk**\n例如  **点歌 fm https://www.qingting.fm/radios/339**"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**2.  导入歌单       +       QQ或网易云的歌单id或链接**"
            }
        }, {
            "type": "section",
            "text": {
                "type":
                "kmarkdown",
                "content":
                "功能:    将网易云或QQ歌单中的歌曲导入到播放队列\n例如  **导入歌单 977171340**\n例如  **导入歌单 8374280842**\n例如  **导入歌单 https://music.163.com/#/playlist?id=977171340**\n例如  **导入歌单 https://y.qq.com/n/ryqq/playlist/8374280842**\n例如  **导入歌单 https://c.y.qq.com/base/fcgi-bin/u?__=Juyj4pTo4rxn**"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**3.  导入电台       +       网易云电台id/链接**"
            }
        }, {
            "type": "section",
            "text": {
                "type":
                "kmarkdown",
                "content":
                "功能:    将网易电台中的歌曲导入到播放队列\n例如  **导入电台 972583481**\n例如  **导入电台 https://music.163.com/#/djradio?id=972583481**"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**4.  导入专辑       +       网易云专辑id/链接**"
            }
        }, {
            "type": "section",
            "text": {
                "type":
                "kmarkdown",
                "content":
                "功能:    将网易云专辑中的歌曲导入到播放队列\n例如  **导入专辑 37578031**\n例如  **导入专辑 https://music.163.com/#/album?id=37578031**"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**5.  搜索       +       歌名**"
            }
        }, {
            "type": "section",
            "text": {
                "type":
                "kmarkdown",
                "content":
                "功能:    从网易云、网易电台、咪咕音乐与qq音乐搜索歌曲（qq平台需单独打开）\n例如  **搜索 海阔天空**"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**6.  重新连接**"
            }
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "功能:    当机器人意外掉出语音后可使用该命令重新连接至语音"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**7.  循环模式**"
            }
        }, {
            "type": "section",
            "text": {
                "type":
                "kmarkdown",
                "content":
                "功能:    切换循环模式，目前支持四种模式:**关闭,单曲循环,列表循环,随机播放**（**推荐使用按钮调用**）"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**8.  下一首**"
            }
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "功能:    跳过当前正播放的歌曲（**推荐使用按钮调用**）"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**9.  清空歌单**"
            }
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "功能:    清空播放队列（**推荐使用按钮调用**）"
            }
        }, {
            "type": "divider"
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "**10.  歌单**"
            }
        }, {
            "type": "section",
            "text": {
                "type": "kmarkdown",
                "content": "功能:    展示播放队列内剩余的歌曲（**播放消息中已自带**）"
            }
        }, {
            "type": "divider"
        }, {
            "type":
            "context",
            "elements": [{
                "type":
                "plain-text",
                "content":
                "如有其他问题、bug或反馈建议，请私信开发人员：\nnick-haoran#0722      Gunale#2333\n特别鸣谢:        k1nbo#0001"
            }]
        }]
    }]
    return helpcm


async def getCidAndTitle(duration, deltatime, guild, bvid, p=1):
    url = 'https://api.bilibili.com/x/web-interface/view?bvid=' + bvid
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            data = (await r.json())['data']
    title = data['title']
    cid = data['pages'][p - 1]['cid']
    duration[guild] = data['pages'][p - 1]['duration'] + deltatime
    mid = str(data['owner']['mid'])
    name = data['owner']['name']
    pic = data['pic']
    print(cid, title, mid)
    return str(cid), title, mid, name, pic


async def getInformation(duration, deltatime, bvid, guild):
    bvid = bvid.replace("?p=", " ")
    item = []
    if len(bvid) == 12:

        cid, title, mid, name, pic = await getCidAndTitle(
            duration, deltatime, guild, bvid[:12], 1)
        item.append(bvid)
    else:
        cid, title, mid, name, pic = await getCidAndTitle(
            duration, deltatime, guild, bvid[:12], int(bvid[13:]))
        item.append(bvid[:12])
    item.append(cid)
    item.append(title)
    item.append(mid)
    item.append(name)
    item.append(pic)

    return guild, item


async def getAudio(guild, item, botid):
    baseUrl = 'http://api.bilibili.com/x/player/playurl?fnval=16&'
    bvid, cid, title, mid, name, pic = item[0], item[1], item[2], item[
        3], item[4], item[5]
    url = baseUrl + 'bvid=' + bvid + '&cid=' + cid
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            audioUrl = (await r.json())['data']['dash']['audio'][0]['baseUrl']
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Range': 'bytes=0-',
        'Referer':
        'https://api.bilibili.com/x/web-interface/view?bvid=' + bvid,
        'Origin': 'https://www.bilibili.com',
        'Connection': 'keep-alive'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=audioUrl,
                               headers=headers,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            with open(guild + "_" + botid + ".mp3", 'wb') as f:
                while True:
                    chunk = await r.content.read()
                    if not chunk:
                        break
                    f.write(chunk)
    return bvid, cid, title, mid, name, pic


def parse_kmd_to_url(link):
    try:
        pattern = r'(?<=\[)(.*?)(?=\])'
        link = re.search(pattern, link).group()
        return link
    except:
        return link


def start_play(guild, port, botid):
    return subprocess.Popen(
        'ffmpeg -re -nostats -i "' + guild + "_" + botid +
        '.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:' +
        port[guild],
        shell=True)


def get_playlist(guild, playlist):
    c = Card()
    c.append(Module.Header('播放队列：'))
    if len(playlist[guild]) == 0:
        c.append(Module.Section('无'))
    i = 0
    for item in playlist[guild]:
        if i == 10:
            break
        c.append(Module.Section(item['display']))
        i += 1
    c.append(Module.Header('共有' + str(len(playlist[guild])) + '首歌'))
    return c


async def delmsg(msg_id, config, botid):
    print(msg_id)
    url = 'https://www.kookapp.cn/api/v3/message/delete'
    data = {"msg_id": str(msg_id)}
    headers = {"Authorization": "Bot " + config['token' + botid]}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,
                                data=data,
                                headers=headers,
                                timeout=aiohttp.ClientTimeout(total=5)) as r:
            print(await r.text())


def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        configstr = f.read().replace('\\', '!')
        configtmp = json.loads(configstr)
        config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
        return config


async def status_active_music(slot, config, botid):
    print("已用槽位:" + slot)
    url = "https://www.kookapp.cn/api/v3/game/activity"
    headers = {'Authorization': "Bot " + config['token' + botid]}
    params = {
        "data_type": 2,
        "software": "qqmusic",
        "singer": "KO-ON",
        "music_name": "已用槽位:" + slot
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=params, headers=headers) as r:
            return json.loads(await r.text())


async def login(botid, qq_enable, netease_phone, netease_passwd, qq_cookie,
                qq_id, voice, config):
    print("id:" + botid)
    print('login check')
    print(await status_active_music(str(len(voice)), config, botid))
    url = 'http://127.0.0.1:3000/login/status?timestamp='
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            response = await r.json()
    print(response)
    try:
        response = response['data']['account']['status']
        if response == -10:
            url = 'http://127.0.0.1:3000/login/cellphone?phone=' + netease_phone + '&password=' + netease_passwd
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    print(await r.text())
            print('网易云登陆成功')
    except:
        url = 'http://127.0.0.1:3000/login/cellphone?phone=' + netease_phone + '&password=' + netease_passwd
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                print(await r.text())
        print('网易云登陆成功')
    print('网易已登录')
    url = 'http://127.0.0.1:3000/login/refresh'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            print(await r.text())
    print('刷新登录cookie')
    if qq_enable == "1":
        url = 'http://127.0.0.1:3300/user/setCookie'
        data = {"data": qq_cookie}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=url, data=data,
                    timeout=aiohttp.ClientTimeout(total=5)) as r:
                print(await r.text())
        url = 'http://127.0.0.1:3300/user/getCookie?id=' + qq_id

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                print(await r.text())
        print('QQ已登录')


async def save_cache(botid, playlist, voicechannelid, msgid, channel):
    with open(botid + 'playlistcache', 'w', encoding='utf-8') as f:
        f.write(str(playlist))
    with open(botid + 'voiceidcache', 'w', encoding='utf-8') as f:
        f.write(str(voicechannelid))
    with open(botid + 'msgidcache', 'w', encoding='utf-8') as f:
        f.write(str(msgid))
    with open(botid + 'channelidcache', 'w', encoding='utf-8') as f:
        f.write(str(channel))


def kill(guild, p):
    try:
        process = psutil.Process(p[guild].pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    except Exception as e:
        print(e)


async def load_cache(botid, singleloops, timeout, LOCK, playtime, duration,
                     port, voice, config, rtcpport, voiceffmpeg, playlist,
                     voicechannelid, msgid, channel, event_loop):
    try:
        print('loading cache')

        with open(botid + 'playlistcache', 'r', encoding='utf-8') as f:
            playlist = eval(f.read())
        with open(botid + 'voiceidcache', 'r', encoding='utf-8') as f:
            voicechannelid = eval(f.read())
        with open(botid + 'msgidcache', 'r', encoding='utf-8') as f:
            msgid = eval(f.read())
        with open(botid + 'channelidcache', 'r', encoding='utf-8') as f:
            channel = eval(f.read())
        for guild, voiceid in voicechannelid.items():
            print(voiceid)
            singleloops[guild] = 0
            timeout[guild] = 0
            LOCK[guild] = False
            playtime[guild] = 0
            duration[guild] = 0
            port[guild] = rtcpport
            voice[guild] = Voice(config['token' + botid])
            asyncio.ensure_future(start(voice[guild], voiceid, guild,
                                        voiceffmpeg, port),
                                  loop=event_loop)
            await asyncio.sleep(0.3)

    except:
        print('load cache fail')


async def start(voice, voiceid, guild, voiceffmpeg, port):
    await asyncio.wait([
        voice_Engine(voice, voiceid, guild, voiceffmpeg, port),
        voice.handler()
    ])


async def voice_Engine(voice, voiceid: str, guild, voiceffmpeg, port):
    print(voiceid)
    rtp_url = ''
    voice.channel_id = voiceid
    while True:
        if len(voice.rtp_url) != 0:
            rtp_url = voice.rtp_url
            comm = "ffmpeg -re -loglevel level+info -nostats -stream_loop -1 -i zmq:tcp://127.0.0.1:" + port[
                guild] + " -map 0:a:0 -acodec libopus -ab 128k -filter:a volume=0.15 -ac 2 -ar 48000 -f tee [select=a:f=rtp:ssrc=1357:payload_type=100]" + rtp_url
            print(comm)
            voiceffmpeg[guild] = subprocess.Popen(comm, shell=True)
            break
        await asyncio.sleep(0.1)


async def disconnect(guild, voice, timeout, voiceffmpeg, LOCK, msgid,
                     voicechannelid, channel, singleloops, playtime, duration,
                     port, config, botid):
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
    print(await status_active_music(str(len(voice)), config, botid))
    print(str(guild) + " disconnected")