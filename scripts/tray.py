import pystray
import os
import threading
from PIL import Image, ImageDraw
from pystray import MenuItem as item
from datetime import datetime

import json

import Time_collection_tools
from tools import 获取进程信息, get_runtime_by_pid

# 全局变量存储进程信息和菜单
process_dict = {}
process_menu = []

# 添加全局退出标志
exit_flag = False

# 选中的进程名称
进程名称 = "未选择程序"
进程PID = -1

# 创建圆形图标
def create_icon():
    """创建圆形图标"""
    image = Image.new('RGB', (64, 64), 'white')
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, 64, 64), fill='blue')
    return image

# 菜单事件处理
def on_quit(icon):
    """退出程序"""
    global exit_flag
    icon.stop()
    exit_flag = True  # 设置退出标志

# 显示选中的进程名称
def select_process(icon):
    '''显示选中的进程名称'''
    # 显示选中的进程名称
    print(f'选中的进程: {进程名称}')

def generate_menu(data):
    """根据字典数据生成动态子菜单"""
    global process_menu
    
    # 清空现有菜单项
    process_menu = []
    
    # 为每个进程创建菜单项
    for name, pid in data.items():
        # 使用闭包函数确保正确的pid传递
        def create_action(n, p):
            def action(icon):
                # 显示进程详细信息
                runtime = get_runtime_by_pid(p)
                icon.notify(
                    message=f"进程名: {n}\nPID: {p}\n运行时间: {runtime}",
                    title="进程详情"
                )
                global 进程名称,进程PID
                进程名称 = n
                进程PID = p
                on_refresh(icon)
                print(f"点击进程: {n}, PID={p}, 运行时间: {runtime}秒")
            return action
        
        # 创建菜单项
        process_menu.append(
            item(
                text=f"{name} (PID: {pid})",
                action=create_action(name, pid)
            )
        )
    
    # 添加刷新按钮
    process_menu.append(item("刷新进程列表", on_refresh))
    
    return process_menu

def get_process_time(icon):
    """显示示例进程的运行时间"""
    runtime = get_runtime_by_pid(进程PID)
    print(f"进程运行时长: {runtime}")

def on_about(icon):
    """显示关于信息"""
    icon.notify(
        message="进程监控工具 v1.0\n可查看系统进程信息",
        title="关于"
    )
    

def on_refresh(icon):
    """刷新进程列表"""
    global  process_menu,process_dict
    print("刷新进程列表...")
    
    # 获取新的进程信息
    process_dict = 获取进程信息()
    

    
    # # 生成新菜单
    new_menu = generate_menu(process_dict)
    
    # 更新托盘菜单
    icon.menu = pystray.Menu(
        
        item(f"选择的程序: {进程名称}(PID:{进程PID})", None, enabled=False),
        item('显示进程运行时间', get_process_time),
        item('开始监测进程', start_monitor),
        item('所有前端进程', pystray.Menu(*new_menu)),
        item('关于', on_about),
        item('退出', on_quit)
    )


    

# 开始监测进程运行时间
def start_monitor(icon):
    """开始监测进程运行时间"""
    global 进程名称,进程PID
    if 进程PID == -1:
        print(f'请先选择进程')
        return
    # 监测进程是否退出(进程名称,进程PID)
    print(f"正在监测进程 {进程名称} (PID: {进程PID})")
    进程状态 = Time_collection_tools.monitor_process_exit(进程PID)
    print(f"进程 {进程PID} 已退出,运行时间{进程状态}")
    # 将数据写入json文件
    data = []
    # 如果不存在则创建
    if not os.path.exists("process_time.json"):
        with open('process_time.json', 'w', encoding='utf-8') as f:
            f.write("[]")
    with open('process_time.json', 'r',encoding='utf-8') as f:
        data = json.load(f)
    data.append({
        '进程名称':进程名称,
        '进程ID':进程PID,
        '运行时长':进程状态,
        '创建时间':datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open('process_time.json', 'w',encoding='utf-8') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)
    print(f'写入文件成功')

    # 刷新进程列表
    进程名称 = "未选择程序"
    进程PID = -1
    on_refresh(icon)

def 构建托盘():
    """构建并运行托盘图标"""
    # 构建托盘图标
    icon = pystray.Icon("my_app")
    icon.icon = create_icon()
    icon.title = "进程监控器"
    
    # 初始菜单（将在刷新后更新）
    icon.menu = pystray.Menu(
        item('加载中...', lambda: None)
    )
    
    # 在独立线程中运行图标
    threading.Thread(
        target=icon.run, 
        daemon=True
    ).start()
    
    # 初始刷新
    on_refresh(icon)
    
    return icon

if __name__ == '__main__':
    # 初始获取进程信息
    process_dict = 获取进程信息()
    print("初始进程信息:", process_dict)
    
    # 构建托盘并运行
    tray_icon = 构建托盘()
    
    try:
        # 修改为检查退出标志的循环
        while not exit_flag:
            # 降低CPU占用，每0.5秒检查一次退出标志
            threading.Event().wait(0.5)
    except KeyboardInterrupt:
        tray_icon.stop()
        print("程序已退出")
    finally:
        # 移除强制退出，让程序自然结束
        print("清理完成，程序退出")