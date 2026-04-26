from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.qq import *
import aiohttp
GetMcUser = on_command("查询MC玩家",aliases={"查询mc玩家"},priority=10,block=True)

@GetMcUser.handle()
async def GetStatus(args:Message = CommandArg()):
    if UserName := args.extract_plain_text():
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://uapis.cn/api/v1/game/minecraft/userinfo?username={UserName}") as response:
                if response.status == 200:
                    user_data = await response.json()
                    username = user_data["username"]
                    uuid = user_data["uuid"]
                    skin_url = user_data["skin_url"]    
            async with session.get(skin_url) as response_skin:
                image_data = await response_skin.read()
            rely_msg = Message([MessageSegment.text(f"\n玩家名称：{username}\nUUID：{uuid}\n"),MessageSegment.file_image(image_data)])
            await GetMcUser.send(rely_msg)
            