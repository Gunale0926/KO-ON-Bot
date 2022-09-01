from asyncio import AbstractEventLoop, ensure_future, sleep, wait
from concurrent.futures import ThreadPoolExecutor
from json import dumps, loads
from logging import Logger
from re import search
from subprocess import PIPE, STDOUT, Popen

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from functools import partial
from func_timeout import func_set_timeout, FunctionTimedOut
from khl.card import Card, CardMessage, Element, Module, Types
from khl import Bot, SoftwareTypes
from psutil import Process

from voiceAPI import Voice

platform = {
    '网易', 'netease', 'Netease', '网易云', '网易云音乐', '网易音乐', 'qq', 'qq音乐', 'QQ',
    'QQ音乐', '网易电台', '电台', '咪咕', '咪咕音乐', 'bili', 'b站', 'bilibili', 'Bili',
    'Bilibili', 'B站', 'k歌', 'K歌', '全民k歌', '全民K歌', 'ytb', 'YTB', 'youtube',
    'Youtube', '油管', 'FM', 'fm', 'Fm'
}


def custom_timeout(config: dict, logger: Logger) -> int:
    try:
        assert config['timeout'] != '' and config['timeout'].isdigit()
        logger.warning("自定义超时阈值装载:" + config['timeout'])
        return int(config['timeout'])
    except:
        logger.warning("默认超时阈值装载")
        return 60


def custom_joincommand(config: dict, botid: str, logger: Logger) -> str:
    try:
        assert config[f'join_command{botid}'] != ''
        logger.warning("自定义呼叫命令装载:" + config[f'join_command{botid}'])
        return config[f'join_command{botid}']
    except:
        logger.warning("默认呼叫命令装载")
        return f'{botid}号加入语音'


def custom_preferred_platform(config: dict, botid: str, logger: Logger) -> str:
    try:
        assert 'default_platform' + botid in config
        if config['default_platform' + botid] in platform:
            logger.warning(f"自定义首选平台装载:{config['default_platform' + botid]}")
            return config['default_platform' + botid]
        else:
            logger.warning("配置文件中的首选平台不在支持的参数列表中")
            logger.warning(f"支持的平台关键词:{platform}")
            logger.warning("默认首选平台装载:网易")
            return "网易"
    except:
        logger.warning("默认首选平台装载:网易")
        return '网易'


def lrc_list_to_dict(lrclist: list, lrcdict: dict, bias=0.0):
    for lyric in lrclist:
        lrc_word = lyric.replace("[", "]").strip().split("]")
        for i in range(len(lrc_word) - 1):
            if lrc_word[i]:
                try:
                    timestamp = lrc_word[i].strip().split(":")
                    lrcdict[abs(
                        int(timestamp[0]) * 60.000 + float(timestamp[1]) +
                        bias)] = lrc_word[-1]
                except:
                    pass


def get_qq_headers(qq_cookie: str) -> dict:
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
    return headers


def get_netease_headers(netease_cookie: str) -> dict:
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
    return headers


def get_helpcm(default_platform: str) -> list:
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
                "content": "**1.  点歌   +    (平台)    +    歌名    +    (--置顶)**"
            }
        }, {
            "type": "section",
            "text": {
                "type":
                "kmarkdown",
                "content":
                "功能:    将歌曲加到播放队列中\n**[Warning]**:\n歌名中如果有英文引号等特殊字符，需要将歌名用英文引号括起来\n例如  **点歌 \"Rrhar'il\"**\n**[Feature and Tips]**:\n现支持QQ音乐、全民k歌、咪咕音乐、网易云音乐、网易云音乐电台、Youtube、蜻蜓Fm广播电台与B站，若不写平台则默认从"
                + default_platform +
                "获取数据\n**1.**B站在使用链接点歌时支持分P\n**2.**咪咕音乐全会员\n**3.**QQ音乐，全民K歌需要单独安装api并在config.json中启用平台\n**4.**网易云电台仅支持从节目id点播，b站支持从视频名(可模糊搜索)、BV号与链接点播，全民k歌、蜻蜓Fm广播电台与Youtube仅支持从链接点播\n**5.**在指令最后带上“--置顶”会将歌曲添加到播放队列最前端\n**6.**如果需要指定歌曲版本播放，可以在歌名后添加歌手\n例如  **点歌 勇敢勇敢-黄勇**\n例如  **点歌 qq heavensdoor**\n例如  **点歌 勇敢勇敢-黄勇 --置顶**\n例如  **点歌 网易 勇敢勇敢-黄勇**\n例如  **点歌 b站 BV1qa411e7Fi**\n例如  **点歌 你看到的我**\n例如  **点歌 网易电台 2499131107**\n例如  **点歌 咪咕 青花瓷**\n例如  **点歌 b站 https://www.bilibili.com/video/BV1kT4y1X7UW?p=4**\n例如  **点歌 k歌 https://node.kg.qq.com/play?s=R2M-Y3Rux5IKPRyf**\n例如  **点歌 ytb https://www.youtube.com/watch?v=WMgYcBvw0dk**\n例如  **点歌 fm https://www.qingting.fm/radios/339**"
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


async def bsearch(keyword: str, bili_cookie: str, session: ClientSession):
    url = f'https://api.bilibili.com/x/web-interface/search/type?&page_size=1&keyword={keyword}&search_type=video'
    headers = {
        'Host': 'api.bilibili.com',
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'cookie': bili_cookie
    }
    async with session.get(url=url,
                           headers=headers,
                           timeout=ClientTimeout(total=5)) as r:
        return await r.json()


async def getCidAndTitle(duration: dict,
                         deltatime: int,
                         guild: str,
                         bvid: str,
                         session: ClientSession,
                         logger: Logger,
                         p: int = 1):
    url = 'https://api.bilibili.com/x/web-interface/view?bvid=' + bvid
    async with session.get(url=url, timeout=ClientTimeout(total=5)) as r:
        data = (await r.json())['data']
    title = data['title']
    cid = data['pages'][p - 1]['cid']
    duration[guild] = data['pages'][p - 1]['duration'] + deltatime
    mid = str(data['owner']['mid'])
    name = data['owner']['name']
    pic = data['pic']
    logger.warning(f"{cid},{title},{mid}")
    return str(cid), title, mid, name, pic


async def getInformation(duration: dict, deltatime: int, bvid: str, guild: str,
                         session: ClientSession, logger: Logger):
    bvid = bvid.replace("?p=", " ")
    item = []
    if len(bvid) == 12:

        cid, title, mid, name, pic = await getCidAndTitle(
            duration, deltatime, guild, bvid[:12], session, logger, 1)
        item.append(bvid)
    else:
        cid, title, mid, name, pic = await getCidAndTitle(
            duration, deltatime, guild, bvid[:12], session, logger,
            int(bvid[13:]))
        item.append(bvid[:12])
    item.append(cid)
    item.append(title)
    item.append(mid)
    item.append(name)
    item.append(pic)

    return item


async def getAudio(guild: str, item: list, botid: str, session: ClientSession):
    baseUrl = 'http://api.bilibili.com/x/player/playurl?fnval=16&'
    bvid, cid, title, mid, name, pic = item[0], item[1], item[2], item[
        3], item[4], item[5]
    url = baseUrl + 'bvid=' + bvid + '&cid=' + cid
    async with session.get(url=url, timeout=ClientTimeout(total=5)) as r:
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
    async with session.get(url=audioUrl,
                           headers=headers,
                           timeout=ClientTimeout(total=10)) as r:
        with open(guild + "_" + botid + ".mp3", 'wb') as f:
            while True:
                chunk = await r.content.read()
                if not chunk:
                    break
                f.write(chunk)
    return bvid, cid, title, mid, name, pic


def parse_kmd_to_url(link: str):
    try:
        pattern = r'(?<=\[)(.*?)(?=\])'
        tmp = search(pattern, link)
        assert tmp is not None
        link = tmp.group()
        return link
    except:
        return link


def start_play(guild: str, port: dict, botid: str):
    return Popen(
        'ffmpeg -re -nostats -i "' + guild + "_" + botid +
        '.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:' +
        port[guild],
        shell=True,
        #        stdout=PIPE,
        #        stderr=STDOUT,
        encoding='utf-8')


def get_playlist(guild: str, playlist: dict):
    c = Card(color="#6AC629")
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


async def delmsg(msg_id: str, config: dict, botid: str, session: ClientSession,
                 logger: Logger):
    logger.warning(msg_id)
    url = 'https://www.kookapp.cn/api/v3/message/delete'
    data = {"msg_id": msg_id}
    headers = {"Authorization": "Bot " + config['token' + botid]}
    async with session.post(url=url,
                            data=data,
                            headers=headers,
                            timeout=ClientTimeout(total=5)) as r:
        logger.warning(await r.text())


async def uptmsg(msg_id: str, content: str, config: dict, botid: str,
                 session: ClientSession, logger: Logger):
    logger.warning(msg_id)
    url = 'https://www.kookapp.cn/api/v3/message/update'
    data = {"msg_id": msg_id, "content": content}
    headers = {"Authorization": "Bot " + config['token' + botid]}
    async with session.post(url=url,
                            data=data,
                            headers=headers,
                            timeout=ClientTimeout(total=5)) as r:
        logger.warning(await r.text())


def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            configstr = f.read().replace('\\', '!')
            configtmp = loads(configstr)
            config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
            return config
    except:
        with open("config.json", "r", encoding="GBK") as f:
            configstr = f.read().replace('\\', '!')
            configtmp = loads(configstr)
            config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
            return config


async def login(bot: Bot, botid: str, qq_enable: str, netease_phone: str,
                netease_passwd: str, qq_cookie: str, qq_id: str, voice: dict,
                logger: Logger):
    logger.warning("id:" + botid)
    logger.warning('login check')
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        await bot.client.update_listening_music(f"已用槽位:{str(len(voice))}",
                                                "KO-ON",
                                                SoftwareTypes.CLOUD_MUSIC)
        url = 'http://127.0.0.1:3000/login/status?timestamp='
        logger.warning(url)
        async with session.get(url=url, timeout=ClientTimeout(total=5)) as r:
            response = await r.json()
        logger.warning(response)
        try:
            response = response['data']['account']['status']
            if response == -10:
                url = 'http://127.0.0.1:3000/login/cellphone?phone=' + netease_phone + '&password=' + netease_passwd
                async with session.get(url=url,
                                       timeout=ClientTimeout(total=5)) as r:
                    logger.warning(await r.text())
                logger.warning('网易云登陆成功')
        except:
            url = 'http://127.0.0.1:3000/login/cellphone?phone=' + netease_phone + '&password=' + netease_passwd
            async with session.get(url=url,
                                   timeout=ClientTimeout(total=5)) as r:
                logger.warning(await r.text())
            logger.warning('网易云登陆成功')
        logger.warning('网易已登录')
        url = 'http://127.0.0.1:3000/login/refresh'
        async with session.get(url=url, timeout=ClientTimeout(total=5)) as r:
            logger.warning(await r.text())
        logger.warning('刷新登录cookie')
        if qq_enable == "1":
            url = 'http://127.0.0.1:3300/user/setCookie'
            data = {"data": qq_cookie}
            async with session.post(url=url,
                                    data=data,
                                    timeout=ClientTimeout(total=5)) as r:
                logger.warning(await r.text())
            url = 'http://127.0.0.1:3300/user/getCookie?id=' + qq_id

            async with session.get(url=url,
                                   timeout=ClientTimeout(total=5)) as r:
                logger.warning(await r.text())
            logger.warning('QQ已登录')


async def save_cache(botid: str, playlist: dict, voicechannelid: dict,
                     msgid: dict, channel: dict):
    with open(botid + 'playlistcache', 'w', encoding='utf-8') as f:
        f.write(str(playlist))
    with open(botid + 'voiceidcache', 'w', encoding='utf-8') as f:
        f.write(str(voicechannelid))
    with open(botid + 'msgidcache', 'w', encoding='utf-8') as f:
        f.write(str(msgid))
    with open(botid + 'channelidcache', 'w', encoding='utf-8') as f:
        tmp = {}
        for guild, chl in channel.items():
            tmp[guild] = chl.id
        f.write(str(tmp))


def kill(guild: str, p: dict, logger: Logger):
    try:
        process = Process(p[guild].pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    except Exception as e:
        logger.warning(e)


async def start(voice: Voice, voiceid: str, guild: str, voiceffmpeg: dict,
                port: dict, logger: Logger):
    await wait([
        voice_Engine(voice, voiceid, guild, voiceffmpeg, port, logger),
        voice.handler()
    ])


async def voice_Engine(voice: Voice, voiceid: str, guild: str,
                       voiceffmpeg: dict, port: dict, logger: Logger):
    logger.warning(voiceid)
    rtp_url = ''
    voice.channel_id = voiceid
    while True:
        if len(voice.rtp_url) != 0:
            rtp_url = voice.rtp_url
            comm = "ffmpeg -re -loglevel debug -nostats -stream_loop -1 -i zmq:tcp://127.0.0.1:" + port[
                guild] + " -map 0:a:0 -acodec libopus -ab 128k -filter:a volume=0.15 -ac 2 -ar 48000 -f tee [select=a:f=rtp:ssrc=1357:payload_type=100]" + rtp_url
            logger.warning(comm)
            voiceffmpeg[guild] = Popen(comm,
                                       shell=True,
                                       stdout=PIPE,
                                       stderr=STDOUT,
                                       encoding='utf-8')
            break
        await sleep(0.1)


async def disconnect(bot: Bot, guild: str, voice: dict, timeout: dict,
                     voiceffmpeg: dict, LOCK: dict, msgid: dict,
                     voicechannelid: dict, channel: dict, singleloops: dict,
                     playtime: dict, duration: dict, port: dict, pop_now: dict,
                     task_id: dict, add_LOCK: dict, logger: Logger):
    try:
        process = Process(voiceffmpeg[guild].pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    except Exception as e:
        logger.warning(e)
    voice[guild].is_exit = True
    del timeout[guild]
    del voiceffmpeg[guild]
    del voice[guild]
    del LOCK[guild]
    del msgid[guild]
    del voicechannelid[guild]
    del channel[guild]
    del singleloops[guild]
    del playtime[guild]
    del duration[guild]
    del port[guild]
    del pop_now[guild]
    del task_id[guild]
    del add_LOCK[guild]
    await bot.client.update_listening_music(f"已用槽位:{str(len(voice))}", "KO-ON",
                                            SoftwareTypes.CLOUD_MUSIC)
    logger.warning(str(guild) + " disconnected")
@func_set_timeout(7)
def delay_alignment(p: Popen, run_status: dict, logger: Logger):
    while p.poll() is None:
        assert p.stdout is not None
        line = p.stdout.readline().strip()
        logger.warning(line)
        if "#0:0" in line:
            run_status['status'] = 'FINISH'
            break


async def async_run_in_executor(f, *args, loop: AbstractEventLoop,
                                executor: ThreadPoolExecutor, run_status: dict,
                                **kwargs):
    try:
        result = await loop.run_in_executor(executor,
                                            partial(f, *args, **kwargs))
        return result
    except FunctionTimedOut:
        run_status['status'] = 'TIMEOUT'


async def start_delay(bot: Bot, guild: str, voiceffmpeg: dict, logger: Logger,
                      event_loop: AbstractEventLoop,
                      executor: ThreadPoolExecutor, playlist: dict,
                      duration: dict, playtime: dict, LOCK: dict,
                      channel: dict):
    try:
        run_status = {'status': 'RUNNING'}
        ensure_future(async_run_in_executor(delay_alignment,
                                            voiceffmpeg[guild],
                                            run_status,
                                            logger,
                                            loop=event_loop,
                                            executor=executor,
                                            run_status=run_status),
                      loop=event_loop)
        while run_status['status'] == 'RUNNING':
            await sleep(0.1)
        if run_status['status'] == 'TIMEOUT':
            logger.warning('RUN IN EXECUTOR TIMEOUT')
            raise FunctionTimedOut
    except FunctionTimedOut:
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        await bot.client.send(
            channel[guild],
            '发生错误，请重试',
        )
        return 'ERROR'


async def play_lyrics(guild: str, lrc_dict: dict, lrc_roma_dict: dict,
                      lrc_trans_dict: dict, enable_roma: bool,
                      enable_trans: bool, lyrics_broadid: str, config: dict,
                      botid: str, session: ClientSession, logger: Logger,
                      event_loop: AbstractEventLoop, duration: dict):
    now_time = 0.000
    new_now_time = 0.000
    while True:
        cm = CardMessage()
        c = Card(theme=Types.Theme.NONE)
        endflag = True
        new_now_time = 0.000

        for key in sorted(lrc_dict.keys()):
            s = ""
            if lrc_dict[key] == "":
                continue
            if key >= now_time and key < (now_time + 5.000):
                endflag = False
                if enable_roma:
                    try:
                        if lrc_roma_dict[key] != "":
                            s += "*" + lrc_roma_dict[key] + "*\n"
                    except:
                        s += "\n"
                s += "**" + lrc_dict[key] + "**\n"
                if enable_trans:
                    try:
                        if lrc_trans_dict[key] != "":
                            s += lrc_trans_dict[key] + "\n"
                    except:
                        s += "\n"
                s += "---"
                new_now_time = key
                c.append(Module.Section(Element.Text(s, Types.Text.KMD)))
            elif key >= (now_time + 5.000):
                endflag = False
                new_now_time = key
                break

        cm.append(c)
        ensure_future(uptmsg(lyrics_broadid, dumps(cm), config, botid, session,
                             logger),
                      loop=event_loop)
        if endflag:
            break
        if now_time == new_now_time:
            break
        await sleep(new_now_time - now_time)
        now_time = new_now_time
    await sleep(float(duration[guild]) - new_now_time)
    await delmsg(lyrics_broadid, config, botid, session, logger)
