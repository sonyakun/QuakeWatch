# QuakeWatch👀
QuakeWatchは、Discord/Misskey上で動作する地震情報botです。

[Misskey公式bot](https://misskey.io/@eewbot)

~~Discord公式bot~~現在公式botは非公開です。

[非公式MastodonBot](https://social.vivaldi.net/@jpearthquake)
# Example
![readme_img/Screenshot 2023-05-29 11.07.05.png](https://github.com/sonyakun/QuakeWatch/blob/0976efc9e5452295dc73482a6391902b721ece4c/readme_img/Screenshot%202023-05-29%2011.07.05.png)
![img](https://github.com/sonyakun/QuakeWatch/blob/0976efc9e5452295dc73482a6391902b721ece4c/readme_img/Screenshot%202023-05-29%2011.32.19.png)
# Self Hosting
> **Warning**
> セルフホスティングにより動作環境で生じた不具合などの責任は**一切負いません。**
## 依存関係
- folium
- fastapi
- discord-webhook
- misskey.py
- websockets
- httpx
- uvicorn[standard]
- playwright

依存関係をまとめてインストールしてくれるやつ
```shell
pip install folium fastapi discord-webhook misskey.py websockets httpx "uvicorn[standard]" playwright
```

インストール後に実行するやつ
```shell
py -m playwright install
```
## セッティング
起動する前に、config.iniを編集する必要があります。
config.iniを開き、tokenの部分にmisskeyのapiトークンを書き込んでください。
serverには、アカウントのあるインスタンス(misskey.ioなど)を入力してください。
WEBHOOK_URLは何も書かれていない場合はスルーされます。
```ini
[MISSKEY] #Misskeyへの送信を利用する際に参照するセクションです。
TOKEN = 
SERVER = 

[DISCORD] #DiscordのWebhookへの送信を利用する際に参照するセクションです。
WEBHOOK_URL = 
#WEBHOOK_URLの末尾に?wait=trueをつけてください。
```
## 起動
起動は、backend.py=>main.pyの順で起動してください。backendが起動していない場合、地震発生時に正常な動作になりません。
