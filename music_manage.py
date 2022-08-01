import time
import aiohttp
import subprocess
import re
import json
from datetime import datetime, timedelta
from status_manage import kill, delmsg, start_play, get_playlist, parse_kmd_to_url, getAudio, getInformation
from khl import Bot, Event, EventTypes, Message, api
from khl.card import Card, CardMessage, Element, Module, Struct, Types
from pytube import YouTube
from aiohttp import TCPConnector


async def netease(guild, song_name, LOCK, netease_cookie, playlist, duration,
                  deltatime, bot, config, playtime, p, botid, port, msgid,
                  channel):
    LOCK[guild] = True
    try:
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
        if playlist[guild][0]['time'] > int(round(time.time() * 1000)):
            song_name = song_name.split('-')[-1]
            musicid = song_name
        else:
            url = "http://127.0.0.1:3000/cloudsearch?keywords=" + song_name + "&limit=1"
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    response = await r.json()
            musicid = str(response['result']['songs'][0]['id'])

        url = 'http://127.0.0.1:3000/song/detail?ids=' + musicid
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    url=url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)) as r:
                response = (await r.json())['songs'][0]
        duration[guild] = int(response['dt'] / 1000) + deltatime
        song_name = response['name']
        playlist[guild][0]['display'] = song_name
        ban = re.compile('(惊雷)|(Lost Rivers)')
        resu = ban.findall(song_name)
        print(resu)
        if len(resu) > 0:

            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(config["channel"]),
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
                int(round(time.time() * 1000)))

        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    url=getfile_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)) as r:
                urlresponse = (await r.json())['data'][0]['url']
        print(urlresponse)
        if urlresponse is None:
            urlresponse = ''

        if (urlresponse.startswith("http://m702")
                or urlresponse.startswith("http://m802") or len(urlresponse)
                == 0) and (not urlresponse.endswith(".flac")):
            getfile_url = 'http://127.0.0.1:3000/song/download/url?id=' + str(
                response['id']) + '&br=320000&timestamp=' + str(
                    int(round(time.time() * 1000)))
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=getfile_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']['url']
            print(urlresponse)
        if urlresponse is None:
            urlresponse = ''

        if (urlresponse.startswith("http://m702")
                or urlresponse.startswith("http://m802") or len(urlresponse)
                == 0) and (not urlresponse.endswith(".flac")):
            getfile_url = 'http://127.0.0.1:3000/song/url?id=' + str(
                response['id']) + '&br=320000'
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=getfile_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data'][0]['url']
            print(urlresponse)
        if urlresponse is None:
            urlresponse = ''

        if (urlresponse.startswith("http://m702")
                or urlresponse.startswith("http://m802") or len(urlresponse)
                == 0) and (not urlresponse.endswith(".flac")):
            getfile_url = 'http://127.0.0.1:3000/song/download/url?id=' + str(
                response['id']) + '&br=320000'
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=getfile_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']['url']
            print(urlresponse)
        if urlresponse is None:
            urlresponse = ''

        if urlresponse.endswith("flac"):
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        urlresponse,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    with open(guild + "_" + botid + ".flac", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild, p)
            p[guild] = subprocess.Popen(
                'ffmpeg -re -nostats -i "' + guild + "_" + botid +
                '.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'
                + port[guild],
                shell=True)
        else:
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        urlresponse,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    with open(guild + "_" + botid + ".mp3", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild, p)
            p[guild] = start_play(guild, port, botid)
        playtime[guild] = 0
        if len(song_name) > 50:
            song_name = song_name[:50]
        await delmsg(msgid[guild], config, botid)
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(
            Module.Header("正在播放： " + song_name),
            Module.Context(
                Element.Text(
                    "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" +
                    album_name + "](" + album_url + ")", Types.Text.KMD)),
            Module.File(Types.File.AUDIO,
                        src=urlresponse,
                        title=song_name,
                        cover=pic_url),
            Module.Countdown(
                datetime.now() + timedelta(seconds=duration[guild]),
                mode=Types.CountdownMode.SECOND), Module.Divider(),
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
                Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)))
        cm.append(c)
        msgid[guild] = (await bot.send(
            await bot.fetch_public_channel(channel[guild]), cm))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e) == "'songs'":
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '未检索到此歌曲',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '发生错误，请重试',
            )
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        return
    LOCK[guild] = False
    return


async def bili(guild, song_name, LOCK, playlist, duration, deltatime, bot,
               config, playtime, p, botid, port, msgid, channel):
    LOCK[guild] = True
    try:
        pattern = r'BV\w{10}(\?p=[0-9]+)*'
        song_name = re.search(pattern, song_name).group()
        guild, item = await getInformation(duration, deltatime, song_name,
                                           guild)
        bvid, cid, title, mid, name, pic = await getAudio(guild, item, botid)
        print(duration[guild])
        ban = re.compile('(惊雷)|(Lost Rivers)')
        resu = ban.findall(title)
        if len(resu) > 0:
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '吃了吗，没吃吃我一拳',
            )
            duration[guild] = 0
            playtime[guild] = 0
            LOCK[guild] = False
            return
        playtime[guild] = 0
        kill(guild, p)
        p[guild] = start_play(guild, port, botid)
        playlist[guild][0]['display'] = title
        await delmsg(msgid[guild], config, botid)
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(
            Module.Context(
                Element.Text(
                    "**标题:        [" + title +
                    "](https://www.bilibili.com/video/" + song_name + "/)**",
                    Types.Text.KMD)),
            Module.Context(
                Element.Text(
                    "UP:         [" + name + "](https://space.bilibili.com/" +
                    mid + "/)", Types.Text.KMD)),
            Module.Container(Element.Image(src=pic)),
            Module.Countdown(datetime.now() +
                             timedelta(seconds=duration[guild]),
                             mode=Types.CountdownMode.SECOND),
            Module.ActionGroup(
                Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)))
        cm.append(c)
        msgid[guild] = (await bot.send(
            await bot.fetch_public_channel(channel[guild]), cm))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e) == "'data'":
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '未检索到此歌曲',
            )
        elif str(e) == "'NoneType' object has no attribute 'group'":
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                'BV号或链接输入有误',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '发生错误，请重试',
            )
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        return
    LOCK[guild] = False
    return


async def neteaseradio(guild, song_name, LOCK, netease_cookie, playlist,
                       duration, deltatime, bot, config, playtime, p, botid,
                       port, msgid, channel):
    LOCK[guild] = True
    try:
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
        song_name = song_name.replace(" ", "")
        song_name = song_name.split('-')[-1]
        print(song_name)
        url = 'http://127.0.0.1:3000/dj/program/detail?id=' + song_name
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    url=url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)) as r:
                response = await r.json()
        print(response['code'])
        if response['code'] == 404 or response['code'] == 400:
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
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
        ban = re.compile('(惊雷)|(Lost Rivers)')
        resu = ban.findall(song_name)
        print(resu)
        if len(resu) > 0:
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
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
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    url=getfile_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)) as r:
                urlresponse = (await r.json())['data'][0]['url']
        print(urlresponse)
        if urlresponse is None:
            urlresponse = ''
        if (urlresponse.startswith("http://m702")
                or urlresponse.startswith("http://m802") or len(urlresponse)
                == 0) and not urlresponse.endswith(".flac"):
            getfile_url = 'http://127.0.0.1:3000/song/download/url?id=' + str(
                response['mainSong']['id']) + '&br=320000'
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=getfile_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']['url']
            print(urlresponse)
        if urlresponse is None:
            urlresponse = ''

        if (urlresponse.startswith("http://m702")
                or urlresponse.startswith("http://m802") or len(urlresponse)
                == 0) and not urlresponse.endswith(".flac"):
            getfile_url = 'http://127.0.0.1:3000/song/url?id=' + str(
                response['mainSong']['id']) + '&br=320000'
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=getfile_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data'][0]['url']
            print(urlresponse)
        if urlresponse is None:
            urlresponse = ''

        if (urlresponse.startswith("http://m702")
                or urlresponse.startswith("http://m802") or len(urlresponse)
                == 0) and not urlresponse.endswith(".flac"):
            getfile_url = 'http://127.0.0.1:3000/song/download/url?id=' + str(
                response['mainSong']['id']) + '&br=320000'
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=getfile_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']['url']
            print(urlresponse)
        if urlresponse is None:
            urlresponse = ''
        if (urlresponse.startswith("http://m702")
                or urlresponse.startswith("http://m802") or len(urlresponse)
                == 0) and not urlresponse.endswith(".flac"):
            getfile_url = 'http://127.0.0.1:3000/song/url?id=' + str(
                response['mainSong']['id']) + '?timestamp='
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=getfile_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data'][0]['url']
            print(urlresponse)
        if urlresponse is None:
            urlresponse = ''
        if urlresponse.endswith("flac"):
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        urlresponse,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    with open(guild + ".flac", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild, p)
            p[guild] = subprocess.Popen(
                'ffmpeg -re -nostats -i "' + guild +
                '.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'
                + port[guild],
                shell=True)
        else:
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        urlresponse,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    with open(guild + "_" + botid + ".mp3", 'wb') as f:
                        while True:
                            chunk = await r.content.read()
                            if not chunk:
                                break
                            f.write(chunk)
            kill(guild, p)
            p[guild] = start_play(guild, port, botid)

        playtime[guild] = 0

        await delmsg(msgid[guild], config, botid)
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(
            Module.Header("正在播放： " + song_name),
            Module.Context(
                Element.Text(
                    "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" +
                    album_name + "](" + album_url + ")", Types.Text.KMD)),
            Module.File(Types.File.AUDIO,
                        src=urlresponse,
                        title=song_name,
                        cover=pic_url),
            Module.Countdown(
                datetime.now() + timedelta(seconds=duration[guild]),
                mode=Types.CountdownMode.SECOND), Module.Divider(),
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
                Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)))
        cm.append(c)
        print(json.dumps(cm))
        msgid[guild] = (await bot.send(
            await bot.fetch_public_channel(channel[guild]), cm))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        await bot.send(
            await bot.fetch_public_channel(channel[guild]),
            '发生错误，请重试',
        )
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        return
    LOCK[guild] = False
    return


async def qqmusic(guild, song_name, LOCK, playlist, duration, deltatime, bot,
                  config, playtime, p, botid, port, msgid, channel):
    LOCK[guild] = True
    try:
        if playlist[guild][0]['time'] > int(round(time.time() * 1000)):
            song_name = song_name.split('-')[-1]
            musicid = song_name
        else:
            url = "http://127.0.0.1:3300/search/quick?key=" + song_name
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    response = (await r.json())['data']['song']['itemlist'][0]
            musicid = response['mid']

        url = "http://127.0.0.1:3300/song?songmid=" + musicid
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                response = (await r.json())['data']['track_info']
        song_name = response['name']
        playlist[guild][0]['display'] = song_name
        duration[guild] = response['interval'] + deltatime
        song_url = 'https://y.qq.com/n/ryqq/songDetail/' + response['mid']
        album_name = response['album']['name']
        if album_name == '':
            album_name = '无专辑'
        album_url = 'https://y.qq.com/n/ryqq/albumDetail/' + response['album'][
            'mid']
        singer_name = response['singer'][0]['name']
        singer_url = 'https://y.qq.com/n/ryqq/singer/' + response['singer'][0][
            'mid']
        pic_url = 'https://y.gtimg.cn/music/photo_new/T002R300x300M000' + response[
            'album']['mid'] + '.jpg'
        getfile_url = 'http://127.0.0.1:3300/song/url?id=' + response[
            'mid'] + '&mediaId=' + response['file'][
                'media_mid'] + '&ownCookie=1'
        ban = re.compile('(惊雷)|(Lost Rivers)')
        resu = ban.findall(song_name)
        if len(resu) > 0:
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '吃了吗，没吃吃我一拳',
            )
            duration[guild] = 0
            playtime[guild] = 0
            LOCK[guild] = False
            return
        try:
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=getfile_url,
                        timeout=aiohttp.ClientTimeout(total=5)) as r:
                    urlresponse = (await r.json())['data']
        except:
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                'api cookie失效',
            )
            playlist[guild].pop(0)
            duration[guild] = 0
            playtime[guild] = 0
            LOCK[guild] = False
            return
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    urlresponse, timeout=aiohttp.ClientTimeout(total=5)) as r:
                with open(guild + "_" + botid + ".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)

        playtime[guild] = 0
        kill(guild, p)

        p[guild] = start_play(guild, port, botid)
        await delmsg(msgid[guild], config, botid)
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(
            Module.Header("正在播放： " + song_name),
            Module.Context(
                Element.Text(
                    "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" +
                    album_name + "](" + album_url + ")", Types.Text.KMD)),
            Module.File(Types.File.AUDIO,
                        src=urlresponse,
                        title=song_name,
                        cover=pic_url),
            Module.Countdown(
                datetime.now() + timedelta(seconds=duration[guild]),
                mode=Types.CountdownMode.SECOND), Module.Divider(),
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
                Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)))
        cm.append(c)
        msgid[guild] = (await bot.send(
            await bot.fetch_public_channel(channel[guild]), cm))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e) == "list index out of range":
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '未检索到此歌曲',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '发生错误，请重试',
            )
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        return
    LOCK[guild] = False
    return


async def migu(guild, song_name, LOCK, playlist, duration, deltatime, bot,
               config, playtime, p, botid, port, msgid, channel):
    LOCK[guild] = True
    try:
        if playlist[guild][0]['time'] > int(round(time.time() * 1000)):
            song_name = song_name.split('-')[-1]
            musicid = song_name
        else:

            url = "http://127.0.0.1:3400/song/find?keyword=" + song_name
            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    response = await r.json()
            musicid = str(response['data']['cid'])

        url = 'http://127.0.0.1:3400/song?cid=' + musicid
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                response = (await r.json())["data"]
        duration[guild] = response["duration"] + deltatime
        song_name = response["name"]
        playlist[guild][0]['display'] = song_name
        ban = re.compile('(惊雷)|(Lost Rivers)')
        resu = ban.findall(song_name)
        print(resu)
        if len(resu) > 0:

            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(config["channel"]),
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

        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    urlresponse, timeout=aiohttp.ClientTimeout(total=5)) as r:
                with open(guild + "_" + botid + ".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)
        kill(guild, p)
        p[guild] = start_play(guild, port, botid)
        playtime[guild] = 0
        if len(song_name) > 50:
            song_name = song_name[:50]
        await delmsg(msgid[guild], config, botid)
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(
            Module.Header("正在播放： " + song_name),
            Module.Context(
                Element.Text(
                    "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" +
                    album_name + "](" + album_url + ")", Types.Text.KMD)),
            Module.File(Types.File.AUDIO,
                        src=urlresponse,
                        title=song_name,
                        cover=pic_url),
            Module.Countdown(
                datetime.now() + timedelta(seconds=duration[guild]),
                mode=Types.CountdownMode.SECOND), Module.Divider(),
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
                Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)))
        cm.append(c)
        msgid[guild] = (await bot.send(
            await bot.fetch_public_channel(channel[guild]), cm))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e) == "'songs'":
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '未检索到此歌曲',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '发生错误，正在重试',
            )
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        return
    LOCK[guild] = False
    return


async def kmusic(guild, song_name, LOCK, playlist, duration, deltatime, bot,
                 config, playtime, p, botid, port, msgid, channel):
    LOCK[guild] = True
    try:
        song_name = parse_kmd_to_url(song_name)
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    url=song_name,
                    timeout=aiohttp.ClientTimeout(total=5)) as r:
                response = await r.text()

        pattern = r'(?<=window.__DATA__ = ).*?(?=; </script>)'
        response = json.loads(re.search(pattern, response).group())

        song_name = response['detail']['song_name']

        song_url = 'https://node.kg.qq.com/play?s=' + response['shareid']

        singer_name = response['detail']['nick']
        singer_url = 'https://node.kg.qq.com/personal?uid=' + response[
            'detail']['uid']
        pic_url = response['detail']['cover']
        urlresponse = response['detail']['playurl']
        ban = re.compile('(惊雷)|(Lost Rivers)')
        resu = ban.findall(song_name)
        if len(resu) > 0:
            playlist[guild].pop(0)
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
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
            url = "http://127.0.0.1:3300/song?songmid=" + re.search(
                r'(?<=songmid=)[0-9|a-z|A-Z]+',
                response['songinfo']['data']['song_url']).group()

            async with aiohttp.ClientSession(connector=TCPConnector(
                    verify_ssl=False)) as session:
                async with session.get(
                        url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    response = (await r.json())['data']['track_info']
            duration[guild] = response['interval'] + deltatime
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    urlresponse, timeout=aiohttp.ClientTimeout(total=5)) as r:
                with open(guild + "_" + botid + ".mp3", 'wb') as f:
                    while True:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        f.write(chunk)

        playtime[guild] = 0
        kill(guild, p)

        p[guild] = start_play(guild, port, botid)
        playlist[guild][0]['display'] = song_name
        await delmsg(msgid[guild], config, botid)
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(
            Module.Header("正在播放： " + song_name),
            Module.Context(
                Element.Text("歌手： [" + singer_name + "](" + singer_url + ")",
                             Types.Text.KMD)),
            Module.File(Types.File.AUDIO,
                        src=urlresponse,
                        title=song_name,
                        cover=pic_url),
            Module.Countdown(
                datetime.now() + timedelta(seconds=duration[guild]),
                mode=Types.CountdownMode.SECOND), Module.Divider(),
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
                Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)))
        cm.append(c)
        msgid[guild] = (await bot.send(
            await bot.fetch_public_channel(channel[guild]), cm))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if str(e) == "'songs'":
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '未检索到此歌曲',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '发生错误，正在重试',
            )
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        return
    LOCK[guild] = False
    return


async def get_result(link, event_loop, executor):
    return await event_loop.run_in_executor(executor, YouTube, link)


async def download(result, guild, event_loop, executor, botid):
    tmp = await event_loop.run_in_executor(executor,
                                           result.streams.get_by_itag, 251)
    await event_loop.run_in_executor(executor, tmp.download, '.',
                                     guild + "_" + botid + ".mp3")


async def ytb(guild, song_name, LOCK, playlist, duration, deltatime, bot,
              config, playtime, p, botid, port, msgid, channel, event_loop,
              executor):

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
        kill(guild, p)
        p[guild] = start_play(guild, port, botid)
        await delmsg(msgid[guild], config, botid)
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(
            Module.Context(
                Element.Text(
                    "**标题:        [" + title + "](" + song_name + ")**",
                    Types.Text.KMD)),
            Module.Context(Element.Text("UP:         " + name,
                                        Types.Text.KMD)),
            Module.Countdown(datetime.now() +
                             timedelta(seconds=duration[guild]),
                             mode=Types.CountdownMode.SECOND),
            Module.ActionGroup(
                Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)))
        cm.append(c)
        msgid[guild] = (await bot.send(
            await bot.fetch_public_channel(channel[guild]), cm))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        if 'is unavailable' in str(e):
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '未检索到此视频',
            )
        elif str(
                e
        ) == r"regex_search: could not find match for (?:v=|\/)([0-9A-Za-z_-]{11}).*":
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '链接输入有误',
            )
        else:
            await bot.send(
                await bot.fetch_public_channel(channel[guild]),
                '发生错误，正在重试',
            )
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        return
    LOCK[guild] = False
    return


async def fm(guild, song_name, LOCK, playlist, duration, deltatime, bot,
             config, playtime, p, botid, port, msgid, channel):
    LOCK[guild] = True
    try:
        song_name = parse_kmd_to_url(song_name)
        broadcastid = re.search(r'(?<=/radios/)[0-9]+', song_name).group()
        url = 'https://webapi.qtfm.cn/api/pc/radio/' + broadcastid
        async with aiohttp.ClientSession(connector=TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(
                    url=url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                response = await r.json()
        title = response['album']['title'] + '-' + response['album'][
            'nowplaying']['title']
        description = response['album']['description']
        now = datetime.strptime(time.strftime("%H:%M:%S", time.localtime()),
                                '%H:%M:%S')
        end = datetime.strptime(response['album']['nowplaying']['end_time'],
                                '%H:%M:%S')
        duration[guild] = (end - now).seconds
        playtime[guild] = 0
        kill(guild, p)
        p[guild] = subprocess.Popen(
            'ffmpeg -re -nostats -i "https://lhttp.qingting.fm/live/' +
            broadcastid +
            '/64k.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'
            + port[guild],
            shell=True)
        await delmsg(msgid[guild], config, botid)
        playlist[guild][0]['display'] = title
        cm = CardMessage()
        c = get_playlist(guild, playlist)
        cm.append(c)
        c = Card(
            Module.Header("正在播放： " + title),
            Module.Context(Element.Text(description, Types.Text.KMD)),
            Module.Countdown(
                datetime.now() + timedelta(seconds=duration[guild]),
                mode=Types.CountdownMode.SECOND), Module.Divider(),
            Module.ActionGroup(
                Element.Button('下一首', 'NEXT', Types.Click.RETURN_VAL),
                Element.Button('清空歌单', 'CLEAR', Types.Click.RETURN_VAL),
                Element.Button('循环模式', 'LOOP', Types.Click.RETURN_VAL)))
        cm.append(c)
        msgid[guild] = (await bot.send(
            await bot.fetch_public_channel(channel[guild]), cm))["msg_id"]
        playtime[guild] += deltatime
    except Exception as e:
        print(str(e))
        playlist[guild].pop(0)
        duration[guild] = 0
        playtime[guild] = 0
        LOCK[guild] = False
        return
    LOCK[guild] = False
    return