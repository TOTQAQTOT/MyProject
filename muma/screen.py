import json
import os
import socket
import threading
import time
from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
import logging
from werkzeug.serving import make_server
# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

# 禁用SocketIO日志
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
class screen:
    def __init__(self):
        self.is_webrunning = False
    def screen_view(self,server_socket:socket,client_socket:socket,command_):
        if command_ != "exitsv":
            global last_modified
            self.isrun = True
            client_socket.sendall("screenview".encode("utf-8"))
            self.start_web_server()
        try:
            while True:
                size = client_socket.recv(4)
                image_size = int.from_bytes(size, byteorder='big')
                receive = b""
                remaining = image_size
                while remaining > 0 and self.isrun:
                    data = client_socket.recv(4096)
                    if not data:
                        print("传输中断")
                        break
                    receive += data
                    remaining -= len(data)
                with lock:
                    with open("D:\\b.jpg", "wb") as f:
                        f.write(receive)
                if remaining == 0:  # 确保接收完整
                    with lock:
                        # 更新时间戳并通知前端
                        last_modified = time.time()
                        socketio.emit('image_updated', {'timestamp': last_modified})
        except Exception as e:
            print(e)
    def stop_web_server(self):
        if self.is_webrunning:
            # 停止SocketIO服务
            socketio.stop()
            self.web_thread.join(timeout=1.0)
            self.is_webrunning = False
            print("Web服务已停止")
    def start_web_server(self):
        if not self.is_webrunning:
            self.web_thread = threading.Thread(
            target=lambda:socketio.run(
                app,
                host='0.0.0.0',
                port=WEB_PORT,
                debug=False,
                allow_unsafe_werkzeug=True
            ),daemon=True)
            self.web_thread.start()
            self.is_webrunning=True
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