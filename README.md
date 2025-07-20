## 编译方式:
1. 安装xmake
2. 执行xmake
3. 将编译的pyd文件复制到scripts目录下
4. 打包成exe
   1. 安装pyinstaller
   2. pyinstaller --add-data "Time_collection_tools.pyd;." --name=时间统计器 tray.py

## TIPS
1. include文件夹的内容是pybind11源文件