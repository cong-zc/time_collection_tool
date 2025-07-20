import Time_collection_tools

import time
import psutil
import json

from datetime import timedelta

def 获取进程信息():
    processes = Time_collection_tools.get_active_processes()
    
    print(f"发现 {len(processes)} 个活动进程:")
    # for i, proc in enumerate(processes):
    #     print(f"{i+1}. {proc.name} (PID: {proc.pid})")
    
    # 转换为字典格式便于其他Python模块使用
    process_dict = {proc.name: proc.pid for proc in processes}
    return process_dict

def get_runtime_by_pid(pid):
    try:
        process = psutil.Process(pid)  # 根据PID获取进程对象
        create_time = process.create_time()  # 获取进程启动时间戳（Unix纪元秒数）
        current_time = time.time()
        runtime_seconds = current_time - create_time  # 计算运行时长（秒）
        print(f"进程 {pid} 已运行 {timedelta(seconds=runtime_seconds)}")
        # 计算运行时间,时，分，秒
        runtime = seconds_to_hms_divmod(runtime_seconds)
        return runtime
    except psutil.NoSuchProcess:
        return "进程不存在或已终止"
    except psutil.AccessDenied:
        return "权限不足，请以管理员身份运行脚本"

def seconds_to_hms_divmod(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds_remaining = divmod(remainder, 60)
    print(f"进程已运行 {hours}小时{minutes}分")
    
    return f"{hours}小时{minutes}分"

# def 监测进程是否退出(_进程名称,进程id):
#     print(f"正在监测进程 {_进程名称} (PID: {进程id})")
#     进程状态 = Time_collection_tools.monitor_process_exit(进程id)
#     print(f"进程 {进程id} 已退出,运行时间{进程状态}")
#     # 将数据写入json文件
#     data = {
#         '进程名称':_进程名称,
#         '进程ID':进程id,
#         '运行时长':进程状态
#     }
#     with open('./db/process_time.json', 'w',encoding='utf-8') as f:
#         json.dump(data,f,indent=4,ensure_ascii=False)