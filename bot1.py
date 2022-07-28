import asyncio
import concurrent.futures
import os
import random
import re
import signal
import time
import aiohttp
import nest_asyncio
import psutil
from khl import Bot, Event, EventTypes, Message, api
from khl.card import Card, CardMessage, Element, Module, Struct, Types
from music_manage import bili, fm, kmusic, migu, netease, neteaseradio, qqmusic, ytb

from status_manage import (delmsg, kill, load_cache, load_config, login,
                           save_cache, status_active_music, disconnect, start,
                           get_playlist, parse_kmd_to_url, get_helpcm)
from voiceAPI import Voice

eventloop = asyncio.new_event_loop()
asyncio.set_event_loop(eventloop)
executor = concurrent.futures.ThreadPoolExecutor()
try:
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    print("platform:linux")
except:
    print("platform:windows")
nest_asyncio.apply()
botid = os.path.basename(__file__).split(".")[0].replace('bot', '')
config = load_config()
rtcpport = botid + '234'
firstlogin = True
load = True
JOINLOCK = False
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
bot = Bot(token=config['token' + botid])
playlist = {}  #guild list
port = {}  #guild port
p = {}  #guild process
deltatime = 7
singleloops = {}


@bot.command(name='导入歌单')
async def import_playlist(msg: Message, linkid: str):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid = voiceid[0].id
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
            linkid = parse_kmd_to_url(linkid)
            headers = {
                'accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding':
                'gzip, deflate, br',
                'accept-language':
                'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'cookie':
                qq_cookie,
                'sec-ch-ua':
                '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
                'sec-ch-ua-mobile':
                '?0',
                'sec-ch-ua-platform':
                "Windows",
                'sec-fetch-dest':
                'document',
                'sec-fetch-mode':
                'navigate',
                'sec-fetch-site':
                'none',
                'sec-fetch-user':
                '?1',
                'upgrade-insecure-requests':
                '1',
                'user-agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=linkid,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    linkid = await r.text()
        pattern = r'(?<=[^user]id=)[0-9]+|(?<=playlist/)[0-9]+'
        linkid = re.search(pattern, linkid).group()
    except Exception as e:
        print(e)
    print(linkid)
    headers = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control':
        'max-age=0',
        'Connection':
        'keep-alive',
        'Cookie':
        netease_cookie,
        'Host':
        '127.0.0.1:3000',
        'Referer':
        'https://music.163.com',
        'If-None-Match':
        'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
        'sec-ch-ua':
        '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile':
        '?0',
        'sec-ch-ua-platform':
        "Windows",
        'Sec-Fetch-Dest':
        'document',
        'Sec-Fetch-Mode':
        'navigate',
        'Sec-Fetch-Site':
        'none',
        'Sec-Fetch-User':
        '?1',
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
    }
    try:

        offset = 0
        while True:
            url = "http://127.0.0.1:3000/playlist/track/all?id=" + linkid + '&limit=1000&offset=' + str(
                offset * 1000)
            offset += 1
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    resp_json = await r.json()
                    print
                    songs = resp_json.get("songs", [])
                    if len(songs) == 0:
                        break
                    for song in songs:
                        playlist[msg.ctx.guild.id].append({
                            'name':
                            song.get('name', '') + "-" +
                            song.get('ar', [])[0].get('name', '') + '-' +
                            str(song.get('id')),
                            'userid':
                            msg.author.id,
                            'type':
                            '网易',
                            'time':
                            int(round(time.time() * 1000)) + 1000000000000
                        })
    except:
        pass
    try:
        url = "http://127.0.0.1:3300/songlist?id=" + linkid
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                resp_json = await r.json()
                songs = resp_json.get("data", {}).get("songlist", [])
                for song in songs:
                    playlist[msg.ctx.guild.id].append({
                        'name':
                        song.get('songname', '') + "-" +
                        song.get('singer', [])[0].get('name', '') + '-' +
                        str(song.get('songmid')),
                        'userid':
                        msg.author.id,
                        'type':
                        'qq',
                        'time':
                        int(round(time.time() * 1000)) + 1000000000000
                    })
    except:
        pass
    await msg.ctx.channel.send("导入完成")


@bot.command(name='导入专辑')
async def import_netease_album(msg: Message, linkid: str):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid = voiceid[0].id
        if voiceid != voicechannelid[msg.ctx.guild.id]:
            await msg.ctx.channel.send("请先进入听歌频道或退出重进")
            return
    except:
        await msg.ctx.channel.send("请先进入听歌频道或退出重进")
        return
    global netease_cookie
    try:
        pattern = r'(?<=[^user]id=)[0-9]+'
        linkid = re.search(pattern, linkid).group()
    except:
        pass
    headers = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control':
        'max-age=0',
        'Connection':
        'keep-alive',
        'Cookie':
        netease_cookie,
        'Host':
        '127.0.0.1:3000',
        'Referer':
        'https://music.163.com',
        'If-None-Match':
        'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
        'sec-ch-ua':
        '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile':
        '?0',
        'sec-ch-ua-platform':
        "Windows",
        'Sec-Fetch-Dest':
        'document',
        'Sec-Fetch-Mode':
        'navigate',
        'Sec-Fetch-Site':
        'none',
        'Sec-Fetch-User':
        '?1',
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
    }
    try:
        global playlist

        url = "http://127.0.0.1:3000/album?id=" + linkid

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)) as r:
                resp_json = await r.json()
                songs = resp_json.get("songs", [])

                for song in songs:
                    playlist[msg.ctx.guild.id].append({
                        'name':
                        song.get('name', '') + "-" +
                        song.get('ar', [])[0].get('name', '') + '-' +
                        str(song.get('id')),
                        'userid':
                        msg.author.id,
                        'type':
                        '网易',
                        'time':
                        int(round(time.time() * 1000)) + 1000000000000
                    })
        await msg.ctx.channel.send("导入完成")
    except:
        pass


@bot.command(name='导入电台')
async def import_netease_radio(msg: Message, linkid: str):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid = voiceid[0].id
        if voiceid != voicechannelid[msg.ctx.guild.id]:
            await msg.ctx.channel.send("请先进入听歌频道或退出重进")
            return
    except:
        await msg.ctx.channel.send("请先进入听歌频道或退出重进")
        return
    global netease_cookie
    try:
        pattern = r'(?<=[^user]id=)[0-9]+'
        linkid = re.search(pattern, linkid).group()
    except:
        pass
    headers = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control':
        'max-age=0',
        'Connection':
        'keep-alive',
        'Cookie':
        netease_cookie,
        'Host':
        '127.0.0.1:3000',
        'Referer':
        'https://music.163.com',
        'If-None-Match':
        'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
        'sec-ch-ua':
        '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile':
        '?0',
        'sec-ch-ua-platform':
        "Windows",
        'Sec-Fetch-Dest':
        'document',
        'Sec-Fetch-Mode':
        'navigate',
        'Sec-Fetch-Site':
        'none',
        'Sec-Fetch-User':
        '?1',
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
    }
    try:
        global playlist
        offset = 0
        while True:
            url = "http://127.0.0.1:3000/dj/program?rid=" + linkid + "&limit=1000&offset=" + str(
                offset * 1000)
            offset += 1
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    resp_json = await r.json()
                    programs = resp_json.get("programs", [])
                    if len(programs) == 0:
                        break
                    for program in programs:
                        playlist[msg.ctx.guild.id].append({
                            'name':
                            program.get('mainSong', {}).get('name', '') + '-' +
                            str(program.get('id')),
                            'userid':
                            msg.author.id,
                            'type':
                            '网易电台',
                            'time':
                            int(round(time.time() * 1000)) + 1000000000000
                        })
        await msg.ctx.channel.send("导入完成")
    except:
        pass


@bot.command(name=botid + '号加入语音')
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
    JOINLOCK = True
    if len(voice) >= 2 and channel.get(msg.ctx.guild.id, -1) == -1:
        await msg.ctx.channel.send(
            "播放槽位已满,请加入交流服务器获取备用机 https://kook.top/vyAPVw")
        JOINLOCK = False
        return
    voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid = voiceid[0].id
    except:
        await msg.ctx.channel.send("请先进入一个语音频道或退出重进")
        JOINLOCK = False
        return
    print(voiceid)
    singleloops[msg.ctx.guild.id] = 0
    timeout[msg.ctx.guild.id] = 0
    LOCK[msg.ctx.guild.id] = False
    playlist[msg.ctx.guild.id] = []
    voicechannelid[msg.ctx.guild.id] = voiceid
    channel[msg.ctx.guild.id] = msg.ctx.channel.id
    playtime[msg.ctx.guild.id] = 0
    msgid[msg.ctx.guild.id] = "0"
    duration[msg.ctx.guild.id] = 0
    port[msg.ctx.guild.id] = rtcpport
    await msg.ctx.channel.send("已加入频道")
    voice[msg.ctx.guild.id] = Voice(config['token' + botid])
    event_loop = asyncio.get_event_loop()

    asyncio.ensure_future(start(voice[msg.ctx.guild.id], voiceid,
                                msg.ctx.guild.id, voiceffmpeg, port),
                          loop=event_loop)
    rtcpport = str(int(rtcpport) + 1)
    print(await status_active_music(str(len(voice)), config, botid))
    JOINLOCK = False


@bot.command(name='绑定点歌频道')
async def bind_text_channel(msg: Message):
    global channel
    await msg.ctx.channel.send("绑定频道")
    channel[msg.ctx.guild.id] = msg.ctx.channel.id


@bot.command(name='清空歌单')
async def clear_playlist(msg: Message):
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    try:
        while LOCK[msg.ctx.guild.id]:
            await asyncio.sleep(0.1)
        LOCK[msg.ctx.guild.id] = True
        global playlist
        if len(playlist[msg.ctx.guild.id]) > 0:
            now = playlist[msg.ctx.guild.id][0]
            playlist[msg.ctx.guild.id] = []
            playlist[msg.ctx.guild.id].append(now)
        await msg.ctx.channel.send("清空完成")
        LOCK[msg.ctx.guild.id] = False
    except:
        LOCK[msg.ctx.guild.id] = False


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
        while LOCK[msg.ctx.guild.id]:
            await asyncio.sleep(0.1)
        LOCK[msg.ctx.guild.id] = True
        kill(msg.ctx.guild.id, p)
        if len(playlist[msg.ctx.guild.id]) == 0:
            await msg.ctx.channel.send("无下一首")
            LOCK[msg.ctx.guild.id] = False
            return None
        if singleloops[msg.ctx.guild.id] == 2:
            playlist[msg.ctx.guild.id].append(
                playlist[msg.ctx.guild.id].pop(0))
        else:
            playlist[msg.ctx.guild.id].pop(0)
        LOCK[msg.ctx.guild.id] = False
        playtime[msg.ctx.guild.id] = 0
        duration[msg.ctx.guild.id] = 0
        await msg.ctx.channel.send("切换成功")
    except:
        LOCK[msg.ctx.guild.id] = False


@bot.command(name="点歌")
async def addmusic(msg: Message, *args):
    global qq_enable
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid = voiceid[0].id
        if voiceid != voicechannelid[msg.ctx.guild.id]:
            await msg.ctx.channel.send("请先进入听歌频道或退出重进")
            return
    except:
        await msg.ctx.channel.send("请先进入听歌频道或退出重进")
        return
    try:
        args = list(args)
        global playlist
        typ = '网易'
        song_name = ''
        coefficient = 1
        platform = {
            '网易', 'netease', 'Netease', '网易云', '网易云音乐', '网易音乐', 'qq', 'qq音乐',
            'QQ', 'QQ音乐', '网易电台', '电台', '咪咕', '咪咕音乐', 'bili', 'b站', 'bilibili',
            'Bili', 'Bilibili', 'B站', 'k歌', 'K歌', '全民k歌', '全民K歌', 'ytb', 'YTB',
            'youtube', 'Youtube', '油管', 'FM', 'fm', 'Fm'
        }
        if args[0] in platform:
            typ = args[0]
            args.pop(0)
            if typ in {'qq', 'qq音乐', 'QQ', 'QQ音乐', 'k歌', 'K歌', '全民k歌', '全民K歌'
                       } and qq_enable == '0':
                await msg.ctx.channel.send('未启用QQ音乐与全民k歌点歌')
                return None
        if args[-1] in {"--置顶", "-置顶", "--top", "-top", "/置顶", "/top"}:
            args.pop()
            coefficient = -1
        for st in args:
            song_name = song_name + st + " "
        playlist[msg.ctx.guild.id].append({
            'name':
            song_name,
            'userid':
            msg.author.id,
            'type':
            typ,
            'time':
            int(round(time.time() * 1000)) * coefficient,
            'display':
            song_name
        })
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
        config = load_config()
        netease_phone = config["n_phone"]
        netease_passwd = config["n_passwd"]
        netease_cookie = config["n_cookie"]
        qq_cookie = config["q_cookie"]
        qq_id = config["q_id"]
        qq_enable = config["qq_enable"]
        firstlogin = True
        await msg.ctx.channel.send("reload成功")
    except:
        await msg.ctx.channel.send("reload失败")


@bot.command(name="REBOOT" + str(botid))
async def reboot(msg: Message):
    os._exit(0)


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
        c = get_playlist(msg.ctx.guild.id, playlist)
        cm.append(c)
        await msg.ctx.channel.send(cm)
    except:
        pass


@bot.command(name="帮助")
async def help(msg: Message):
    await msg.ctx.channel.send(get_helpcm(botid))


@bot.command(name="状态")
async def status(msg: Message):
    await msg.ctx.channel.send("已用槽位:" + str(len(voice)))


@bot.command(name="循环模式")
async def singlesongloop(msg: Message):
    global singleloops
    try:
        if msg.ctx.channel.id != channel[msg.ctx.guild.id]:
            return
    except:
        return
    try:
        if singleloops[msg.ctx.guild.id] == 0:
            singleloops[msg.ctx.guild.id] = 1
            await msg.ctx.channel.send('循环模式已调整为:单曲循环')
        elif singleloops[msg.ctx.guild.id] == 1:
            singleloops[msg.ctx.guild.id] = 2
            await msg.ctx.channel.send('循环模式已调整为:列表循环')
        elif singleloops[msg.ctx.guild.id] == 2:
            singleloops[msg.ctx.guild.id] = 3
            await msg.ctx.channel.send('循环模式已调整为:随机播放')
        else:
            singleloops[msg.ctx.guild.id] = 0
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
    voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
    try:
        voiceid = voiceid[0].id
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
        voicechannelid[msg.ctx.guild.id] = voiceid
        del voiceffmpeg[msg.ctx.guild.id]
        await msg.ctx.channel.send("已加入频道")
        voice[msg.ctx.guild.id] = Voice(config['token' + botid])
        event_loop = asyncio.get_event_loop()
        asyncio.ensure_future(start(botid, singleloops, timeout, LOCK,
                                    playtime, duration, port, voice, config,
                                    rtcpport, voiceffmpeg),
                              loop=event_loop)
        rtcpport = str(int(rtcpport) + 1)
    except Exception as e:
        print(e)


@bot.command(name="搜索")
async def search(msg: Message, *args):
    global netease_cookie
    global botid
    if botid != "1":
        return
    headers = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control':
        'max-age=0',
        'Connection':
        'keep-alive',
        'Cookie':
        netease_cookie,
        'Host':
        '127.0.0.1:3000',
        'Referer':
        'https://music.163.com',
        'If-None-Match':
        'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
        'sec-ch-ua':
        '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile':
        '?0',
        'sec-ch-ua-platform':
        "Windows",
        'Sec-Fetch-Dest':
        'document',
        'Sec-Fetch-Mode':
        'navigate',
        'Sec-Fetch-Site':
        'none',
        'Sec-Fetch-User':
        '?1',
        'Upgrade-Insecure-Requests':
        '1',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
    }
    song_name = ''
    for st in args:
        song_name = song_name + st + " "
    url = "http://127.0.0.1:3000/search?keywords=" + song_name + "&limit=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               headers=headers,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            songs = (await r.json())['result']['songs']
    text = '网易云结果:\n'
    try:
        for song in songs:
            text += song['name'] + '-' + song['artists'][0][
                'name'] + '-' + song['album']['name'] + '-' + str(
                    song['id']) + '\n'
    except:
        text += '无\n'

    if qq_enable == '1':
        text += 'QQ结果:\n'
        url = "http://127.0.0.1:3300/search/quick?key=" + song_name
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                songs = (await r.json())['data']['song']['itemlist']
        try:
            for song in songs:
                text += song['name'] + '-' + song['singer'] + '\n'
        except:
            text += '无\n'

    text += '网易电台结果:\n'
    url = "http://127.0.0.1:3000/search?keywords=" + song_name + "&limit=5&type=2000"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            songs = (await r.json())['data']['resources']
    try:
        for song in songs:
            text += song['baseInfo']['mainSong']['name'] + '-' + song[
                'baseInfo']['mainSong']['artists'][0]['name'] + '-' + song[
                    'resourceId'] + '\n'
    except:
        text += '无\n'

    text += '咪咕结果:\n'
    url = "http://127.0.0.1:3400/search?keyword=" + song_name
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            songs = (await r.json())['data']['list']
    try:
        i = 0
        for song in songs:
            i += 1
            text += song['name'] + '-' + song['artists'][0][
                'name'] + '-' + song['album']['name'] + '-' + song['cid'] + '\n'
            if i == 5:
                break
    except:
        text += '无\n'
    await msg.ctx.channel.send(text)


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
    global netease_cookie
    global timeout
    global voice
    global LOCK
    global singleloops
    global load
    print("STEP1")
    if firstlogin == True:
        firstlogin = False
        await login(botid, qq_enable, netease_phone, netease_passwd, qq_cookie,
                    qq_id, voice, config)
    if load == True:
        load = False
        event_loop = asyncio.get_event_loop()
        await load_cache(botid, singleloops, timeout, LOCK, playtime, duration,
                         port, voice, config, rtcpport, voiceffmpeg, playlist,
                         voicechannelid, msgid, channel, event_loop)
    print("STEP2")

    deletelist = []
    savetag = False
    for guild, songlist in playlist.items():
        if LOCK[guild]:
            print("LOCK")
            continue
        LOCK[guild] = True
        if channel.get(guild, -1) == -1 or timeout.get(
                guild, -1) == -1 or voiceffmpeg.get(guild, -1) == -1:
            LOCK[guild] = False
            continue
        if len(playlist[guild]) == 0:
            print("timeout +7")
            LOCK[guild] = False
            timeout[guild] += deltatime
            if timeout[guild] > 60:
                print("timeout auto leave")
                await delmsg(msgid[guild], config, botid)
                await disconnect(guild, voice, timeout, voiceffmpeg, LOCK,
                                 msgid, voicechannelid, channel, singleloops,
                                 playtime, duration, port, config, botid)
                deletelist.append(guild)
            continue
        else:
            timeout[guild] = 0
            if playtime[guild] == 0:
                print("playing process start")
                savetag = True
                if singleloops[guild] == 3:
                    random.shuffle(playlist[guild])
                if singleloops[guild] in {0,1}:
                    playlist[guild].sort(key=lambda x: list(x.values())[3])
                song_name = playlist[guild][0]['name']
                if song_name == "":
                    LOCK[guild] = False
                    continue
                event_loop = asyncio.get_event_loop()
                if playlist[guild][0]['type'] in {
                        '网易', 'netease', 'Netease', '网易云', '网易云音乐', '网易音乐'
                }:
                    LOCK[guild] = False
                    asyncio.ensure_future(netease(guild, song_name, LOCK,
                                                  netease_cookie, playlist,
                                                  duration, deltatime, bot,
                                                  config, playtime, p, botid,
                                                  port, msgid, channel),
                                          loop=event_loop)
                elif playlist[guild][0]['type'] in {
                        'bili', 'b站', 'bilibili', 'Bili', 'Bilibili', 'B站'
                }:
                    LOCK[guild] = False
                    asyncio.ensure_future(bili(guild, song_name, LOCK,
                                               playlist, duration, deltatime,
                                               bot, config, playtime, p, botid,
                                               port, msgid, channel),
                                          loop=event_loop)
                elif playlist[guild][0]['type'] in {'网易电台', '电台'}:
                    LOCK[guild] = False
                    asyncio.ensure_future(neteaseradio(guild, song_name, LOCK,
                                                       netease_cookie,
                                                       playlist, duration,
                                                       deltatime, bot, config,
                                                       playtime, p, botid,
                                                       port, msgid, channel),
                                          loop=event_loop)
                elif playlist[guild][0]['type'] in {
                        'qq', 'qq音乐', 'QQ', 'QQ音乐'
                }:
                    LOCK[guild] = False
                    asyncio.ensure_future(qqmusic(guild, song_name, LOCK,
                                                  playlist, duration,
                                                  deltatime, bot, config,
                                                  playtime, p, botid, port,
                                                  msgid, channel),
                                          loop=event_loop)
                elif playlist[guild][0]['type'] in {
                        'k歌', 'K歌', '全民k歌', '全民K歌'
                }:
                    LOCK[guild] = False
                    asyncio.ensure_future(kmusic(guild, song_name, LOCK,
                                                 playlist, duration, deltatime,
                                                 bot, config, playtime, p,
                                                 botid, port, msgid, channel),
                                          loop=event_loop)
                elif playlist[guild][0]['type'] in {
                        'ytb', 'YTB', 'youtube', 'Youtube', '油管'
                }:
                    LOCK[guild] = False
                    asyncio.ensure_future(ytb(guild, song_name, LOCK, playlist,
                                              duration, deltatime, bot, config,
                                              playtime, p, botid, port, msgid,
                                              channel, event_loop, executor),
                                          loop=event_loop)
                elif playlist[guild][0]['type'] in {'FM', 'fm', 'Fm'}:
                    LOCK[guild] = False
                    asyncio.ensure_future(fm(guild, song_name, LOCK, playlist,
                                             duration, deltatime, bot, config,
                                             playtime, p, botid, port, msgid,
                                             channel),
                                          loop=event_loop)
                else:
                    LOCK[guild] = False
                    asyncio.ensure_future(migu(guild, song_name, LOCK,
                                               playlist, duration, deltatime,
                                               bot, config, playtime, p, botid,
                                               port, msgid, channel),
                                          loop=event_loop)
            else:
                if playtime[guild] < duration[guild]:
                    print("playing process time+7")
                    playtime[guild] += deltatime
                    LOCK[guild] = False
                else:
                    print("playing process end")
                    kill(guild, p)
                    if singleloops[guild] == 0:
                        playlist[guild].pop(0)
                    if singleloops[guild] == 1:
                        pass
                    if singleloops[guild] == 2:
                        playlist[guild].append(playlist[guild].pop(0))
                    if singleloops[guild] == 3:
                        playlist[guild].pop(0)
                    playtime[guild] = 0
                    duration[guild] = 0
                    LOCK[guild] = False

    print("STEP3")
    for guild in deletelist:
        savetag = True
        del playlist[guild]
    if savetag:
        await save_cache(botid, playlist, voicechannelid, msgid, channel)


@bot.task.add_interval(minutes=30)
async def keep_login():
    url = 'http://127.0.0.1:3000/login/refresh'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,
                               timeout=aiohttp.ClientTimeout(total=5)) as r:
            print(await r.text())
    if qq_enable == '1':
        url = 'http://127.0.0.1:3300/user/refresh'
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                print(await r.text())
    print('刷新登录')


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def on_btn_clicked(_: Bot, e: Event):
    print(
        f'''{e.body['user_info']['nickname']} took the {e.body['value']} pill'''
    )
    print(e.body["guild_id"])
    global playlist
    global playtime
    global duration
    global singleloops

    guild = e.body["guild_id"]
    if e.body['value'] == "NEXT":
        try:
            while LOCK[guild]:
                await asyncio.sleep(0.1)
            LOCK[guild] = True
            kill(guild, p)
            if len(playlist[guild]) == 0:
                LOCK[guild] = False
                return
            if singleloops[guild] == 2:
                playlist[guild].append(playlist[guild].pop(0))
            else:
                playlist[guild].pop(0)
            playtime[guild] = 0
            duration[guild] = 0
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                "来自" + e.body['user_info']['nickname'] + "的操作:已切换下一首")
            LOCK[guild] = False
        except:
            LOCK[guild] = False
    if e.body['value'] == "CLEAR":
        try:
            while LOCK[guild]:
                await asyncio.sleep(0.1)
            LOCK[guild] = True
            if len(playlist[guild]) > 0:
                now = playlist[guild][0]
                playlist[guild] = []
                playlist[guild].append(now)
            await bot.send(await bot.fetch_public_channel(channel[guild]),
                           "来自" + e.body['user_info']['nickname'] + "的操作:清空完成")
            LOCK[guild] = False
        except:
            LOCK[guild] = False
    if e.body['value'] == "LOOP":

        try:
            while LOCK[guild]:
                await asyncio.sleep(0.1)
            LOCK[guild] = True
            if singleloops[guild] == 0:
                singleloops[guild] = 1
                await bot.send(
                    await bot.fetch_public_channel(channel[guild]), "来自" +
                    e.body['user_info']['nickname'] + "的操作:循环模式已调整为:单曲循环")
            elif singleloops[guild] == 1:
                singleloops[guild] = 2
                await bot.send(
                    await bot.fetch_public_channel(channel[guild]), "来自" +
                    e.body['user_info']['nickname'] + "的操作:循环模式已调整为:列表循环")
            elif singleloops[guild] == 2:
                singleloops[guild] = 3
                await bot.send(
                    await bot.fetch_public_channel(channel[guild]), "来自" +
                    e.body['user_info']['nickname'] + "的操作:循环模式已调整为:随机播放")
            else:
                singleloops[guild] = 0
                await bot.send(
                    await bot.fetch_public_channel(channel[guild]),
                    "来自" + e.body['user_info']['nickname'] + "的操作:循环模式已调整为:关闭")
            LOCK[guild] = False
        except:
            LOCK[guild] = False


@bot.on_event(EventTypes.EXITED_CHANNEL)
async def on_exit_voice(_: Bot, e: Event):
    try:
        guild = e.target_id
        while LOCK[guild]:
            await asyncio.sleep(0.1)
        LOCK[guild] = True
        global playlist
        print(e.body)
        now = playlist[guild][0]
        plcp = playlist[guild]
        plcp.pop(0)
        tmp = [song for song in plcp if song['userid'] != e.body['user_id']]
        tmp.insert(0, now)
        playlist[guild] = tmp
        LOCK[guild] = False
    except Exception as e:
        LOCK[guild] = False
        print(str(e))


bot.command.update_prefixes("")

event_loop = asyncio.get_event_loop()
asyncio.ensure_future(bot.start(), loop=event_loop)
event_loop.run_forever()
