from fastapi import FastAPI, status, Response
import uvicorn
import base64
import binascii
import json
import uuid
import folium
import os
import httpx
from playwright.sync_api import sync_playwright
from folium.features import CustomIcon

description = """
QuakeWatch向けバックエンドAPI
"""

app = FastAPI(
    title="QuakeWatch Backend API",
    description=description,
)

@app.get("/generate_map")
def generate_map(map_data: str, response: Response):
    file_name = uuid.uuid4()
    scale_to_icon = {
        "10": "images/震度1_bg.png",
        "20": "images/震度2_bg.png",
        "30": "images/震度3_bg.png",
        "40": "images/震度4_bg.png",
        "45": "images/震度5-_bg.png",
        "50": "images/震度5+_bg.png",
        "55": "images/震度6-_bg.png",
        "60": "images/震度6+_bg.png",
        "70": "images/震度7_bg.png"
    }
    try:
        jl = json.loads(map_data) #map_dataをstringとして受け取り、デコードしたものをjsonでロードする
        print([jl["earthquake"]["hypocenter"]["latitude"], jl["earthquake"]["hypocenter"]["longitude"]])
        m = folium.Map(
            location=[jl["earthquake"]["hypocenter"]["latitude"], jl["earthquake"]["hypocenter"]["longitude"]],
            tiles="cartodbdark_matter",
            zoom_start=7
        )
        icon = CustomIcon(
            icon_image = "images/x.png",
            icon_size = (25, 25),
            icon_anchor = (30, 30),
            popup_anchor = (3, 3)
        )
        folium.Marker(
            location = [jl["earthquake"]["hypocenter"]["latitude"], jl["earthquake"]["hypocenter"]["longitude"]],
            icon=icon
        ).add_to(m)
        for i in range(len(jl["points"])):
            print(i)
            resp = httpx.get(url=f'https://msearch.gsi.go.jp/address-search/AddressSearch?q={jl["points"][i]["pref"]}{jl["points"][i]["addr"]}')
            rj = resp.json()
            print(type(jl["points"][i]["scale"]))
            print(type(str(jl["points"][i]["scale"])))
            if jl["points"][i]["scale"] == 10:
                icon = CustomIcon(
                    icon_image = "images/震度1_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            if jl["points"][i]["scale"] == 20:
                icon = CustomIcon(
                    icon_image = "images/震度2_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            if jl["points"][i]["scale"] == 30:
                icon = CustomIcon(
                    icon_image = "images/震度3_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            if jl["points"][i]["scale"] == 40:
                icon = CustomIcon(
                    icon_image = "images/震度4_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            if jl["points"][i]["scale"] == 45:
                icon = CustomIcon(
                    icon_image = "images/震度5-_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            if jl["points"][i]["scale"] == 50:
                icon = CustomIcon(
                    icon_image = "images/震度5+_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            if jl["points"][i]["scale"] == 55:
                icon = CustomIcon(
                    icon_image = "images/震度6-_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            if jl["points"][i]["scale"] == 60:
                icon = CustomIcon(
                    icon_image = "images/震度6+_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            if jl["points"][i]["scale"] == 70:
                icon = CustomIcon(
                    icon_image = "images/震度7_bg.png",
                    icon_size = (25, 25),
                    icon_anchor = (30, 30),
                    popup_anchor = (3, 3)
                )
            folium.Marker(
                location = [rj[0]["geometry"]["coordinates"][1], rj[0]["geometry"]["coordinates"][0]],
                icon=icon
            ).add_to(m)

        m.save(f"temp/{file_name}.html")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{os.path.abspath('.')}/temp/{file_name}.html")
            import time
            time.sleep(1)
            page.screenshot(path=f'temp/{file_name}.png', full_page=True)
        os.remove(f"temp/{file_name}.html")
        with open(f"temp/{file_name}.png", "rb") as image_file:
            data = base64.b64encode(image_file.read())
        #os.remove(f"temp/{file_name}.png") 現状削除をここでするのは良くない
        return {"message": "成功", "content": data, "uuid": file_name}
    except binascii.Error as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "不正な文字列"}
    
if __name__ == "__main__":
    uvicorn.run(app, port=8000)