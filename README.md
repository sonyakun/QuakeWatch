# QuakeWatch👀 - Selenium
> **Warning**
> ChromeDriver(selenium)版QuakeWatchは公式Botでは**一切利用されていません。**
> そのため、バグが発生する可能性があります。
QuakeWatchは、Discord/Misskey上で動作する地震情報botです。

[非公式MastodonBot](https://social.vivaldi.net/@jpearthquake)
## 依存関係
- folium
- fastapi
- discord-webhook
- misskey.py
- websockets
- httpx
- uvicorn[standard]
- selenium
- ChromeDriver

依存関係をまとめてインストールしてくれるやつ
```shell
pip install folium fastapi discord-webhook misskey.py websockets httpx "uvicorn[standard]" selenium
```

インストール後、お使いのOSとChromeのバージョンに対応したChromeDriverをダウンロードしてください。
https://chromedriver.chromium.org/downloads

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
