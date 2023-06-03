import asyncio, json, aiohttp
from websockets import client
from websockets.exceptions import ConnectionClosed
import websockets
from discord_webhook import DiscordWebhook, DiscordEmbed
import base64
import httpx as requests
from datetime import datetime
from misskey import Misskey, MiAuth
import misskey
import os
import configparser
import webbrowser
import logging

"""
QuakeWatchの画像生成用バックエンドの簡易ドキュメント
http://ip/generate_map?map_data=にp2p地震速報のjsonを投げる(キーが0から始まるものは中身を投げてください。)
成功時に返却されるものはcontentキーの中身にある文字base64でエンコードしたpngです。
"""

inifile = configparser.ConfigParser()
inifile.read('config.ini', encoding="utf-8")
gateway_url = "wss://api.p2pquake.net/v2/ws"
genmap = "http://localhost:8000/generate_map?map_data="
gateway_dummy = "ws://localhost:8765/"

class Color:
	BLACK          = '\033[30m'#(文字)黒
	RED            = '\033[31m'#(文字)赤
	GREEN          = '\033[32m'#(文字)緑
	YELLOW         = '\033[33m'#(文字)黄
	BLUE           = '\033[34m'#(文字)青
	MAGENTA        = '\033[35m'#(文字)マゼンタ
	CYAN           = '\033[36m'#(文字)シアン
	WHITE          = '\033[37m'#(文字)白
	COLOR_DEFAULT  = '\033[39m'#文字色をデフォルトに戻す
	BOLD           = '\033[1m'#太字
	UNDERLINE      = '\033[4m'#下線
	INVISIBLE      = '\033[08m'#不可視
	REVERCE        = '\033[07m'#文字色と背景色を反転
	BG_BLACK       = '\033[40m'#(背景)黒
	BG_RED         = '\033[41m'#(背景)赤
	BG_GREEN       = '\033[42m'#(背景)緑
	BG_YELLOW      = '\033[43m'#(背景)黄
	BG_BLUE        = '\033[44m'#(背景)青
	BG_MAGENTA     = '\033[45m'#(背景)マゼンタ
	BG_CYAN        = '\033[46m'#(背景)シアン
	BG_WHITE       = '\033[47m'#(背景)白
	BG_DEFAULT     = '\033[49m'#背景色をデフォルトに戻す
	RESET          = '\033[0m'#全てリセット

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # ログレベルに応じて色を設定
        if record.levelno == logging.DEBUG:
            color = '\033[37m' # White
        elif record.levelno == logging.INFO:
            color = '\033[32m' # Green
        elif record.levelno == logging.WARNING:
            color = '\033[33m' # Yellow
        elif record.levelno == logging.ERROR:
            color = '\033[31m' # Red
        elif record.levelno == logging.CRITICAL:
            color = '\033[35m' # Magenta

        # ログメッセージをカラーフォーマットで出力
        message = super().format(record)
        message = color + message + '\033[0m'
        return message

# ログの設定
logging.basicConfig(
    format="{asctime} {websocket.id} {websocket.remote_address[0]} {message}",
    level=logging.INFO,
    style="{",
)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(ColoredFormatter())
logging.getLogger().addHandler(handler)

class LoggerAdapter(logging.LoggerAdapter):
    """Add connection ID and client IP address to websockets logs."""
    def process(self, msg, kwargs):
        try:
            websocket = kwargs["extra"]["websocket"]
        except KeyError:
            return msg, kwargs
        xff = websocket.request_headers.get("X-Forwarded-For")
        return f"{websocket.id} {xff} {msg}", kwargs

async def connect():
    print(f"{Color.GREEN}[INFO]{Color.RESET}P2P地震速報WebSocketAPIに接続しています...")
    while True:
        async for ws in client.connect(gateway_url):
            print(f"{Color.GREEN}[INFO]{Color.RESET}P2P地震速報WebSocketAPIに接続しました！")
            try:
                while True:
                    recv = await ws.recv()
                    print(f"{Color.YELLOW}[LOG]{Color.RESET}\n------------------------------------------------------\n{recv}\n------------------------------------------------------")
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
                                    file_bin_logoeffect = io.BytesIO(base64.b64decode(rj["content"].encode('utf-8')))
                                    #with open(f'temp\\{rj["uuid"]}.png', 'rb') as f:
                                    #    file_bin_logoeffect = f.read()
                                    files_discord  = {
                                        "logo_bg" : ( "eew2.png", file_bin_logobg ),
                                        "logo_effect" : ( "eew.png", file_bin_logoeffect ),
                                    }
                                    payload2['payload_json'] = json.dumps( payload2['payload_json'], ensure_ascii=False )
                                    print(WEBHOOK_URL)
                                    async with requests.AsyncClient() as httpx:
                                        res = httpx.post(WEBHOOK_URL, files = files_qiita  , data = payload2 )
                                        print( res.status_code )
                                        print( json.dumps( json.loads(res.content), indent=4, ensure_ascii=False ) )
                                if not inifile.get('MISSKEY', 'TOKEN') == "":
                                    mk = Misskey(inifile.get('MISSKEY', 'SERVER'), i=inifile.get('MISSKEY', 'TOKEN'))
                                    f = io.BytesIO(base64.b64decode(rj["content"].encode('utf-8')))
                                    data = mk.drive_files_create(f, name="eew.png")
                                    new_note = mk.notes_create(text=f'{result_str}頃、マグニチュード{magnitude}、最大{mt[sindo]}の地震が発生しました。深さは{depth}km、発生場所は{name}です。詳細は以下の画像をご覧ください。', file_ids=[data["id"]])
                                    os.remove(f'temp\\{rj["uuid"]}.png')
            except ConnectionClosed:
                print(f"{Color.GREEN}[INFO]{Color.RESET}接続が終了しました。再接続しています...")
                continue

if __name__ == "__main__":
    asyncio.run(connect())
