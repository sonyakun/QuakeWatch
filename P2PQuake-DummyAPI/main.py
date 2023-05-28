"""
これってなに？
このプログラムは、P2P地震速報WebsocketAPIで地震情報を取得した際のjsonと全く同じ構造のjsonを定期的に送信するwebsocketサーバーです。
システムが正常に動作しているかの確認で利用することが多いです。
"""

import asyncio
import json
import websockets
import time

async def send_messages(websocket, path):
    while True:
        message = {"_id":"6472dd2f51d38bb17b2e831a","code":551,"earthquake":{"domesticTsunami":"None","foreignTsunami":"Unknown","hypocenter":{"depth":10,"latitude":29.9,"longitude":130,"magnitude":2,"name":"【テスト】トカラ列島近海"},"maxScale":10,"time":"2023/05/28 13:45:00"},"issue":{"correct":"None","source":"元データ: 気象庁","time":"2023/05/28 13:48:47","type":"DetailScale"},"points":[{"addr":"鹿児島十島村口 之島出張所","isArea":False,"pref":"鹿児島県","scale":70}],"time":"2023/05/28 13:48:47.464","timestamp":{"convert":"2023/05/28 13:48:47.458","register":"2023/05/28 13:48:47.464"},"user_agent":"jmaxml-seis-parser-go, relay, register-api","ver":"20220813"}
        await websocket.send(json.dumps(message))
        await asyncio.sleep(10)

async def start_server():
    async with websockets.serve(send_messages, 'localhost', 8765):
        await asyncio.Future()

asyncio.get_event_loop().run_until_complete(start_server())
asyncio.get_event_loop().run_forever()
