import colorama
import requests
import json
import time
from colorama import Fore
colorama.init(autoreset=True)
print(Fore.LIGHTGREEN_EX+"by B1ank")
while True:
    path = input("请输入保存路径：")
    name_list = input("请输入歌曲（歌曲名用逗号隔开）：")
    name_list = name_list.replace("，",",").split(",")
    for name in name_list:
        search_id_url = 'https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={}&type=1&offset=0&total=true&limit=10'.format(name)
        get = json.loads(requests.get(search_id_url).text)
        for songs in get['result']['songs']:
            name = songs['name']
            artists = songs['artists'][0]['name']
            id = songs['id']
            mp3_url = 'http://music.163.com/song/media/outer/url?id={}.mp3'.format(id)
            mp3 = requests.get(mp3_url).content
            time.sleep(4)
            if 'DOCTYPE html' not in str(mp3):
                file = open(r'{}\{} - {}.mp3'.format(path,artists,name),'ab')
                file.write(mp3)
                file.close()
                print(Fore.LIGHTCYAN_EX+'\n歌曲名:{}\n歌曲id:{}\n歌手:{}\n'.format(name, id, artists))
                break