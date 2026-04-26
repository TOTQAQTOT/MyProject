from nonebot import on_command,on_message
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.qq import *
import aiohttp
from pathlib import Path
from openai import *
client = AsyncOpenAI(
    api_key="sk-414f5b8d5c9445e9ae48681378014099", 
    base_url="https://api.deepseek.com"
)
getmessage = on_message(rule=to_me(),priority=10)

@getmessage.handle()
async def process(bot:Bot,event:MessageEvent):
    
    message = str(event.get_message())
    if message[0] != "/":
        response = await client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {"role": "system", "content": "你是一个有用的助手"},
                {"role": "user", "content": f"{message}"}
            ],
            temperature=1.3,
            max_tokens=2048,
            stream=False,
        )
        await getmessage.send(response.choices[0].message.content)
    