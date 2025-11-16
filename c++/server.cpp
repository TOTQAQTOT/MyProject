#include <iostream>
#include <winsock2.h>
#include <easyx.h>
#pragma comment(lib,"ws2_32.lib")
using namespace std;
struct Hs {
    int type;
    int size;
};
int main() {
    initgraph(1280,720);
    IMAGE img;
    WSADATA wsadata;
    WSAStartup(MAKEWORD(2,2),&wsadata);
    SOCKET server_socket = socket(AF_INET,SOCK_STREAM,0);
    sockaddr_in server_in;
    server_in.sin_family = AF_INET;
    server_in.sin_addr.s_addr = INADDR_ANY;
    server_in.sin_port = htons(8080);
    bind(server_socket,(SOCKADDR*)&server_in,sizeof(server_in));
    listen(server_socket,5);
    sockaddr_in client_in;
    int client_in_len = sizeof(client_in);
    while (true) {
        SOCKET client_socket = accept(server_socket,(SOCKADDR*)&client_in,&client_in_len);
        while (true) {
            struct Hs hdr;

            if (recv(client_socket,(char*)&hdr,sizeof(hdr),0)<=0)break;
            if (hdr.type ==0) {

            }else if (hdr.type == 1) {
                FILE* fp = fopen("D:\\s.jpg","wb");
                char buff[4096] = {0};
                int size = hdr.size;
                while (size>0) {
                    int ret = recv(client_socket,buff,size<4096?size:4096,0);
                    if (ret <=0) {
                        fclose(fp);
                        goto end;
                    }
                    size -= ret;
                    if (fp != nullptr) {
                        fwrite(buff,1,ret,fp);
                    }
                }
                if (fp!=nullptr) {
                    fclose(fp);
                }
            }
            loadimage(&img,"D:\\s.jpg",getwidth(),getheight());
            putimage(0,0,&img);
        }
        end:
        closesocket(client_socket);
    }

    closesocket(server_socket);
    WSACleanup();

    return 0;
}