from tkinter import ttk
import tkinter as tk
from tkinter import ttk
import os
class windowsshow:
    def __init__(self):
        self.isrun = True
        self.root = tk.Tk()
        self.root.title("BlackWind v1 by b1ank")
        self.root.geometry("1000x500")

        self.frame1 = ttk.Frame(self.root,)

        self.menu_bar = tk.Menu(self.root)

        self.programe = tk.Menu(self.menu_bar, tearoff=0)
        self.programe.add_command(label="打开目录", command=lambda: os.system("explorer.exe D:\\BlackWind"))
        self.programe.add_separator()
        self.programe.add_command(label="退出")
        self.menu_bar.add_cascade(label="程序", menu=self.programe)

        self.help = tk.Menu(self.menu_bar, tearoff=0)
        self.help.add_command(label="关于")
        self.help.add_command(label="帮助文档")
        self.menu_bar.add_cascade(label="帮助", menu=self.help)
        self.root.config(menu=self.menu_bar)
        self.root.columnconfigure(0, minsize=100)
        self.root.columnconfigure(1, minsize=40)
        ttk.Label(self.root, text="客户端列表").grid(row=0, column=0)
        ttk.Label(self.root, text="主机名").grid(row=0, column=2)
        # ttk.Label(self.root,text=f"{self.client_address[0]}:{self.client_address[1]}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self, tearoff=0)

        # 添加菜单选项
        self.context_menu.add_command(label="选项1", command=self.option1)
        self.context_menu.add_command(label="选项2", command=self.option2)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="关于", command=self.about)

    def select_button(self, event):
        """选中按钮（变蓝色）"""
        self.is_selected = True
        self.action_button.config(bg="#4a90e2", fg="white")  # 蓝色背景+白色文字
        # 阻止事件冒泡，避免触发主窗口的取消选中
        return "break"

    def select_and_show_menu(self, event):
        """选中按钮并显示菜单"""
        self.select_button(event)  # 先选中
        # 在鼠标位置显示菜单
        self.context_menu.post(event.x_root, event.y_root)
        # 阻止事件冒泡
        return "break"

    def check_deselect(self, event):
        """检查是否需要取消选中（点击了其他区域）"""
        # 如果当前是选中状态，且点击的不是按钮本身，则取消选中
        if self.is_selected and event.widget != self.action_button:
            self.deselect_button()

    def deselect_button(self):
        """取消选中（恢复透明）"""
        self.is_selected = False
        self.action_button.config(bg=self.parent_bg, fg="black")  # 恢复透明样式
    def on_close(self):
        self.isrun = False
        # if self.t1.is_alive():
        #     self.t1.join()
        self.root.destroy()
