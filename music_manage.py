from asyncio import AbstractEventLoop, CancelledError

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from json import dumps, loads
from logging import Logger
from re import compile, search
from subprocess import Popen
from time import localtime, strftime, time

from aiohttp import TCPConnector
from aiohttp.client import ClientSession, ClientTimeout
from khl.bot.bot import Bot
from khl.card import Card, CardMessage, Element, Module, Types
from pytube import YouTube
from status_manage import (bsearch, delmsg, get_netease_headers, get_playlist,
                           get_qq_headers, getAudio, getInformation, kill,
                           lrc_list_to_dict, parse_kmd_to_url, play_lyrics,
                           start_delay, start_play)


async def netease(guild: str, song_name: str, LOCK: dict, netease_cookie: str,
                  playlist: dict, duration: dict, deltatime: int, bot: Bot,
                  config: dict, playtime: dict, p: dict, botid: str,
                  port: dict, msgid: dict, channel: dict,
                  event_loop: AbstractEventLoop, voiceffmpeg: dict,
                  executor: ThreadPoolExecutor, logger: Logger):
    LOCK[guild] = True
    musicid = ""
    headers = get_netease_headers(netease_cookie)
    lyrics_broadid = ''
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        try:

            if playlist[guild][0]['time'] > int(round(time() * 1000)):
                song_name = song_name.split('-')[-1]
                musicid = song_name
            else:
                url = "http://127.0.0.1:3000/cloudsearch?keywords=" + song_name + "&limit=1"

                async with session.get(url=url,
                                       headers=headers,
                                       timeout=ClientTimeout(total=5)) as r:
                    response = await r.json()
                musicid = str(response['result']['songs'][0]['id'])

            url = 'http://127.0.0.1:3000/song/detail?ids=' + musicid
            async with session.get(url=url,
                                   headers=headers,
                                   timeout=ClientTimeout(total=5)) as r:
                response = (await r.json())['songs'][0]
            duration[guild] = int(response['dt'] / 1000) + deltatime
            song_name = response['name']
            playlist[guild][0]['display'] = song_name
            ban = compile('(惊雷)|(Lost Rivers)')
            resu = ban.findall(song_name)
            logger.warning(resu)
            if len(resu) > 0:

                playlist[guild].pop(0)
                await bot.client.send(
                    await bot.fetch_public_channel(channel[guild]),
                    '吃了吗，没吃吃我一拳',
                )
                duration[guild] = 0
                playtime[guild] = 0
                LOCK[guild] = False
                return
            song_url = 'https://music.163.com/#/song?id=' + str(response['id'])
            album_name = response['al']['name']
            if album_name == '':
                album_name = '无专辑'
            album_url = 'https://music.163.com/#/album?id=' + str(
                response['al']['id'])
            singer_name = response['ar'][0]['name']
            singer_url = 'https://music.163.com/#/artist?id=' + str(
                response['ar'][0]['id'])
            pic_url = response['al']['picUrl']
            getfile_url = 'http://127.0.0.1:3000/song/url?id=' + str(
                response['id']) + '&br=320000&timestamp=' + str(
                    int(round(time() * 1000)))

            async with session.get(url=getfile_url,
                                   headers=headers,
                                   timeout=ClientTimeout(total=5)) as r:
                urlresponse = (await r.json())['data'][0]['url']
            logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''

            if (urlresponse.startswith("http://m702") or
                    urlresponse.startswith("http://m802") or len(urlresponse)
                    == 0) and (not urlresponse.endswith(".flac")):
                getfile_url = 'http://127.0.0.1:3000/song/download/url?id=' + str(
                    response['id']) + '&br=320000&timestamp=' + str(
                        int(round(time() * 1000)))
                async with session.get(url=getfile_url,
                                       headers=headers,
                                       timeout=ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']['url']
                logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''

            if (urlresponse.startswith("http://m702") or
                    urlresponse.startswith("http://m802") or len(urlresponse)
                    == 0) and (not urlresponse.endswith(".flac")):
                getfile_url = 'http://127.0.0.1:3000/song/url?id=' + str(
                    response['id']) + '&br=320000'
                async with session.get(url=getfile_url,
                                       headers=headers,
                                       timeout=ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data'][0]['url']
                logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''

            if (urlresponse.startswith("http://m702") or
                    urlresponse.startswith("http://m802") or len(urlresponse)
                    == 0) and (not urlresponse.endswith(".flac")):
                getfile_url = 'http://127.0.0.1:3000/song/download/url?id=' + str(
                    response['id']) + '&br=320000'
                async with session.get(url=getfile_url,
                                       headers=headers,
                                       timeout=ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']['url']
                logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''

            playtime[guild] = 0
            if len(song_name) > 50:
                song_name = song_name[:50]
            await delmsg(msgid[guild], config, botid, session, logger)
            cm = CardMessage()
            c = get_playlist(guild, playlist)
            cm.append(c)
            c = Card(
                Module.Header("正在播放： " + song_name),
                Module.Context(
                    Element.Text(
                        "歌手： [" + singer_name + "](" + singer_url +
                        ")  —出自专辑 [" + album_name + "](" + album_url + ")",
                        Types.Text.KMD)),
                Module.File(Types.File.AUDIO,
                            src=urlresponse,
                            title=song_name,
                            cover=pic_url),
                Module.Countdown(datetime.now() +
                                 timedelta(seconds=duration[guild]),
                                 mode=Types.CountdownMode.SECOND),
                Module.Divider(),
                Module.Context(
                    Element.Image(
                        src=
                        "https://img.kookapp.cn/assets/2022-05/UmCnhm4mlt016016.png"
                    ),
                    Element.Text("网易云音乐  [在网页查看](" + song_url + ")",
                                 Types.Text.KMD)),
                Module.ActionGroup(
                    Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                    Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                    Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)),
                color="#6AC629")
            cm.append(c)
            msgid[guild] = (await
                            bot.client.send(channel[guild],
                                            cm))["msg_id"]  # type: ignore
            cm = CardMessage()
            c = Card(theme=Types.Theme.NONE)
            c.append(Module.Section("正在启动歌词板"))
            cm.append(c)
            LOCK[guild] = False
            lyrics_broadid = (await
                              bot.client.send(channel[guild],
                                              cm))["msg_id"]  # type: ignore
            playtime[guild] += deltatime
            if urlresponse.endswith("flac"):
                async with session.get(urlresponse,
                                       timeout=ClientTimeout(total=10)) as r:
                    with open(guild + "_" + botid + ".flac", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
                kill(guild, p, logger)
                p[guild] = Popen(
                    'ffmpeg -re -nostats -i "' + guild + "_" + botid +
                    '.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'
                    + port[guild],
                    shell=True)
            else:
                async with session.get(urlresponse,
                                       timeout=ClientTimeout(total=10)) as r:
                    with open(guild + "_" + botid + ".mp3", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
                kill(guild, p, logger)
                p[guild] = start_play(guild, port, botid)

        except Exception as e:
            playlist[guild].pop(0)
            duration[guild] = 0
            playtime[guild] = 0
            LOCK[guild] = False
            logger.warning(str(e))
            if str(e) == "'songs'":
                await bot.client.send(
                    channel[guild],
                    '未检索到此歌曲',
                )
            else:
                await bot.client.send(
                    channel[guild],
                    '发生错误，请重试',
                )
            return
        LOCK[guild] = False
        try:
            lrc_dict = {}
            lrc_trans_dict = {}
            lrc_roma_dict = {}
            enable_trans = False
            enable_roma = False
            lyrics_list = []
            lyrics_trans_list = []
            lyrics_roma_list = []
            lyrics_url = "http://127.0.0.1:3000/lyric?id=" + musicid
            async with session.get(url=lyrics_url,
                                   headers=headers,
                                   timeout=ClientTimeout(total=5)) as r:
                lyrics_list = (await
                               r.json())['lrc']['lyric'].strip().splitlines()
                try:
                    enable_trans = True
                    lyrics_trans_list = (
                        await
                        r.json())['tlyric']['lyric'].strip().splitlines()
                    assert lyrics_trans_list != []
                except:
                    enable_trans = False
                try:
                    enable_roma = True
                    lyrics_roma_list = (
                        await
                        r.json())['romalrc']['lyric'].strip().splitlines()
                    assert lyrics_roma_list != []
                except:
                    enable_roma = False
            lrc_list_to_dict(lyrics_list, lrc_dict, -0.5)
            if enable_trans:
                lrc_list_to_dict(lyrics_trans_list, lrc_trans_dict, -0.5)
            if enable_roma:
                lrc_list_to_dict(lyrics_roma_list, lrc_roma_dict, -0.5)
            logger.warning(lrc_dict)
            if (await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                                  executor, playlist, duration, playtime, LOCK,
                                  channel)) == 'ERROR':
                return
            await play_lyrics(guild, lrc_dict, lrc_roma_dict, lrc_trans_dict,
                              enable_roma, enable_trans, lyrics_broadid,
                              config, botid, session, logger, event_loop,
                              duration)
        except Exception as e:
            logger.warning(str(e))
            logger.warning("!!!!")
            await bot.client.send(
                channel[guild],
                '歌词板获取错误',
            )
            await delmsg(lyrics_broadid, config, botid, session, logger)
        except CancelledError:
            await delmsg(lyrics_broadid, config, botid, session, logger)
            logger.warning('cancel task')
            raise
        return


async def bili(guild: str, song_name: str, LOCK: dict, bili_cookie: str,
               playlist: dict, duration: dict, deltatime: int, bot: Bot,
               config: dict, playtime: dict, p: dict, botid: str, port: dict,
               msgid: dict, channel: dict, voiceffmpeg: dict,
               event_loop: AbstractEventLoop, executor: ThreadPoolExecutor,
               logger: Logger):
    LOCK[guild] = True
    try:
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            try:
                pattern = r'BV\w{10}(\?p=[0-9]+)*'
                tmp = search(pattern, song_name)
                assert tmp is not None
                song_name = tmp.group()
            except:
                song_name = (await
                             bsearch(song_name, bili_cookie,
                                     session))['data']['result'][0]['bvid']
            item = await getInformation(duration, deltatime, song_name, guild,
                                        session, logger)
            bvid, cid, title, mid, name, pic = await getAudio(
                guild, item, botid, session)
            logger.warning(duration[guild])
            ban = compile('(惊雷)|(Lost Rivers)')
            resu = ban.findall(title)
            if len(resu) > 0:
                playlist[guild].pop(0)
                await bot.client.send(
                    channel[guild],
                    '吃了吗，没吃吃我一拳',
                )
                duration[guild] = 0
                playtime[guild] = 0
                LOCK[guild] = False
                return
            playtime[guild] = 0
            kill(guild, p, logger)
            p[guild] = start_play(guild, port, botid)
            if (await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                                  executor, playlist, duration, playtime, LOCK,
                                  channel)) == 'ERROR':
                return
            playlist[guild][0]['display'] = title
            await delmsg(msgid[guild], config, botid, session, logger)
            cm = CardMessage()
            c = get_playlist(guild, playlist)
            cm.append(c)
            c = Card(Module.Context(
                Element.Text(
                    "**标题:        [" + title +
                    "](https://www.bilibili.com/video/" + song_name + "/)**",
                    Types.Text.KMD)),
                     Module.Context(
                         Element.Text(
                             "UP:         [" + name +
                             "](https://space.bilibili.com/" + mid + "/)",
                             Types.Text.KMD)),
                     Module.Container(Element.Image(src=pic)),
                     Module.Countdown(datetime.now() +
                                      timedelta(seconds=duration[guild]),
                                      mode=Types.CountdownMode.SECOND),
                     Module.ActionGroup(
                         Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                         Element.Button('清空歌单', 'CLEAR',
                                        Types.Click.RETURN_VAL),
                         Element.Button('循环模式', 'LOOP',
                                        Types.Click.RETURN_VAL)),
                     color="#6AC629")
            cm.append(c)
            msgid[guild] = (await
                            bot.client.send(channel[guild],
                                            cm))["msg_id"]  # type: ignore
            playtime[guild] += deltatime
    except Exception as e:
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        logger.warning(str(e))
        if str(e) == "'data'" or str(e) == "'result'":
            await bot.client.send(
                channel[guild],
                '未检索到此歌曲',
            )
        elif str(e) == "'NoneType' object has no attribute 'group'":
            await bot.client.send(
                channel[guild],
                'BV号或链接输入有误',
            )
        else:
            await bot.client.send(
                channel[guild],
                '发生错误，请重试（本视频可能需要填写b_cookie）',
            )
        return
    LOCK[guild] = False
    return


async def neteaseradio(guild: str, song_name: str, LOCK: dict,
                       netease_cookie: str, playlist: dict, duration: dict,
                       deltatime: int, bot: Bot, config: dict, playtime: dict,
                       p: dict, botid: str, port: dict, msgid: dict,
                       channel: dict, voiceffmpeg: dict,
                       event_loop: AbstractEventLoop,
                       executor: ThreadPoolExecutor, logger: Logger):
    LOCK[guild] = True
    try:
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            headers = get_netease_headers(netease_cookie)
            song_name = song_name.replace(" ", "")
            song_name = song_name.split('-')[-1]
            logger.warning(song_name)
            url = 'http://127.0.0.1:3000/dj/program/detail?id=' + song_name

            async with session.get(url=url,
                                   headers=headers,
                                   timeout=ClientTimeout(total=5)) as r:
                response = await r.json()
            logger.warning(response['code'])
            if response['code'] == 404 or response['code'] == 400:
                await bot.client.send(
                    channel[guild],
                    '未检索到此歌曲',
                )
                playlist[guild].pop(0)
                duration[guild] = 0
                playtime[guild] = 0
                LOCK[guild] = False
                return
            response = response['program']
            duration[guild] = int(response['duration'] / 1000) + deltatime
            song_url = 'https://music.163.com/#/program?id=' + song_name
            song_name = response['mainSong']['name']
            playlist[guild][0]['display'] = song_name
            ban = compile('(惊雷)|(Lost Rivers)')
            resu = ban.findall(song_name)
            logger.warning(resu)
            if len(resu) > 0:
                playlist[guild].pop(0)
                await bot.client.send(
                    channel[guild],
                    '吃了吗，没吃吃我一拳',
                )
                duration[guild] = 0
                playtime[guild] = 0
                LOCK[guild] = False
                return

            album_name = response['radio']['name']
            if album_name == '':
                album_name = '无专辑'
            album_url = 'https://music.163.com/#/djradio?id=' + str(
                response['radio']['id'])

            singer_name = response['dj']['nickname']
            singer_url = 'https://music.163.com/#/user/home?id=' + str(
                response['dj']['userId'])
            pic_url = response['radio']['picUrl']
            getfile_url = 'http://127.0.0.1:3000/song/url?id=' + str(
                response['mainSong']['id']) + '&br=320000'
            async with session.get(url=getfile_url,
                                   headers=headers,
                                   timeout=ClientTimeout(total=5)) as r:
                urlresponse = (await r.json())['data'][0]['url']
            logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''
            if (urlresponse.startswith("http://m702") or
                    urlresponse.startswith("http://m802") or len(urlresponse)
                    == 0) and not urlresponse.endswith(".flac"):
                getfile_url = 'http://127.0.0.1:3000/song/download/url?id=' + str(
                    response['mainSong']['id']) + '&br=320000'
                async with session.get(url=getfile_url,
                                       headers=headers,
                                       timeout=ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']['url']
                logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''

            if (urlresponse.startswith("http://m702") or
                    urlresponse.startswith("http://m802") or len(urlresponse)
                    == 0) and not urlresponse.endswith(".flac"):
                getfile_url = 'http://127.0.0.1:3000/song/url?id=' + str(
                    response['mainSong']['id']) + '&br=320000'
                async with session.get(url=getfile_url,
                                       headers=headers,
                                       timeout=ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data'][0]['url']
                logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''

            if (urlresponse.startswith("http://m702") or
                    urlresponse.startswith("http://m802") or len(urlresponse)
                    == 0) and not urlresponse.endswith(".flac"):
                getfile_url = 'http://127.0.0.1:3000/song/download/url?id=' + str(
                    response['mainSong']['id']) + '&br=320000'
                async with session.get(url=getfile_url,
                                       headers=headers,
                                       timeout=ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']['url']
                logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''
            if (urlresponse.startswith("http://m702") or
                    urlresponse.startswith("http://m802") or len(urlresponse)
                    == 0) and not urlresponse.endswith(".flac"):
                getfile_url = 'http://127.0.0.1:3000/song/url?id=' + str(
                    response['mainSong']['id']) + '?timestamp='
                async with session.get(url=getfile_url,
                                       headers=headers,
                                       timeout=ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data'][0]['url']
                logger.warning(urlresponse)
            if urlresponse is None:
                urlresponse = ''
            if urlresponse.endswith("flac"):

                async with session.get(urlresponse,
                                       timeout=ClientTimeout(total=10)) as r:
                    with open(guild + ".flac", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
                kill(guild, p, logger)
                p[guild] = Popen(
                    'ffmpeg -re -nostats -i "' + guild +
                    '.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'
                    + port[guild],
                    shell=True)

            else:
                async with session.get(urlresponse,
                                       timeout=ClientTimeout(total=10)) as r:
                    with open(guild + "_" + botid + ".mp3", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
                kill(guild, p, logger)
                p[guild] = start_play(guild, port, botid)
            playtime[guild] = 0

            await delmsg(msgid[guild], config, botid, session, logger)
            if (await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                                  executor, playlist, duration, playtime, LOCK,
                                  channel)) == 'ERROR':
                return
            cm = CardMessage()
            c = get_playlist(guild, playlist)
            cm.append(c)
            c = Card(
                Module.Header("正在播放： " + song_name),
                Module.Context(
                    Element.Text(
                        "歌手： [" + singer_name + "](" + singer_url +
                        ")  —出自专辑 [" + album_name + "](" + album_url + ")",
                        Types.Text.KMD)),
                Module.File(Types.File.AUDIO,
                            src=urlresponse,
                            title=song_name,
                            cover=pic_url),
                Module.Countdown(datetime.now() +
                                 timedelta(seconds=duration[guild]),
                                 mode=Types.CountdownMode.SECOND),
                Module.Divider(),
                Module.Context(
                    Element.Image(
                        src=
                        "https://img.kookapp.cn/assets/2022-05/UmCnhm4mlt016016.png"
                    ),
                    Element.Text("网易云音乐  [在网页查看](" + song_url + ")",
                                 Types.Text.KMD)),
                Module.ActionGroup(
                    Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                    Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                    Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)),
                color="#6AC629")
            cm.append(c)
            logger.warning(dumps(cm))
            msgid[guild] = (await
                            bot.client.send(channel[guild],
                                            cm))["msg_id"]  # type: ignore
            playtime[guild] += deltatime
    except Exception as e:
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        logger.warning(str(e))
        await bot.client.send(
            channel[guild],
            '发生错误，请重试',
        )
        return
    LOCK[guild] = False
    return


async def qqmusic(guild: str, song_name: str, LOCK: dict, playlist: dict,
                  duration: dict, deltatime: int, bot: Bot, config: dict,
                  playtime: dict, p: dict, botid: str, port: dict, msgid: dict,
                  channel: dict, qq_cookie: str, voiceffmpeg: dict,
                  event_loop: AbstractEventLoop, executor: ThreadPoolExecutor,
                  logger: Logger):
    LOCK[guild] = True
    lyrics_broadid = ''
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        try:

            if playlist[guild][0]['time'] > int(round(time() * 1000)):
                song_name = song_name.split('-')[-1]
                musicid = song_name
            else:
                url = "http://127.0.0.1:3300/search/quick?key=" + song_name

                async with session.get(url=url,
                                       timeout=ClientTimeout(total=5)) as r:
                    response = (await r.json())['data']['song']['itemlist'][0]
                musicid = response['mid']

            url = "http://127.0.0.1:3300/song?songmid=" + musicid
            async with session.get(url=url,
                                   timeout=ClientTimeout(total=5)) as r:
                response = (await r.json())['data']['track_info']
            song_name = response['name']
            playlist[guild][0]['display'] = song_name
            duration[guild] = response['interval'] + deltatime
            song_url = 'https://y.qq.com/n/ryqq/songDetail/' + response['mid']
            album_name = response['album']['name']
            if album_name == '':
                album_name = '无专辑'
            album_url = 'https://y.qq.com/n/ryqq/albumDetail/' + response[
                'album']['mid']
            singer_name = response['singer'][0]['name']
            singer_url = 'https://y.qq.com/n/ryqq/singer/' + response[
                'singer'][0]['mid']
            pic_url = 'https://y.gtimg.cn/music/photo_new/T002R300x300M000' + response[
                'album']['mid'] + '.jpg'
            getfile_url = 'http://127.0.0.1:3300/song/url?id=' + response[
                'mid'] + '&mediaId=' + response['file'][
                    'media_mid'] + '&ownCookie=1'
            ban = compile('(惊雷)|(Lost Rivers)')
            resu = ban.findall(song_name)
            if len(resu) > 0:
                playlist[guild].pop(0)
                await bot.client.send(
                    channel[guild],
                    '吃了吗，没吃吃我一拳',
                )
                duration[guild] = 0
                playtime[guild] = 0
                LOCK[guild] = False
                return
            try:
                async with session.get(url=getfile_url,
                                       timeout=ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']
            except:
                await bot.client.send(
                    channel[guild],
                    'api cookie失效',
                )
                playlist[guild].pop(0)
                duration[guild] = 0
                playtime[guild] = 0
                LOCK[guild] = False
                return
            headers = get_qq_headers(qq_cookie)
            async with session.get(url=urlresponse,
                                   headers=headers,
                                   timeout=ClientTimeout(total=10)) as r:
                with open(guild + "_" + botid + ".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)

            playtime[guild] = 0
            kill(guild, p, logger)

            p[guild] = start_play(guild, port, botid)
            await delmsg(msgid[guild], config, botid, session, logger)
            if (await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                                  executor, playlist, duration, playtime, LOCK,
                                  channel)) == 'ERROR':
                return
            cm = CardMessage()
            c = get_playlist(guild, playlist)
            cm.append(c)
            c = Card(
                Module.Header("正在播放： " + song_name),
                Module.Context(
                    Element.Text(
                        "歌手： [" + singer_name + "](" + singer_url +
                        ")  —出自专辑 [" + album_name + "](" + album_url + ")",
                        Types.Text.KMD)),
                Module.File(Types.File.AUDIO,
                            src=urlresponse,
                            title=song_name,
                            cover=pic_url),
                Module.Countdown(datetime.now() +
                                 timedelta(seconds=duration[guild]),
                                 mode=Types.CountdownMode.SECOND),
                Module.Divider(),
                Module.Context(
                    Element.Image(
                        src=
                        "https://img.kookapp.cn/assets/2022-06/cqzmClO3Sq07s07x.png"
                    ),
                    Element.Text("QQ音乐  [在网页查看](" + song_url + ")",
                                 Types.Text.KMD)),
                Module.ActionGroup(
                    Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                    Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                    Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)),
                color="#6AC629")
            cm.append(c)
            msgid[guild] = (await
                            bot.client.send(channel[guild],
                                            cm))["msg_id"]  # type: ignore
            cm = CardMessage()
            c = Card(theme=Types.Theme.NONE)
            c.append(Module.Section("正在启动歌词板"))
            cm.append(c)
            LOCK[guild] = False
            lyrics_broadid = (await
                              bot.client.send(channel[guild],
                                              cm))["msg_id"]  # type: ignore
            playtime[guild] += deltatime
        except Exception as e:
            playlist[guild].pop(0)
            duration[guild] = 0
            playtime[guild] = 0
            LOCK[guild] = False
            logger.warning(str(e))
            if str(e) == "list index out of range":
                await bot.client.send(
                    channel[guild],
                    '未检索到此歌曲',
                )
            else:
                await bot.client.send(
                    channel[guild],
                    '发生错误，请重试',
                )
            return
        LOCK[guild] = False
        try:
            lrc_dict = {}
            lrc_trans_dict = {}
            lrc_roma_dict = {}
            enable_trans = False
            enable_roma = False
            lyrics_list = []
            lyrics_trans_list = []
            lyrics_url = "http://127.0.0.1:3300/lyric?songmid=" + musicid
            async with session.get(url=lyrics_url,
                                   headers=headers,
                                   timeout=ClientTimeout(total=5)) as r:
                lyrics_list = (await
                               r.json())['data']['lyric'].strip().splitlines()
                try:
                    enable_trans = True
                    lyrics_trans_list = (
                        await r.json())['data']['trans'].strip().splitlines()
                    assert lyrics_trans_list != []
                except:
                    enable_trans = False
            lrc_list_to_dict(lyrics_list, lrc_dict, -1.5)
            if enable_trans:
                lrc_list_to_dict(lyrics_trans_list, lrc_trans_dict, -1.5)
            logger.warning(lrc_dict)
            await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                              executor, playlist, duration, playtime, LOCK,
                              channel)
            await play_lyrics(guild, lrc_dict, lrc_roma_dict, lrc_trans_dict,
                              enable_roma, enable_trans, lyrics_broadid,
                              config, botid, session, logger, event_loop,
                              duration)
        except Exception as e:
            logger.warning(str(e))
            logger.warning("!!!!")
            await bot.client.send(
                channel[guild],
                '歌词板获取错误',
            )
            await delmsg(lyrics_broadid, config, botid, session, logger)
        except CancelledError:
            await delmsg(lyrics_broadid, config, botid, session, logger)
            logger.warning('cancel task')
            raise
        return


async def migu(guild: str, song_name: str, LOCK: dict, playlist: dict,
               duration: dict, deltatime: int, bot: Bot, config: dict,
               playtime: dict, p: dict, botid: str, port: dict, msgid: dict,
               channel: dict, voiceffmpeg: dict, event_loop: AbstractEventLoop,
               executor: ThreadPoolExecutor, logger: Logger):
    LOCK[guild] = True
    try:
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            if playlist[guild][0]['time'] > int(round(time() * 1000)):
                song_name = song_name.split('-')[-1]
                musicid = song_name
            else:

                url = "http://127.0.0.1:3400/song/find?keyword=" + song_name
                async with session.get(url=url,
                                       timeout=ClientTimeout(total=5)) as r:
                    response = await r.json()
                musicid = str(response['data']['cid'])

            url = 'http://127.0.0.1:3400/song?cid=' + musicid
            async with session.get(url=url,
                                   timeout=ClientTimeout(total=5)) as r:
                response = (await r.json())["data"]
            duration[guild] = response["duration"] + deltatime
            song_name = response["name"]
            playlist[guild][0]['display'] = song_name
            ban = compile('(惊雷)|(Lost Rivers)')
            resu = ban.findall(song_name)
            logger.warning(resu)
            if len(resu) > 0:

                playlist[guild].pop(0)
                await bot.client.send(
                    await bot.fetch_public_channel(channel[guild]),
                    '吃了吗，没吃吃我一拳',
                )
                duration[guild] = 0
                playtime[guild] = 0
                LOCK[guild] = False
                return

            song_url = 'https://music.migu.cn/v3/music/song/' + response['cid']
            album_name = response['album']['name']
            if album_name == '':
                album_name = '无专辑'
            album_url = 'https://music.migu.cn/v3/music/album/' + response[
                'album']['id']
            singer_name = response['artists'][0]['name']
            singer_url = 'https://music.migu.cn/v3/music/artist/' + response[
                'artists'][0]['id']
            pic_url = response["picUrl"]

            urlresponse = response["320"]

            async with session.get(urlresponse,
                                   timeout=ClientTimeout(total=10)) as r:
                with open(guild + "_" + botid + ".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)
            kill(guild, p, logger)
            p[guild] = start_play(guild, port, botid)
            playtime[guild] = 0
            if len(song_name) > 50:
                song_name = song_name[:50]
            await delmsg(msgid[guild], config, botid, session, logger)
            if (await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                                  executor, playlist, duration, playtime, LOCK,
                                  channel)) == 'ERROR':
                return
            cm = CardMessage()
            c = get_playlist(guild, playlist)
            cm.append(c)
            c = Card(
                Module.Header("正在播放： " + song_name),
                Module.Context(
                    Element.Text(
                        "歌手： [" + singer_name + "](" + singer_url +
                        ")  —出自专辑 [" + album_name + "](" + album_url + ")",
                        Types.Text.KMD)),
                Module.File(Types.File.AUDIO,
                            src=urlresponse,
                            title=song_name,
                            cover=pic_url),
                Module.Countdown(datetime.now() +
                                 timedelta(seconds=duration[guild]),
                                 mode=Types.CountdownMode.SECOND),
                Module.Divider(),
                Module.Context(
                    Element.Image(
                        src=
                        "https://img.kookapp.cn/assets/2022-07/dhSP597xJ502s02r.png"
                    ),
                    Element.Text("咪咕音乐  [在网页查看](" + song_url + ")",
                                 Types.Text.KMD)),
                Module.ActionGroup(
                    Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                    Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                    Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)),
                color="#6AC629")
            cm.append(c)
            msgid[guild] = (await
                            bot.client.send(channel[guild],
                                            cm))["msg_id"]  # type: ignore
            playtime[guild] += deltatime
    except Exception as e:
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        logger.warning(str(e))
        if str(e) == "'songs'":
            await bot.client.send(
                channel[guild],
                '未检索到此歌曲',
            )
        else:
            await bot.client.send(
                channel[guild],
                '发生错误，正在重试',
            )
        return
    LOCK[guild] = False
    return


async def kmusic(guild: str, song_name: str, LOCK: dict, playlist: dict,
                 duration: dict, deltatime: int, bot: Bot, config: dict,
                 playtime: dict, p: dict, botid: str, port: dict, msgid: dict,
                 channel: dict, voiceffmpeg: dict,
                 event_loop: AbstractEventLoop, executor: ThreadPoolExecutor,
                 logger: Logger):
    LOCK[guild] = True
    try:
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            song_name = parse_kmd_to_url(song_name)

            async with session.get(url=song_name,
                                   timeout=ClientTimeout(total=5)) as r:
                response = await r.text()

            pattern = r'(?<=window.__DATA__ = ).*?(?=; </script>)'
            tmp = search(pattern, response)
            assert tmp is not None
            response = loads(tmp.group())
            song_name = response['detail']['song_name']

            song_url = 'https://node.kg.qq.com/play?s=' + response['shareid']

            singer_name = response['detail']['nick']
            singer_url = 'https://node.kg.qq.com/personal?uid=' + response[
                'detail']['uid']
            pic_url = response['detail']['cover']
            urlresponse = response['detail']['playurl']
            ban = compile('(惊雷)|(Lost Rivers)')
            resu = ban.findall(song_name)
            if len(resu) > 0:
                playlist[guild].pop(0)
                await bot.client.send(
                    channel[guild],
                    '吃了吗，没吃吃我一拳',
                )
                duration[guild] = 0
                playtime[guild] = 0
                LOCK[guild] = False
                return
            if response['detail']['segment_end'] != 0:
                duration[guild] = int(
                    response['detail']['segment_end'] / 1000) + deltatime
            else:
                tmp = search(r'(?<=songmid=)[0-9|a-z|A-Z]+',
                             response['songinfo']['data']['song_url'])
                assert tmp is not None
                url = "http://127.0.0.1:3300/song?songmid=" + tmp.group()
                async with session.get(url=url,
                                       timeout=ClientTimeout(total=5)) as r:
                    response = (await r.json())['data']['track_info']
                duration[guild] = response['interval'] + deltatime
            async with session.get(urlresponse,
                                   timeout=ClientTimeout(total=10)) as r:
                with open(guild + "_" + botid + ".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)

            playtime[guild] = 0
            kill(guild, p, logger)

            p[guild] = start_play(guild, port, botid)
            playlist[guild][0]['display'] = song_name
            await delmsg(msgid[guild], config, botid, session, logger)
            if (await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                                  executor, playlist, duration, playtime, LOCK,
                                  channel)) == 'ERROR':
                return
            cm = CardMessage()
            c = get_playlist(guild, playlist)
            cm.append(c)
            c = Card(
                Module.Header("正在播放： " + song_name),
                Module.Context(
                    Element.Text(
                        "歌手： [" + singer_name + "](" + singer_url + ")",
                        Types.Text.KMD)),
                Module.File(Types.File.AUDIO,
                            src=urlresponse,
                            title=song_name,
                            cover=pic_url),
                Module.Countdown(datetime.now() +
                                 timedelta(seconds=duration[guild]),
                                 mode=Types.CountdownMode.SECOND),
                Module.Divider(),
                Module.Context(
                    Element.Image(
                        src=
                        "https://img.kookapp.cn/assets/2022-07/BP8vZb06hs0a409n.png"
                    ),
                    Element.Text("全民K歌  [在网页查看](" + song_url + ")",
                                 Types.Text.KMD)),
                Module.ActionGroup(
                    Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                    Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                    Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)),
                color="#6AC629")
            cm.append(c)
            msgid[guild] = (await
                            bot.client.send(channel[guild],
                                            cm))["msg_id"]  # type: ignore
            playtime[guild] += deltatime
    except Exception as e:
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        logger.warning(str(e))
        if str(e) == "'songs'":
            await bot.client.send(
                channel[guild],
                '未检索到此歌曲',
            )
        else:
            await bot.client.send(
                channel[guild],
                '发生错误，正在重试',
            )
        return
    LOCK[guild] = False
    return


async def get_result(link: str, event_loop: AbstractEventLoop,
                     executor: ThreadPoolExecutor) -> YouTube:
    return await event_loop.run_in_executor(executor, YouTube, link)


async def download(result: YouTube, guild: str, event_loop: AbstractEventLoop,
                   executor: ThreadPoolExecutor, botid: str):
    tmp = await event_loop.run_in_executor(executor,
                                           result.streams.get_by_itag, 251)
    assert tmp is not None
    await event_loop.run_in_executor(executor, tmp.download, '.',
                                     guild + "_" + botid + ".mp3")


async def ytb(guild: str, song_name: str, LOCK: dict, playlist: dict,
              duration: dict, deltatime: int, bot: Bot, config: dict,
              playtime: dict, p: dict, botid: str, port: dict, msgid: dict,
              channel: dict, event_loop: AbstractEventLoop,
              executor: ThreadPoolExecutor, voiceffmpeg: dict, logger: Logger):

    LOCK[guild] = True
    try:
        song_name = parse_kmd_to_url(song_name)
        result = await get_result(song_name, event_loop, executor)
        title = result.title.replace("[", "【").replace("]", "】")
        playlist[guild][0]['display'] = title
        name = result.author
        duration[guild] = result.length
        playtime[guild] = 0
        await download(result, guild, event_loop, executor, botid)
        kill(guild, p, logger)
        p[guild] = start_play(guild, port, botid)
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            await delmsg(msgid[guild], config, botid, session, logger)
        if (await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                              executor, playlist, duration, playtime, LOCK,
                              channel)) == 'ERROR':
            return
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(Module.Context(
            Element.Text("**标题:        [" + title + "](" + song_name + ")**",
                         Types.Text.KMD)),
                 Module.Context(
                     Element.Text("UP:         " + name, Types.Text.KMD)),
                 Module.Countdown(datetime.now() +
                                  timedelta(seconds=duration[guild]),
                                  mode=Types.CountdownMode.SECOND),
                 Module.ActionGroup(
                     Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                     Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                     Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)),
                 color="#6AC629")
        cm.append(c)
        msgid[guild] = (await bot.client.send(channel[guild],
                                              cm))["msg_id"]  # type: ignore
        playtime[guild] += deltatime
    except Exception as e:
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        logger.warning(str(e))
        if 'is unavailable' in str(e):
            await bot.client.send(
                channel[guild],
                '未检索到此视频',
            )
        elif str(
                e
        ) == r"regex_search: could not find match for (?:v=|\/)([0-9A-Za-z_-]{11}).*":
            await bot.client.send(
                channel[guild],
                '链接输入有误',
            )
        else:
            await bot.client.send(
                channel[guild],
                '发生错误，正在重试',
            )
        return
    LOCK[guild] = False
    return


async def fm(guild: str, song_name: str, LOCK: dict, playlist: dict,
             duration: dict, deltatime: int, bot: Bot, config: dict,
             playtime: dict, p: dict, botid: str, port: dict, msgid: dict,
             channel: dict, voiceffmpeg: dict, event_loop: AbstractEventLoop,
             executor: ThreadPoolExecutor, logger: Logger):
    LOCK[guild] = True
    try:
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            song_name = parse_kmd_to_url(song_name)
            tmp = search(r'(?<=/radios/)[0-9]+', song_name)
            assert tmp is not None
            broadcastid = tmp.group()
            url = 'https://webapi.qtfm.cn/api/pc/radio/' + broadcastid

            async with session.get(url=url,
                                   timeout=ClientTimeout(total=5)) as r:
                response = await r.json()
            title = response['album']['title'] + '-' + response['album'][
                'nowplaying']['title']
            description = response['album']['description']
            now = datetime.strptime(strftime("%H:%M:%S", localtime()),
                                    '%H:%M:%S')
            end = datetime.strptime(
                response['album']['nowplaying']['end_time'], '%H:%M:%S')
            duration[guild] = (end - now).seconds
            playtime[guild] = 0
            kill(guild, p, logger)
            p[guild] = Popen(
                'ffmpeg -re -nostats -i "https://lhttp.qingting.fm/live/' +
                broadcastid +
                '/64k.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'
                + port[guild],
                shell=True)
            await delmsg(msgid[guild], config, botid, session, logger)
            if (await start_delay(bot, guild, voiceffmpeg, logger, event_loop,
                                  executor, playlist, duration, playtime, LOCK,
                                  channel)) == 'ERROR':
                return
            playlist[guild][0]['display'] = title
            cm = CardMessage()
            c = get_playlist(guild, playlist)
            cm.append(c)
            c = Card(Module.Header("正在播放： " + title),
                     Module.Context(Element.Text(description, Types.Text.KMD)),
                     Module.Countdown(datetime.now() +
                                      timedelta(seconds=duration[guild]),
                                      mode=Types.CountdownMode.SECOND),
                     Module.Divider(),
                     Module.ActionGroup(
                         Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                         Element.Button('清空歌单', 'CLEAR',
                                        Types.Click.RETURN_VAL),
                         Element.Button('循环模式', 'LOOP',
                                        Types.Click.RETURN_VAL)),
                     color="#6AC629")
            cm.append(c)
            msgid[guild] = (await
                            bot.client.send(channel[guild],
                                            cm))["msg_id"]  # type: ignore
            playtime[guild] += deltatime
    except Exception as e:
        logger.warning(str(e))
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        await bot.client.send(
            channel[guild],
            '发生错误，正在重试',
        )
        return
    LOCK[guild] = False
    return
