import asyncio, json, aiohttp
from websockets import client
from websockets.exceptions import ConnectionClosed
from discord_webhook import DiscordWebhook, DiscordEmbed
import base64
import httpx
from datetime import datetime
from misskey import Misskey, MiAuth
import misskey
import os
import configparser
import webbrowser

inifile = configparser.ConfigParser()
inifile.read('config.ini', encoding="utf-8")
gateway_url = "wss://api.p2pquake.net/v2/ws"
genmap = "http://localhost:8000/generate_map?map_data="
gateway_dummy = "ws://localhost:8765/"

async def connect():
    while True:
        async with client.connect(gateway_url) as ws:
            while True:
                recv = await ws.recv()
                lj = json.loads(recv)
                if lj["code"] == 551:
                    sindo = str(lj["earthquake"]["maxScale"])
                    magnitude = str(lj["earthquake"]["hypocenter"]["magnitude"])
                    depth = str(lj["earthquake"]["hypocenter"]["depth"])
                    name = lj["earthquake"]["hypocenter"]["name"]
                    mt = {
                        "10": "震度1",
                        "20": "震度2",
                        "30": "震度3",
                        "40": "震度4",
                        "50": "震度5弱",
                        "55": "震度5強",
                        "60": "震度6弱",
                        "65": "震度6強",
                        "70": "震度7",
                    }
                    sindoto10code = {
                        "10": 3955330,
                        "20": 1999590,
                        "30": 7923420,
                        "40": 16777110,
                        "50": 16765440,
                        "55": 16750080,
                        "60": 15741440,
                        "65": 12451840,
                        "70": 9175080,
                    }
                    dt = datetime.strptime(lj["earthquake"]["time"], '%Y/%m/%d %H:%M:%S')
                    result_str = dt.strftime('%Y年%m月%d日 %H時%M分')
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url=genmap + recv) as resp:
                            rj = await resp.json()
                            WEBHOOK_URL = inifile.get('DISCORD', 'WEBHOOK_URL')
                            if WEBHOOK_URL == "":
                                pass
                            else:
                                payload2 = {
                                    "payload_json" : {
                                        "username"      :"QuakeWatch👀",
                                        "embeds": [
                                            {
                                                "title"         : "地震発生",
                                                "description"   : f'{result_str}頃、マグニチュード{magnitude}、最大{mt[sindo]}の地震が発生しました。深さは{depth}km、発生場所は{name}です。詳細は以下の画像をご覧ください。',
                                                "url"           : "http://www.seis.bosai.go.jp/",
                                                "color"         : sindoto10code[sindo],
                                                "footer": {
                                                    "text"      : "ソース: 気象庁",
                                                },
                                                "thumbnail": {
                                                    "url"       : "attachment://eew2.png"
                                                },
                                                "image": {
                                                    "url"       : "attachment://eew.png"
                                                }
                                            }
                                        ],
                                    }
                                }
                                with open(f"images/{sindo}.png", 'rb') as f:
                                    file_bin_logobg = f.read()
                                with open(f'G:\\PubricBot-Backend\\EEWMap\\temp\\{rj["uuid"]}.png', 'rb') as f:
                                    file_bin_logoeffect = f.read()
                                files_qiita  = {
                                    "logo_bg" : ( "eew2.png", file_bin_logobg ),
                                    "logo_effect" : ( "eew.png", file_bin_logoeffect ),
                                }
                                payload2['payload_json'] = json.dumps( payload2['payload_json'], ensure_ascii=False )
                                print(WEBHOOK_URL)
                                res = httpx.post(WEBHOOK_URL, files = files_qiita  , data = payload2 )
                                print( res.status_code )
                                print( json.dumps( json.loads(res.content), indent=4, ensure_ascii=False ) )
                            if not inifile.get('MISSKEY', 'TOKEN') == "":
                                mk = Misskey(inifile.get('MISSKEY', 'SERVER'), i=inifile.get('MISSKEY', 'TOKEN'))
                                with open(f'G:\\PubricBot-Backend\\EEWMap\\temp\\{rj["uuid"]}.png', "rb") as f:
                                    data = mk.drive_files_create(f)
                                new_note = mk.notes_create(text=f'{result_str}頃、マグニチュード{magnitude}、最大{mt[sindo]}の地震が発生しました。深さは{depth}km、発生場所は{name}です。詳細は以下の画像をご覧ください。', file_ids=[data["id"]])
                                os.remove(f'G:\\PubricBot-Backend\\EEWMap\\temp\\{rj["uuid"]}.png')

asyncio.run(connect())