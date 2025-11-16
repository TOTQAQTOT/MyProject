cmake_minimum_required(VERSION 3.31)
project(c__)

set(CMAKE_CXX_STANDARD 20)

link_libraries(libeasyx.a libgdi32.a libole32.a)


#add_executable(main main.cpp)
#target_link_libraries(main libeasyx.a ws2_32)


add_executable(client client.cpp)
target_link_libraries(client ws2_32)


