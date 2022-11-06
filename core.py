from asyncio import (AbstractEventLoop, all_tasks, ensure_future,
                     get_event_loop, new_event_loop, set_event_loop, sleep)
from concurrent.futures import ThreadPoolExecutor
from importlib import reload as reload_module
from logging import WARNING, FileHandler, Formatter, StreamHandler, getLogger
from os import _exit
from random import shuffle
from re import search
from sys import argv
from time import time

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from khl import Bot, Event, EventTypes, Message, SoftwareTypes
from khl.card import CardMessage
from psutil import Process

import music_manage
import status_manage
from voiceAPI import Voice

config = status_manage.load_config()
playlist = {}
port = {}
p = {}
pop_now = {}
deltatime = 7
singleloops = {}
rtcpport = ''
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
bili_cookie = config["b_cookie"]
schedule_server = f'{config["schedule_server_address"]}:{config["schedule_server_port"]}{config["schedule_server_path"]}'
rtcpport = ''
lyrics = {}
task_id = {}
add_LOCK = {}
deletelist = set()


def run():
    global rtcpport
    eventloop = new_event_loop()
    set_event_loop(eventloop)
    executor = ThreadPoolExecutor(1000)

    botid = argv[1]
    rtcpport = botid + '234'

    bot = Bot(token=config['token' + botid])
    bot.client.ignore_self_msg=False
    logger = getLogger('bot')
    logger.setLevel(level=WARNING)

    formatter = Formatter(
        '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    )

    file_handler = FileHandler(filename=f'bot{botid}.log', mode='a')
    file_handler.setLevel(level=WARNING)
    file_handler.setFormatter(formatter)

    stream_handler = StreamHandler()
    stream_handler.setLevel(level=WARNING)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    join_command = status_manage.custom_joincommand(config, botid, logger)
    timeout_threshold = status_manage.custom_timeout(config, logger)
    default_platform = status_manage.custom_preferred_platform(
        config, botid, logger)

    try:
        import signal
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)  # type: ignore
        logger.warning("platform:linux")
    except:
        logger.warning("platform:windows")

    @bot.command(name='导入歌单')
    async def import_playlist(msg: Message, linkid: str):
        global qq_enable
        global p
        global port
        global rtcpport
        global channel
        global voice
        global voicechannelid
        global msgid
        global JOINLOCK
        global pop_now
        global add_LOCK
        voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
        try:
            voiceid = voiceid[0].id
            if voiceid != voicechannelid[msg.ctx.guild.id]:
                try:
                    if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                        return
                except:
                    return
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        except Exception as e:
            if e.__class__ == IndexError:
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        if type(voiceid) is not str:
            return
        post_msg = get_post_msg(msg, voiceid)
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            async with session.post(url=schedule_server,
                                    json=post_msg,
                                    timeout=ClientTimeout(total=5)) as r:
                status = await r.text()
                if not post_msg['already_in'][0]:
                    add_LOCK[msg.ctx.guild.id] = True

                    if status == 'REFUSE':
                        return
                    if status == 'REPORT':
                        await msg.ctx.channel.send(
                            "当前服务器内所有机器人槽位均已满，请加入交流服务器获取备用机 https://kook.top/vyAPVw"
                        )
                        return
                    while JOINLOCK:
                        await sleep(0.1)
                    JOINLOCK = True
                    try:
                        logger.warning(voiceid)
                        try:
                            await init_guild(msg, voiceid)
                            event_loop = get_event_loop()

                            ensure_future(status_manage.start(
                                voice[msg.ctx.guild.id], voiceid,
                                msg.ctx.guild.id, voiceffmpeg, port, logger),
                                          loop=event_loop)
                            rtcpport = str(int(rtcpport) + 1)
                            await bot.client.update_listening_music(
                                f"已用槽位:{str(len(voice))}", "KO-ON",
                                SoftwareTypes.CLOUD_MUSIC)
                            JOINLOCK = False
                            add_LOCK[msg.ctx.guild.id] = False
                        except:
                            JOINLOCK = False
                            add_LOCK[msg.ctx.guild.id] = False
                    except:
                        JOINLOCK = False
                        add_LOCK[msg.ctx.guild.id] = False
                    JOINLOCK = False
                    add_LOCK[msg.ctx.guild.id] = False
                try:
                    if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                        return
                except:
                    return

                while add_LOCK[msg.ctx.guild.id]:
                    await sleep(0.1)
                global netease_cookie
                enable_netease = True
                enable_qqmusic = True
                if "163.com" in linkid:
                    enable_qqmusic = False
                if "qq.com" in linkid:
                    enable_netease = False
                try:
                    if "fcgi-bin" in linkid:
                        enable_netease = False
                        linkid = status_manage.parse_kmd_to_url(linkid)
                        headers = status_manage.get_qq_headers(qq_cookie)

                        async with session.get(
                                url=linkid,
                                headers=headers,
                                timeout=ClientTimeout(total=5)) as r:
                            linkid = await r.text()
                    pattern = r'(?<=[^user]id=)[0-9]+|(?<=playlist/)[0-9]+'
                    tmp = search(pattern, linkid)
                    assert tmp is not None
                    linkid = tmp.group()
                except Exception as e:
                    logger.warning(e)
                logger.warning(linkid)
                headers = status_manage.get_netease_headers(netease_cookie)
                if enable_netease:
                    try:
                        offset = 0
                        while True:
                            url = "http://127.0.0.1:3000/playlist/track/all?id=" + linkid + '&limit=1000&offset=' + str(
                                offset * 1000)
                            offset += 1
                            async with session.get(
                                    url,
                                    headers=headers,
                                    timeout=ClientTimeout(total=5)) as r:
                                resp_json = await r.json()
                                songs = resp_json.get("songs", [])
                                if len(songs) == 0:
                                    break
                                for song in songs:
                                    playlist[msg.ctx.guild.id].append({
                                        'name':
                                        song.get('name', '') + "-" +
                                        song.get('ar', [])[0].get('name', '') +
                                        '-' + str(song.get('id')),
                                        'userid':
                                        msg.author.id,
                                        'type':
                                        '网易',
                                        'time':
                                        int(round(time() * 1000)) +
                                        1000000000000,
                                        'display':
                                        song.get('name', '')
                                    })
                    except:
                        pass
                if enable_qqmusic:
                    try:
                        url = "http://127.0.0.1:3300/songlist?id=" + linkid
                        async with session.get(
                                url, timeout=ClientTimeout(total=5)) as r:
                            resp_json = await r.json()
                            songs = resp_json.get("data",
                                                  {}).get("songlist", [])
                            for song in songs:
                                playlist[msg.ctx.guild.id].append({
                                    'name':
                                    song.get('songname', '') + "-" +
                                    song.get('singer', [])[0].get('name', '') +
                                    '-' + str(song.get('songmid')),
                                    'userid':
                                    msg.author.id,
                                    'type':
                                    'qq',
                                    'time':
                                    int(round(time() * 1000)) + 1000000000000,
                                    'display':
                                    song.get('songname', '')
                                })
                    except:
                        pass
                await msg.ctx.channel.send("导入完成")

    @bot.command(name='导入专辑')
    async def import_netease_album(msg: Message, linkid: str):
        global qq_enable
        global playlist
        global p
        global port
        global rtcpport
        global channel
        global voice
        global voicechannelid
        global msgid
        global JOINLOCK
        global pop_now
        global add_LOCK
        voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
        try:
            voiceid = voiceid[0].id
            if voiceid != voicechannelid[msg.ctx.guild.id]:
                try:
                    if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                        return
                except:
                    return
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        except Exception as e:
            if e.__class__ == IndexError:
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        if type(voiceid) is not str:
            return
        post_msg = get_post_msg(msg, voiceid)
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            async with session.post(url=schedule_server,
                                    json=post_msg,
                                    timeout=ClientTimeout(total=5)) as r:
                status = await r.text()
                if not post_msg['already_in'][0]:
                    add_LOCK[msg.ctx.guild.id] = True

                    if status == 'REFUSE':
                        return
                    if status == 'REPORT':
                        await msg.ctx.channel.send(
                            "当前服务器内所有机器人槽位均已满，请加入交流服务器获取备用机 https://kook.top/vyAPVw"
                        )
                        return
                    while JOINLOCK:
                        await sleep(0.1)
                    JOINLOCK = True
                    try:
                        logger.warning(voiceid)
                        try:
                            await init_guild(msg, voiceid)
                            event_loop = get_event_loop()

                            ensure_future(status_manage.start(
                                voice[msg.ctx.guild.id], voiceid,
                                msg.ctx.guild.id, voiceffmpeg, port, logger),
                                          loop=event_loop)
                            rtcpport = str(int(rtcpport) + 1)
                            await bot.client.update_listening_music(
                                f"已用槽位:{str(len(voice))}", "KO-ON",
                                SoftwareTypes.CLOUD_MUSIC)
                            JOINLOCK = False
                            add_LOCK[msg.ctx.guild.id] = False
                        except:
                            JOINLOCK = False
                            add_LOCK[msg.ctx.guild.id] = False
                    except:
                        JOINLOCK = False
                        add_LOCK[msg.ctx.guild.id] = False
                    JOINLOCK = False
                    add_LOCK[msg.ctx.guild.id] = False
                try:
                    if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                        return
                except:
                    return

                while add_LOCK[msg.ctx.guild.id]:
                    await sleep(0.1)
                global netease_cookie
                try:
                    pattern = r'(?<=[^user]id=)[0-9]+'
                    tmp = search(pattern, linkid)
                    assert tmp is not None
                    linkid = tmp.group()
                except:
                    pass
                headers = status_manage.get_netease_headers(netease_cookie)
                try:
                    url = "http://127.0.0.1:3000/album?id=" + linkid

                    async with session.get(
                            url, headers=headers,
                            timeout=ClientTimeout(total=5)) as r:
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
                                int(round(time() * 1000)) + 1000000000000,
                                'display':
                                song.get('name', '')
                            })
                    await msg.ctx.channel.send("导入完成")
                except:
                    pass

    @bot.command(name='导入电台')
    async def import_netease_radio(msg: Message, linkid: str):
        global qq_enable
        global playlist
        global p
        global port
        global rtcpport
        global channel
        global voice
        global voicechannelid
        global msgid
        global JOINLOCK
        global pop_now
        global add_LOCK
        voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
        try:
            voiceid = voiceid[0].id
            if voiceid != voicechannelid[msg.ctx.guild.id]:
                try:
                    if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                        return
                except:
                    return
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        except Exception as e:
            if e.__class__ == IndexError:
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        if type(voiceid) is not str:
            return
        post_msg = get_post_msg(msg, voiceid)
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            async with session.post(url=schedule_server,
                                    json=post_msg,
                                    timeout=ClientTimeout(total=5)) as r:
                status = await r.text()
                if not post_msg['already_in'][0]:
                    add_LOCK[msg.ctx.guild.id] = True

                    if status == 'REFUSE':
                        return
                    if status == 'REPORT':
                        await msg.ctx.channel.send(
                            "当前服务器内所有机器人槽位均已满，请加入交流服务器获取备用机 https://kook.top/vyAPVw"
                        )
                        return
                    while JOINLOCK:
                        await sleep(0.1)
                    JOINLOCK = True
                    try:
                        logger.warning(voiceid)
                        try:
                            await init_guild(msg, voiceid)
                            event_loop = get_event_loop()

                            ensure_future(status_manage.start(
                                voice[msg.ctx.guild.id], voiceid,
                                msg.ctx.guild.id, voiceffmpeg, port, logger),
                                          loop=event_loop)
                            rtcpport = str(int(rtcpport) + 1)
                            await bot.client.update_listening_music(
                                f"已用槽位:{str(len(voice))}", "KO-ON",
                                SoftwareTypes.CLOUD_MUSIC)
                            JOINLOCK = False
                            add_LOCK[msg.ctx.guild.id] = False
                        except:
                            JOINLOCK = False
                            add_LOCK[msg.ctx.guild.id] = False
                    except:
                        JOINLOCK = False
                        add_LOCK[msg.ctx.guild.id] = False
                    JOINLOCK = False
                    add_LOCK[msg.ctx.guild.id] = False
                try:
                    if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                        return
                except:
                    return

                while add_LOCK[msg.ctx.guild.id]:
                    await sleep(0.1)
                global netease_cookie
                try:
                    pattern = r'(?<=[^user]id=)[0-9]+'
                    tmp = search(pattern, linkid)
                    assert tmp is not None
                    linkid = tmp.group()
                except:
                    pass
                headers = status_manage.get_netease_headers(netease_cookie)
                try:
                    offset = 0
                    while True:
                        url = "http://127.0.0.1:3000/dj/program?rid=" + linkid + "&limit=1000&offset=" + str(
                            offset * 1000)
                        offset += 1

                        async with session.get(
                                url,
                                headers=headers,
                                timeout=ClientTimeout(total=5)) as r:
                            resp_json = await r.json()
                            programs = resp_json.get("programs", [])
                            if len(programs) == 0:
                                break
                            for program in programs:
                                playlist[msg.ctx.guild.id].append({
                                    'name':
                                    program.get('mainSong', {}).get(
                                        'name', '') + '-' +
                                    str(program.get('id')),
                                    'userid':
                                    msg.author.id,
                                    'type':
                                    '网易电台',
                                    'time':
                                    int(round(time() * 1000)) + 1000000000000,
                                    'display':
                                    program.get('mainSong',
                                                {}).get('name', '')
                                })
                    await msg.ctx.channel.send("导入完成")
                except:
                    pass

    def get_post_msg(msg: Message, voiceid: str):
        return {
            "server": msg.ctx.guild.id,
            "voicechannel": voiceid,
            "botid": [botid],
            "able": [len(voice) < 2],
            "already_in": [msg.ctx.guild.id in list(voice.keys())]
        }

    async def init_guild(msg: Message, voiceid: str):
        task_id[msg.ctx.guild.id] = -1
        singleloops[msg.ctx.guild.id] = 0
        timeout[msg.ctx.guild.id] = 0
        LOCK[msg.ctx.guild.id] = False
        pop_now[msg.ctx.guild.id] = False
        playlist[msg.ctx.guild.id] = []
        voicechannelid[msg.ctx.guild.id] = voiceid
        channel[msg.ctx.guild.id] = msg.ctx.channel
        playtime[msg.ctx.guild.id] = 0
        msgid[msg.ctx.guild.id] = "0"
        duration[msg.ctx.guild.id] = 0
        port[msg.ctx.guild.id] = rtcpport
        await msg.ctx.channel.send("已加入频道")
        voice[msg.ctx.guild.id] = Voice(config['token' + botid])

    @bot.command(name='退出语音')
    async def exit_voice(msg: Message):
        voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
        try:
            if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                return
        except:
            return
        try:
            voiceid = voiceid[0].id
            if voiceid != voicechannelid[msg.ctx.guild.id]:
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        except:
            await msg.ctx.channel.send("请先进入听歌频道或退出重进")
            return
        try:
            deletelist.add(msg.ctx.guild.id)
            await msg.ctx.channel.send("退出成功")
        except:
            pass

    @bot.command(name=join_command)
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
        global pop_now
        while JOINLOCK:
            await sleep(0.1)
        JOINLOCK = True
        try:
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
            logger.warning(voiceid)
            try:
                add_LOCK[msg.ctx.guild.id] = False
                await init_guild(msg, voiceid)
                event_loop = get_event_loop()

                ensure_future(status_manage.start(voice[msg.ctx.guild.id],
                                                  voiceid, msg.ctx.guild.id,
                                                  voiceffmpeg, port, logger),
                              loop=event_loop)
                rtcpport = str(int(rtcpport) + 1)
                await bot.client.update_listening_music(
                    f"已用槽位:{str(len(voice))}", "KO-ON",
                    SoftwareTypes.CLOUD_MUSIC)
                JOINLOCK = False
            except:
                JOINLOCK = False
        except:
            JOINLOCK = False
        JOINLOCK = False

    @bot.command(name='绑定点歌频道')
    async def bind_text_channel(msg: Message):
        global channel
        await msg.ctx.channel.send("绑定频道")
        channel[msg.ctx.guild.id] = msg.ctx.channel

    @bot.command(name='清空歌单')
    async def clear_playlist(msg: Message):
        try:
            if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                return
        except:
            return
        try:
            while LOCK[msg.ctx.guild.id]:
                await sleep(0.1)
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
        LOCK[msg.ctx.guild.id] = False

    @bot.command(name="下一首")
    async def nextmusic(msg: Message):
        try:
            if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                return
        except:
            return
        try:
            global playlist
            global playtime

            global duration
            while LOCK[msg.ctx.guild.id]:
                await sleep(0.1)
            LOCK[msg.ctx.guild.id] = True
            status_manage.kill(msg.ctx.guild.id, p, logger)
            try:
                for task in all_tasks():
                    if id(task) == task_id[msg.ctx.guild.id]:
                        logger.warning('cancelling the task {}: {}'.format(
                            id(task), task.cancel()))
                task_id[msg.ctx.guild.id] = -1
            except:
                pass
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
        LOCK[msg.ctx.guild.id] = False

    @bot.command(name="点歌")
    async def addmusic(msg: Message, *args):
        global qq_enable
        global playlist
        global p
        global port
        global rtcpport
        global channel
        global voice
        global voicechannelid
        global msgid
        global JOINLOCK
        global pop_now
        global add_LOCK
        voiceid = await msg.ctx.guild.fetch_joined_channel(msg.author)
        try:
            voiceid = voiceid[0].id
            if voiceid != voicechannelid[msg.ctx.guild.id]:
                try:
                    if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                        return
                except:
                    return
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        except Exception as e:
            if e.__class__ == IndexError:
                await msg.ctx.channel.send("请先进入听歌频道或退出重进")
                return
        if type(voiceid) is not str:
            return
        post_msg = get_post_msg(msg, voiceid)
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            async with session.post(url=schedule_server,
                                    json=post_msg,
                                    timeout=ClientTimeout(total=5)) as r:
                status = await r.text()
                if not post_msg['already_in'][0]:
                    add_LOCK[msg.ctx.guild.id] = True

                    if status == 'REFUSE':
                        return
                    if status == 'REPORT':
                        await msg.ctx.channel.send(
                            "当前服务器内所有机器人槽位均已满，请加入交流服务器获取备用机 https://kook.top/vyAPVw"
                        )
                        return
                    while JOINLOCK:
                        await sleep(0.1)
                    JOINLOCK = True
                    try:
                        logger.warning(voiceid)
                        try:
                            await init_guild(msg, voiceid)
                            event_loop = get_event_loop()

                            ensure_future(status_manage.start(
                                voice[msg.ctx.guild.id], voiceid,
                                msg.ctx.guild.id, voiceffmpeg, port, logger),
                                          loop=event_loop)
                            rtcpport = str(int(rtcpport) + 1)
                            await bot.client.update_listening_music(
                                f"已用槽位:{str(len(voice))}", "KO-ON",
                                SoftwareTypes.CLOUD_MUSIC)
                            JOINLOCK = False
                            add_LOCK[msg.ctx.guild.id] = False
                        except:
                            JOINLOCK = False
                            add_LOCK[msg.ctx.guild.id] = False
                    except:
                        JOINLOCK = False
                        add_LOCK[msg.ctx.guild.id] = False
                    JOINLOCK = False
                    add_LOCK[msg.ctx.guild.id] = False
                try:
                    if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                        return
                except:
                    return

                while add_LOCK[msg.ctx.guild.id]:
                    await sleep(0.1)
                try:
                    args = list(args)
                    typ = default_platform
                    song_name = ''
                    coefficient = 1
                    if args[0] in status_manage.platform:
                        typ = args[0]
                        args.pop(0)
                        if typ in {
                                'qq', 'qq音乐', 'QQ', 'QQ音乐', 'k歌', 'K歌', '全民k歌',
                                '全民K歌'
                        } and qq_enable == '0':
                            await msg.ctx.channel.send('未启用QQ音乐与全民k歌点歌')
                            return None
                        if typ in {'ytb', 'YTB', 'youtube', 'Youtube', '油管'}:
                            await msg.ctx.channel.send('Youtube点歌功能因涉及敏感信息暂时下线'
                                                       )
                            return None
                    if args[-1] in {
                            "--置顶", "-置顶", "--top", "-top", "/置顶", "/top"
                    }:
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
                        int(round(time() * 1000)) * coefficient,
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
        global bili_cookie
        try:
            reload_module(status_manage)
            reload_module(music_manage)
            config = status_manage.load_config()
            netease_phone = config["n_phone"]
            netease_passwd = config["n_passwd"]
            netease_cookie = config["n_cookie"]
            qq_cookie = config["q_cookie"]
            qq_id = config["q_id"]
            qq_enable = config["qq_enable"]
            bili_cookie = config["b_cookie"]
            firstlogin = True
            await msg.ctx.channel.send("reload成功")
        except:
            await msg.ctx.channel.send("reload失败")

    @bot.command(name="REBOOT" + str(botid))
    async def reboot(msg: Message):
        _exit(0)

    @bot.command(name="歌单")
    async def prtlist(msg: Message):
        try:
            if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
                return
        except:
            return
        try:
            global playlist
            cm = CardMessage()
            c = status_manage.get_playlist(msg.ctx.guild.id, playlist)
            cm.append(c)
            await msg.ctx.channel.send(cm)
        except:
            pass

    @bot.command(name="帮助")
    async def help(msg: Message):
        await msg.ctx.channel.send(
            status_manage.get_helpcm(default_platform, join_command))

    @bot.command(name="状态")
    async def status(msg: Message):
        await msg.ctx.channel.send("已用槽位:" + str(len(voice)))

    @bot.command(name="循环模式")
    async def singlesongloop(msg: Message):
        global singleloops
        try:
            if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
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
            if msg.ctx.channel.id != channel[msg.ctx.guild.id].id:
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
                process = Process(voiceffmpeg[msg.ctx.guild.id].pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
            except Exception as e:
                logger.warning(e)
            voice[msg.ctx.guild.id].is_exit = True
            del voice[msg.ctx.guild.id]
            voicechannelid[msg.ctx.guild.id] = voiceid
            del voiceffmpeg[msg.ctx.guild.id]
            await msg.ctx.channel.send("已加入频道")
            voice[msg.ctx.guild.id] = Voice(config['token' + botid])
            event_loop = get_event_loop()
            ensure_future(status_manage.start(voice[msg.ctx.guild.id], voiceid,
                                              msg.ctx.guild.id, voiceffmpeg,
                                              port, logger),
                          loop=event_loop)
            rtcpport = str(int(rtcpport) + 1)
        except Exception as e:
            logger.warning(e)

    @bot.command(name="搜索")
    async def musicsearch(msg: Message, *args):
        global netease_cookie
        if botid != '1':
            return
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            await msg.ctx.channel.send("请稍等,正在处理中")
            headers = status_manage.get_netease_headers(netease_cookie)
            song_name = ''
            for st in args:
                song_name = song_name + st + " "
            url = "http://127.0.0.1:3000/search?keywords=" + song_name + "&limit=5"

            async with session.get(url=url,
                                   headers=headers,
                                   timeout=ClientTimeout(total=5)) as r:
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
                async with session.get(url=url,
                                       timeout=ClientTimeout(total=5)) as r:
                    songs = (await r.json())['data']['song']['itemlist']
                try:
                    for song in songs:
                        text += song['name'] + '-' + song['singer'] + '\n'
                except:
                    text += '无\n'

            text += '网易电台结果:\n'
            url = "http://127.0.0.1:3000/search?keywords=" + song_name + "&limit=5&type=2000"
            async with session.get(url=url,
                                   timeout=ClientTimeout(total=5)) as r:
                songs = (await r.json())['data']['resources']
            try:
                for song in songs:
                    text += song['baseInfo']['mainSong']['name'] + '-' + song[
                        'baseInfo']['mainSong']['artists'][0][
                            'name'] + '-' + song['resourceId'] + '\n'
            except:
                text += '无\n'

            text += '咪咕结果:\n'
            url = "http://127.0.0.1:3400/search?keyword=" + song_name
            async with session.get(url=url,
                                   timeout=ClientTimeout(total=5)) as r:
                songs = (await r.json())['data']['list']
            try:
                i = 0
                for song in songs:
                    i += 1
                    text += song['name'] + '-' + song['artists'][0][
                        'name'] + '-' + song['album']['name'] + '-' + song[
                            'cid'] + '\n'
                    if i == 5:
                        break
            except:
                text += '无\n'
            await msg.ctx.channel.send(text)

    async def load_cache(botid: str, singleloops: dict, timeout: dict,
                         LOCK: dict, playtime: dict, duration: dict,
                         port: dict, voice: dict, config: dict,
                         voiceffmpeg: dict, event_loop: AbstractEventLoop):
        global playlist
        global voicechannelid
        global msgid
        global channel
        global rtcpport
        try:
            logger.warning('loading cache')

            with open(botid + 'playlistcache', 'r', encoding='utf-8') as f:
                playlist = eval(f.read())
            with open(botid + 'voiceidcache', 'r', encoding='utf-8') as f:
                voicechannelid = eval(f.read())
            with open(botid + 'msgidcache', 'r', encoding='utf-8') as f:
                msgid = eval(f.read())
            with open(botid + 'channelidcache', 'r', encoding='utf-8') as f:
                tmpchannel = eval(f.read())
            for guild, voiceid in voicechannelid.items():
                logger.warning(voiceid)
                channel[guild] = await bot.client.fetch_public_channel(
                    tmpchannel[guild])
                pop_now[guild] = False
                singleloops[guild] = 0
                timeout[guild] = 0
                LOCK[guild] = False
                playtime[guild] = 0
                duration[guild] = 0
                add_LOCK[guild] = False
                port[guild] = rtcpport
                voice[guild] = Voice(config['token' + botid])
                ensure_future(status_manage.start(voice[guild], voiceid, guild,
                                                  voiceffmpeg, port, logger),
                              loop=event_loop)
                rtcpport = str(int(rtcpport) + 1)
                await sleep(0.3)
        except:
            logger.warning('load cache fail')

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
        global pop_now
        global deletelist
        if firstlogin:
            firstlogin = False
            await status_manage.login(bot, botid, qq_enable, netease_phone,
                                      netease_passwd, qq_cookie, qq_id, voice,
                                      logger)
        if load:
            load = False
            event_loop = get_event_loop()
            await load_cache(botid, singleloops, timeout, LOCK, playtime,
                             duration, port, voice, config, voiceffmpeg,
                             event_loop)
        savetag = False
        for guild, songlist in playlist.items():

            if channel.get(guild, -1) == -1 or timeout.get(
                    guild, -1) == -1 or voiceffmpeg.get(guild, -1) == -1:
                continue
            if len(playlist[guild]) == 0:
                logger.warning("timeout +7")
                timeout[guild] += deltatime
                if timeout[guild] > timeout_threshold:
                    try:
                        deletelist.add(guild)
                        logger.warning("timeout auto leave")
                    except:
                        pass
                continue
            else:
                timeout[guild] = 0
                if playtime[guild] == 0:
                    if LOCK[guild]:
                        logger.warning("LOCK")
                        continue
                    logger.warning("playing process start")
                    savetag = True
                    if singleloops[guild] == 3:
                        shuffle(playlist[guild])
                    if singleloops[guild] in {0, 1}:
                        playlist[guild].sort(key=lambda x: list(x.values())[3])
                    song_name = playlist[guild][0]['name']
                    if song_name == "":
                        LOCK[guild] = False
                        continue
                    event_loop = get_event_loop()
                    if playlist[guild][0]['type'] in {
                            '网易', 'netease', 'Netease', '网易云', '网易云音乐', '网易音乐'
                    }:
                        task_id[guild] = id(
                            ensure_future(music_manage.netease(
                                guild, song_name, LOCK, netease_cookie,
                                playlist, duration, deltatime, bot, config,
                                playtime, p, botid, port, msgid, channel,
                                event_loop, voiceffmpeg, executor, logger),
                                          loop=event_loop))
                    elif playlist[guild][0]['type'] in {
                            'bili', 'b站', 'bilibili', 'Bili', 'Bilibili', 'B站'
                    }:
                        ensure_future(music_manage.bili(
                            guild, song_name, LOCK, bili_cookie, playlist,
                            duration, deltatime, bot, config, playtime, p,
                            botid, port, msgid, channel, voiceffmpeg,
                            event_loop, executor, logger),
                                      loop=event_loop)
                    elif playlist[guild][0]['type'] in {'网易电台', '电台'}:
                        ensure_future(music_manage.neteaseradio(
                            guild, song_name, LOCK, netease_cookie, playlist,
                            duration, deltatime, bot, config, playtime, p,
                            botid, port, msgid, channel, voiceffmpeg,
                            event_loop, executor, logger),
                                      loop=event_loop)
                    elif playlist[guild][0]['type'] in {
                            'qq', 'qq音乐', 'QQ', 'QQ音乐'
                    }:
                        task_id[guild] = id(
                            ensure_future(music_manage.qqmusic(
                                guild, song_name, LOCK, playlist, duration,
                                deltatime, bot, config, playtime, p, botid,
                                port, msgid, channel, qq_cookie, voiceffmpeg,
                                event_loop, executor, logger),
                                          loop=event_loop))
                    elif playlist[guild][0]['type'] in {
                            'k歌', 'K歌', '全民k歌', '全民K歌'
                    }:
                        ensure_future(music_manage.kmusic(
                            guild, song_name, LOCK, playlist, duration,
                            deltatime, bot, config, playtime, p, botid, port,
                            msgid, channel, voiceffmpeg, event_loop, executor,
                            logger),
                                      loop=event_loop)
                    elif playlist[guild][0]['type'] in {
                            'ytb', 'YTB', 'youtube', 'Youtube', '油管'
                    }:
                        ensure_future(music_manage.ytb(
                            guild, song_name, LOCK, playlist, duration,
                            deltatime, bot, config, playtime, p, botid, port,
                            msgid, channel, event_loop, executor, voiceffmpeg,
                            logger),
                                      loop=event_loop)
                    elif playlist[guild][0]['type'] in {'FM', 'fm', 'Fm'}:
                        ensure_future(music_manage.fm(
                            guild, song_name, LOCK, playlist, duration,
                            deltatime, bot, config, playtime, p, botid, port,
                            msgid, channel, voiceffmpeg, event_loop, executor,
                            logger),
                                      loop=event_loop)
                    else:
                        ensure_future(music_manage.migu(
                            guild, song_name, LOCK, playlist, duration,
                            deltatime, bot, config, playtime, p, botid, port,
                            msgid, channel, voiceffmpeg, event_loop, executor,
                            logger),
                                      loop=event_loop)
                else:
                    if playtime[guild] < duration[guild]:
                        logger.warning("playing process time+7")
                        playtime[guild] += deltatime
                    else:
                        logger.warning("playing process end")
                        status_manage.kill(guild, p, logger)
                        async with ClientSession(connector=TCPConnector(
                                ssl=False)) as session:
                            await status_manage.delmsg(msgid[guild], config,
                                                       botid, session, logger)
                        try:
                            for task in all_tasks():
                                if id(task) == task_id[guild]:
                                    logger.warning(
                                        'cancelling the task {}: {}'.format(
                                            id(task), task.cancel()))
                                    task_id[guild] = -1
                        except:
                            pass
                        if singleloops[guild] == 0:
                            playlist[guild].pop(0)
                        if singleloops[guild] == 1:
                            if pop_now[guild]:
                                playlist[guild].pop(0)
                                pop_now[guild] = False
                        if singleloops[guild] == 2:
                            tmp = playlist[guild].pop(0)
                            if pop_now[guild]:
                                pop_now[guild] = False
                            else:
                                playlist[guild].append(tmp)
                        if singleloops[guild] == 3:
                            playlist[guild].pop(0)
                        playtime[guild] = 0
                        duration[guild] = 0
                        LOCK[guild] = False
        for guild in deletelist:
            try:
                savetag = True
                await leave_voice_channel(guild)
                del playlist[guild]
            except:
                pass
        deletelist.clear()
        if savetag:
            await status_manage.save_cache(botid, playlist, voicechannelid,
                                           msgid, channel)

    async def leave_voice_channel(guild: str):
        status_manage.kill(guild, p, logger)
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            await status_manage.delmsg(msgid[guild], config, botid, session,
                                       logger)
        try:
            for task in all_tasks():
                if id(task) == task_id[guild]:
                    logger.warning('cancelling the task {}: {}'.format(
                        id(task), task.cancel()))
                    task_id[guild] = -1
        except:
            pass
        await status_manage.disconnect(bot, guild, voice, timeout, voiceffmpeg,
                                       LOCK, msgid, voicechannelid, channel,
                                       singleloops, playtime, duration, port,
                                       pop_now, task_id, add_LOCK, logger)

    @bot.task.add_interval(minutes=30)
    async def keep_login():
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            url = 'http://127.0.0.1:3000/login/refresh'
            async with session.get(url=url,
                                   timeout=ClientTimeout(total=5)) as r:
                logger.warning(await r.text())
            if qq_enable == '1':
                url = 'http://127.0.0.1:3300/user/refresh'
                async with session.get(url=url,
                                       timeout=ClientTimeout(total=5)) as r:
                    logger.warning(await r.text())
        logger.warning('刷新登录')

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def on_btn_clicked(_: Bot, e: Event):
        logger.warning(
            f'''{e.body['user_info']['nickname']} took the {e.body['value']} pill'''
        )
        logger.warning(e.body["guild_id"])
        global playlist
        global playtime
        global duration
        global singleloops

        guild = e.body["guild_id"]
        if e.body['value'] == "NEXT":
            try:
                while LOCK[guild]:
                    await sleep(0.1)
                LOCK[guild] = True
                status_manage.kill(guild, p, logger)
                try:
                    for task in all_tasks():
                        if id(task) == task_id[guild]:
                            logger.warning('cancelling the task {}: {}'.format(
                                id(task), task.cancel()))
                    task_id[guild] = -1
                except:
                    pass
                if len(playlist[guild]) == 0:
                    LOCK[guild] = False
                    return
                if singleloops[guild] == 2:
                    playlist[guild].append(playlist[guild].pop(0))
                else:
                    playlist[guild].pop(0)
                playtime[guild] = 0
                duration[guild] = 0
                await bot.client.send(
                    channel[guild],
                    "来自" + e.body['user_info']['nickname'] + "的操作:已切换下一首")
                LOCK[guild] = False
            except:
                LOCK[guild] = False
        if e.body['value'] == "CLEAR":
            try:
                while LOCK[guild]:
                    await sleep(0.1)
                LOCK[guild] = True
                if len(playlist[guild]) > 0:
                    now = playlist[guild][0]
                    playlist[guild] = []
                    playlist[guild].append(now)
                await bot.client.send(
                    channel[guild],
                    "来自" + e.body['user_info']['nickname'] + "的操作:清空完成")
                LOCK[guild] = False
            except:
                LOCK[guild] = False
        if e.body['value'] == "LOOP":

            try:
                while LOCK[guild]:
                    await sleep(0.1)
                LOCK[guild] = True
                if singleloops[guild] == 0:
                    singleloops[guild] = 1
                    await bot.client.send(
                        channel[guild], "来自" +
                        e.body['user_info']['nickname'] + "的操作:循环模式已调整为:单曲循环")
                elif singleloops[guild] == 1:
                    singleloops[guild] = 2
                    await bot.client.send(
                        channel[guild], "来自" +
                        e.body['user_info']['nickname'] + "的操作:循环模式已调整为:列表循环")
                elif singleloops[guild] == 2:
                    singleloops[guild] = 3
                    await bot.client.send(
                        channel[guild], "来自" +
                        e.body['user_info']['nickname'] + "的操作:循环模式已调整为:随机播放")
                else:
                    singleloops[guild] = 0
                    await bot.client.send(
                        channel[guild], "来自" +
                        e.body['user_info']['nickname'] + "的操作:循环模式已调整为:关闭")
                LOCK[guild] = False
            except:
                LOCK[guild] = False

    @bot.task.add_interval(minutes=1)
    async def auto_check_exit_voice():
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            for guild_id,voice_id in voicechannelid.items():
                    response=await status_manage.vcch_usrlist(voice_id,config,botid,session)
                    if len(response['data'])<=1:
                        logger.warning(f'{guild_id} empty leave')
                        deletelist.add(guild_id)

    bot.command.update_prefixes("")

    ensure_future(bot.start(), loop=eventloop)
    eventloop.run_forever()


run()
