from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.qq import *
import aiohttp
from pathlib import Path
Today = on_command("历史上的今天",rule=to_me(),priority=10,block=True)
@Today.handle()
async def GetInfomation():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://v2.xxapi.cn/api/historypic") as response:
            if response.status == 200:
                data = await response.json()
                url = data["data"]
        async with session.get(url) as img_res:
            img_data = await img_res.read()
            rely_msg = Message(MessageSegment.file_image(data=img_data))
            await Today.send(rely_msg)