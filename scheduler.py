import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from time import time

from aiohttp import web
from aiohttp.web_request import Request
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import status_manage

config = status_manage.load_config()
system_time = ""

msg_queue = []

result = {}

logger = getLogger('scheduler')
logger.setLevel(level=INFO)

formatter = Formatter(
    '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

file_handler = FileHandler(filename='scheduler.log', mode='a')
file_handler.setLevel(level=INFO)
file_handler.setFormatter(formatter)

stream_handler = StreamHandler()
stream_handler.setLevel(level=INFO)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


async def msg_handler(request: Request):
    event = json.loads((await request.content.read()).decode('utf-8'))
    event['timestamp'] = int(round(time() * 1000))
    new_msg_flag = True
    i = 0
    for msg in msg_queue:
        if event['server'] == msg['server'] and event['voicechannel'] == msg[
                'voicechannel']:
            new_msg_flag = False
            break
        i += 1
    if new_msg_flag:
        msg_queue.append(event)
    else:
        msg_queue[i]['botid'].append(event['botid'][0])
        msg_queue[i]['able'].append(event['able'][0])
        msg_queue[i]['already_in'].append(event['already_in'][0])
    signatures = f"{event['server']}-{event['voicechannel']}-{event['botid'][0]}"
    result[signatures] = 'WAITING'
    while result[signatures] == 'WAITING':
        await asyncio.sleep(0.1)
    return web.Response(status=200, text=result[signatures])


app = web.Application()
app.add_routes([web.post('/scheduler', msg_handler)])


async def timeout():
    global msg_queue
    global system_time
    global result
    system_time = int(round(time() * 1000))
    timeout_queue = []
    keep_queue = []
    for msg in msg_queue:
        if system_time < msg['timestamp'] + 1500:
            keep_queue.append(msg)
        else:
            timeout_queue.append(msg)
    msg_queue = keep_queue
    for msg in timeout_queue:
        logger.info(msg)
        if True in msg['already_in']:
            for botid in msg['botid']:
                signatures = f"{msg['server']}-{msg['voicechannel']}-{botid}"
                result[signatures] = "REFUSE"
                logger.info("REFUSE")
        else:
            i = 0
            used = False
            botnum = len(msg['botid']) - 1
            for botid in msg['botid']:
                signatures = f"{msg['server']}-{msg['voicechannel']}-{botid}"
                result[signatures] = "REFUSE"
                if msg['able'][i]:
                    if not used:
                        used = True
                        result[signatures] = "ACCEPT"
                        logger.info("ACCEPT")
                        continue
                else:
                    if i == botnum:
                        result[signatures] = "REPORT"
                        logger.info("REPORT")
                        continue
                logger.info("REFUSE")
                i += 1


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor = ThreadPoolExecutor(1000)
    sched = AsyncIOScheduler(timezone='Asia/Shanghai')
    sched.add_job(timeout, 'interval', seconds=0.2)
    sched.start()
    web.run_app(app, port=int(config["schedule_server_port"]), loop=loop)
