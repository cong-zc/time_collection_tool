import Time_collection_tools

def 监测进程是否退出(进程id):
    进程状态 = Time_collection_tools.monitor_process_exit(进程id)
    print(f"进程 {进程id} 已退出,运行时间{进程状态}")

# if __name__ == "__main__":
#     监测进程是否退出(9944)