from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.qq import *
import aiohttp
News = on_command("每日新闻",rule=to_me(),priority=10,block=10)

@News.handle()
async def GetNews():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://uapis.cn/api/v1/daily/news-image") as response:
            if response.status == 200:
                image_data = await response.read()
                rely_msg = Message(MessageSegment.file_image(data=image_data))
                await News.send(rely_msg)
            else:
                await query.send("Sorry!There are some mistakes here...")