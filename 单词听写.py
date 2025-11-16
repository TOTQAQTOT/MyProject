import thread.thread
import time
import os
import tkinter as tk
from tkinter import ttk
import random
import pyttsx3
import re
import translate

dir_path = "C:\\wordlist"
read_num_list = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'twenty-one', 'twenty- two', 'twenty- three', 'twenty- four', 'twenty- five', 'twenty- six', 'twenty- seven', 'twenty- eight', 'twenty- nine', 'thirty', 'thirty- one', 'thirty- two', 'thirty- three', 'thirty- four', 'thirty- five', 'thirty- six', 'thirty- seven', 'thirty- eight', 'thirty- nine', 'forty', 'forty- one', 'forty- two', 'forty- three', 'forty- four', 'forty- five', 'forty- six', 'forty- seven', 'forty- eight', 'forty- nine', 'fifty', 'fifty- one', 'fifty- two', 'fifty- three', 'fifty- four', 'fifty- five', 'fifty- six', 'fifty- seven', 'fifty- eight', 'fifty- nine', 'sixty', 'sixty- one', 'sixty- two', 'sixty- three', 'sixty- four', 'sixty- five', 'sixty- six', 'sixty- seven', 'sixty- eight', 'sixty- nine', 'seventy', 'seventy- one', 'seventy- two', 'seventy- three', 'seventy- four', 'seventy- five', 'seventy- six', 'seventy- seven', 'seventy- eight', 'seventy- nine', 'eighty', 'eighty- one', 'eighty- two', 'eighty- three', 'eighty- four', 'eighty- five', 'eighty- six', 'eighty- seven', 'eighty- eight', 'eighty- nine', 'ninety', 'ninety-one', 'ninety- two', 'ninety- three', 'ninety- four', 'ninety- five', 'ninety- six', 'ninety- seven', 'ninety- eight', 'ninety- nine', 'hundred']
ttsx = pyttsx3.init()
voices = ttsx.getProperty("voices")
flags = True
read_num = 0
is_pause = False
tmp_wlist = []
words_list = []
voice = 2
if len(voices) >= 3 :
    while "English" not in voices[voice].name:
        voice += 1

try:
    if(os.path.exists(dir_path) == False):
        os.mkdir(dir_path)
except:
    pass
ttsx.setProperty("rate", 120)
def start_read():
    global flags
    global read_num
    global is_pause
    global tmp_wlist
    global words_list
    t = scale.get()
    flags = True
    word_file = var_combox.get() + ".txt"
    file = open(dir_path+"\\{}".format(word_file),'r',encoding="utf-8")
    if (is_pause == False):
        read_num = 0
        words_list = file.read().split("\n")
        if(var_choose.get() == "random"):
            random.shuffle(words_list)
        if(var_entry.get() != ""):
            words_list = words_list[0:int(var_entry.get())]
        tmp_wlist = words_list[:]
        ttsx.say("单词听写现在开始")
        ttsx.runAndWait()
    is_pause = False
    file.close()
    time.sleep(2)
    if(flags == True):
        for word in words_list:
            ttsx.setProperty("voice",voices[1].id)
            ttsx.say("Number {}".format(read_num_list[read_num]))
            ttsx.runAndWait()
            if(flags == False):
                break
            time.sleep(0.3)
            ttsx.say(tmp_wlist[0])
            ttsx.runAndWait()
            if(flags == False):
                break
            time.sleep(1)
            if len(voices)>=3:
                ttsx.setProperty("voice",voices[voice].id)
            ttsx.say("Number {}".format(read_num_list[read_num]))
            ttsx.runAndWait()
            if(flags == False):
                break
            time.sleep(0.3)
            ttsx.say(tmp_wlist[0])
            ttsx.runAndWait()
            if(flags == False):
                break
            time.sleep(t)


            if(flags == False):
                break
            tmp_wlist.remove(word)
            read_num += 1
    if (is_pause == False):
        time.sleep(1)
        ttsx.setProperty("voice",voices[0].id)
        ttsx.say("单词听写结束")
        ttsx.runAndWait()


def pause_read():
    global flags
    global is_pause
    flags = False
    is_pause = True
    time.sleep(2)
    ttsx.setProperty("voice",voices[0].id)
    ttsx.say("单词听写暂停")
    ttsx.runAndWait()
def exchange():
    global flags
    flags = False
def answer_show():
    if words_list != []:
        num = 1
        tmp_s = words_list[:]
        if var_entry.get() != "":
            tmp_s = tmp_s[0:int(var_entry.get())]
        file = open("D:\\{}单词听写答案{}.txt".format(var_combox.get(),var_entry.get()),"w")
        for i in tmp_s:
            file.write(str(num) + "." + i + "\n")
            num += 1
        file.close()
def validate_check(new_value):
    return new_value.isdigit() or new_value == ""
def translate_():

    if re.search("\\S",tran_E_E.get("1.0", tk.END))  and re.search("\\S",tran_E_C.get("1.0", tk.END) ) == None :
        tran_E_C.replace("1.0", tk.END,translate.Translator(from_lang="English",to_lang="Chinese").translate(tran_E_E.get("1.0", tk.END)))
    if re.search("\\S",tran_E_C.get("1.0", tk.END))  and re.search("\\S",tran_E_E.get("1.0", tk.END) ) == None :
        tran_E_E.replace("1.0", tk.END,translate.Translator(from_lang="Chinese",to_lang="English").translate(tran_E_C.get("1.0", tk.END)))

def translate_r():
    tran_E_E_S = tran_E_E.get("1.0", tk.END)
    tran_E_C_S = tran_E_C.get("1.0", tk.END)

    ttsx.setProperty("voice",voices[1].id)
    ttsx.say(tran_E_E_S)
    ttsx.runAndWait()

    time.sleep(1)

    ttsx.setProperty("voice",voices[2].id)
    ttsx.say(tran_E_E_S)
    ttsx.runAndWait()

    time.sleep(1)

    ttsx.setProperty("voice",voices[0].id)
    ttsx.say(tran_E_C_S)
    ttsx.runAndWait()




txt_list = os.listdir(dir_path)
options = []
for file_name in txt_list:
    if(".txt" in file_name):
        file_name = file_name.replace(".txt",'')
        options.append(file_name)

root = tk.Tk()
root.resizable(False, False)
root.title("Dev by B1ank")
root.geometry("500x300")

var_combox = tk.StringVar()
var_choose = tk.StringVar()
var_label = tk.StringVar()
var_entry = tk.StringVar()
var_choose.set("random")
combox = ttk.Combobox(root,values=options,textvariable=var_combox)
combox.current(0)
random_choose = ttk.Radiobutton(root,text="随机",variable=var_choose,value="random")
order_choose = ttk.Radiobutton(root,text="顺序",variable=var_choose,value="order")
scale = tk.Scale(root,from_=0,to=5,resolution=1,orient=tk.HORIZONTAL)
entry = ttk.Entry(root,textvariable=var_entry,validate = "key", validatecommand = (root.register(validate_check), '%P'))
scale.set(2)
open_b = ttk.Button(root,text="打开",command=lambda :os.startfile(dir_path))
pause_b = ttk.Button(root,text="暂停",command=lambda :thread.Thread(target=pause_read).start())
start_b = ttk.Button(root,text="开始",command=lambda :thread.Thread(target=start_read).start())
close_b = ttk.Button(root,text="结束",command=exchange)
show_b = ttk.Button(root,text="生成答案",command=answer_show)
tran_b = ttk.Button(root,text="翻译",command=lambda :thread.Thread(target=translate_).start())
tran_E_E = tk.Text(root, wrap="word", width=25, height=4)
tran_E_C = tk.Text(root, wrap="word", width=25, height=4)
tran_b_r = ttk.Button(root,text="朗读",command=lambda :thread.Thread(target=translate_r()).start())

ttk.Label(root,text="英文          中文").grid(row=7,column=2)
tran_b_r.grid(row=8,column=2)
tran_b.grid(row=6,column=2)
tran_E_E.grid(ipady=30,row=6,column=0,rowspan=3,columnspan=2)
tran_E_C.grid(ipady=30,row=6,column=3,rowspan=3)
combox.grid(row=0,column=0,columnspan=2)
random_choose.grid(row=1,column=0)
order_choose.grid(row=1,column=1)
entry.grid(row=3,column=0,columnspan=2)
scale.grid(row=3,column=2)
ttk.Label(root,text="单词数量                        时间间隔").grid(row=2,column=0,columnspan=3)
open_b.grid(row=0,column=2)
pause_b.grid(row=4,column=0)
start_b.grid(row=4,column=1)
close_b.grid(row=4,column=2)
show_b.grid(row=5,column=0)
root.mainloop()