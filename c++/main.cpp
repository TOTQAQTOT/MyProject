#include <bits/stdc++.h>
using namespace std;
int main() {
    char a[] = "showwindow hello";
    char b[strlen(a)-10]={0};
    strncpy(b,a+11,strlen(a)-11);
    cout << b;
    return 0;
}