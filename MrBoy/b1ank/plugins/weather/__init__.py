from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.qq import bot,MessageCreateEvent, Message, MessageSegment
import aiohttp
weather = on_command("天气",rule=to_me(),aliases={"weather","查天气"},priority=10,block=True)

@weather.handle()
async def GetWeather(args:Message = CommandArg()):
    if location := args.extract_plain_text():
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://uapis.cn/api/v1/misc/weather?city={location}&lang=zh") as response:
                if response.status != 200:
                    await weather.send("Sorry!There are some mistakes here...")
                else:
                    weather_data = await response.json()
                    province = weather_data["province"]
                    city = weather_data["city"]
                    weather1 = weather_data["weather"]
                    temperature = weather_data["temperature"]
                    wind_direction = weather_data["wind_direction"]
                    wind_power = weather_data["wind_power"]
                    humidity = weather_data["humidity"]
                    report_time = weather_data["report_time"]
        reply_msg = Message([MessageSegment.text(f"\n省份：{province}\n城市：{city}\n天气：{weather1}\n温度：{temperature}\n风向：{wind_direction}\n风力：{wind_power}\n湿度：{humidity}\n时间：{report_time}")])
        await weather.send(reply_msg)
    else:
        await weather.send("Please enter location...")
