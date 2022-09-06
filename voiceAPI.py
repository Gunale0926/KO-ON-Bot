import random
import time
from typing import List
import aiohttp
import json
import asyncio
from aiohttp import ClientWebSocketResponse


class Voice:
    token = ''
    channel_id = ''
    rtp_url = ''
    ws_clients: List[ClientWebSocketResponse] = []
    wait_handler_msgs = []
    is_exit = False
    ssrc = 0

    def __init__(self, token: str):
        self.token = token
        self.ws_clients = []
        self.wait_handler_msgs = []

    async def get_gateway(self, channel_id: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://www.kaiheila.cn/api/v3/gateway/voice?channel_id={channel_id}',
                    headers={'Authorization': f'Bot {self.token}'}) as res:
                return (await res.json())['data']['gateway_url']

    async def connect_ws(self):
        gateway = await self.get_gateway(self.channel_id)
        print(gateway)
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(gateway) as ws:
                self.ws_clients.append(ws)
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if len(self.ws_clients
                               ) != 0 and self.ws_clients[0] == ws:
                            self.wait_handler_msgs.append(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
                    else:
                        return

    async def ws_msg(self):
        while True:
            if self.is_exit:
                return
            if len(self.ws_clients) != 0:
                break
            await asyncio.sleep(0.1)
        payload = {
            "1": {
                "request": True,
                "id": random.randint(1000000, 9999999),
                "method": "getRouterRtpCapabilities",
                "data": {}
            },
            "2": {
                "data": {
                    "displayName": ""
                },
                "id": random.randint(1000000, 9999999),
                "method": "join",
                "request": True
            },
            "3": {
                "data": {
                    "comedia": True,
                    "rtcpMux": False,
                    "type": "plain"
                },
                "id": random.randint(1000000, 9999999),
                "method": "createPlainTransport",
                "request": True
            },
            "4": {
                "data": {
                    "appData": {},
                    "kind": "audio",
                    "peerId": "",
                    "rtpParameters": {
                        "codecs": [{
                            "channels": 2,
                            "clockRate": 48000,
                            "mimeType": "audio/opus",
                            "parameters": {
                                "sprop-stereo": 1
                            },
                            "payloadType": 100
                        }],
                        "encodings": [{
                            "ssrc": random.randint(1000, 9999)
                        }]
                    },
                    "transportId": ""
                },
                "id": random.randint(1000000, 9999999),
                "method": "produce",
                "request": True
            }
        }
        print('1:', payload['1'])
        await self.ws_clients[0].send_json(payload['1'])
        now = 1
        ip = ''
        port = 0
        rtcp_port = 0
        while True:
            if self.is_exit:
                return
            if len(self.wait_handler_msgs) != 0:
                data = json.loads(self.wait_handler_msgs.pop(0))
                if now == 1:
                    print('1:', data)
                    print('2:', payload['2'])
                    await self.ws_clients[0].send_json(payload['2'])
                    now = 2
                elif now == 2:
                    print('2:', data)
                    print('3:', payload['3'])
                    await self.ws_clients[0].send_json(payload['3'])
                    now = 3
                elif now == 3:
                    print('3:', data)
                    transport_id = data['data']['id']
                    ip = data['data']['ip']
                    port = data['data']['port']
                    rtcp_port = data['data']['rtcpPort']
                    payload['4']['data']['transportId'] = transport_id
                    self.ssrc = payload['4']['data']['rtpParameters']['encodings'][
                        0]['ssrc']
                    print('4:', payload['4'])
                    await self.ws_clients[0].send_json(payload['4'])
                    now = 4
                elif now == 4:
                    print('4:', data)
                    self.rtp_url = f'rtp://{ip}:{port}?rtcpport={rtcp_port}'
                    now = 5
                else:
                    if 'notification' in data and 'method' in data and data[
                            'method'] == 'disconnect':
                        print('The connection had been disconnected', data)
                    else:
                        pass
            await asyncio.sleep(0.1)

    async def ws_ping(self):
        while True:
            if self.is_exit:
                return
            if len(self.ws_clients) != 0:
                break
            await asyncio.sleep(0.1)
        ping_time = 0.0
        while True:
            if self.is_exit:
                return
            await asyncio.sleep(0.1)
            if len(self.ws_clients) == 0:
                return
            now_time = time.time()
            if now_time - ping_time >= 30:
                await self.ws_clients[0].ping()
                ping_time = now_time

    async def main(self):
        await asyncio.wait(
            [self.ws_msg(), self.connect_ws(),
             self.ws_ping()],
            return_when='FIRST_COMPLETED')
        if len(self.ws_clients) != 0:
            await self.ws_clients[0].close()
        self.is_exit = False
        self.channel_id = ''
        self.rtp_url = ''
        self.ws_clients.clear()
        self.wait_handler_msgs.clear()

    async def handler(self):
        while True:
            if len(self.channel_id) != 0:
                await self.main()
            await asyncio.sleep(0.1)