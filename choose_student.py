import os
import time
import tkinter
import thread.thread
import tkinter.ttk as ttk
import random
flag = False
def stop():
    global flag
    flag = False
def start():
    global flag
    global student_list
    global String_Var
    if flag == False:
        flag = True
        if combobox_var.get() == "全部":
            while True:
                if flag == False:
                    break

                file_name = student_list[random.randint(0,len(student_list)-1)].replace(".txt","")

                file = open(dir_path + "\\" + file_name + ".txt","r")
                student_name_list = file.read().split("\n")
                file.close()

                String_Var.set(file_name + "-" + student_name_list[random.randint(0,len(student_name_list)-1)])
                time.sleep(0.02)
        else:
            student_txt = dir_path + "\\" + combobox_var.get() + ".txt"
            file = open(student_txt,"r",encoding="utf-8")
            student_name_list = file.read().split("\n")
            file.close()
            while True:
                if flag == False:
                    break
                String_Var.set(combobox_var.get() + "-" + student_name_list[random.randint(0,len(student_name_list)-1)])
                time.sleep(0.02)
        flag = False



root = tkinter.Tk()
root.title("Dev by B1ank")
dir_path = "C:\\student_list"
try:
    if(os.path.exists(dir_path) == False):
        os.mkdir(dir_path)
except:
    pass
options = ["全部"]
student_list = os.listdir(dir_path)
for file_name in student_list:
    if ".txt" in file_name:
        file_name = file_name.replace(".txt",'')
        options.append(file_name)
String_Var = tkinter.StringVar()
String_Var.set("")
combobox_var = tkinter.StringVar()
combobox_var.set("全部")

combobox = ttk.Combobox(root,values=options,textvariable=combobox_var)
stop_b = ttk.Button(root,text="停止",command=lambda :thread.Thread(target=stop).start())
start_b = ttk.Button(root,text="开始",command=lambda :thread.Thread(target=start).start())
label = tkinter.Label(root,textvariable=String_Var,background="#FFD39B",font=("Helvetica", 20, "bold"),width=20)
label.grid(row=0,column=0,columnspan=3)
combobox.grid(row=3,column=0)
start_b.grid(row=3,column=1)
stop_b.grid(row=3,column=2)
root.mainloop()
