from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.qq import *
import aiohttp
from pathlib import Path
import base64
query = on_command("查询MC服务器",rule=to_me(),aliases={"查询Mc服务器","查询mc服务器"},priority=10,block=True)

@query.handle()
async def QueryStatus(bot:Bot,event:MessageEvent,args:Message = CommandArg()):
    if server := args.extract_plain_text():
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://uapis.cn/api/v1/game/minecraft/serverstatus?server={server}") as response:
                if response.status == 200:
                    status_data = await response.json()
                    online = status_data["online"]
                    ip = status_data["ip"]
                    port = status_data["port"]
                    players = status_data["players"]
                    max_players = status_data["max_players"]
                    version = status_data["version"]
                    image_data = status_data["favicon_url"]
                    img_base64_data = base64.b64decode((image_data.split(",",1)[1]))
                    rely_msg = Message([
                        MessageSegment.file_image(data=img_base64_data),
                    MessageSegment.text(f"\nOnline:{online}\nIP:{ip}\nPort:{port}\nPlayers:{players}/{max_players}\nVersion:{version}")])
                    await query.send(rely_msg)

                else:
                    await query.send("Sorry!There are some mistakes here...")