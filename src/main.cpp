#include <windows.h>
#include <psapi.h>
#include <vector>
#include <string>
#include <unordered_map>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "MonitorProcessExit.h"

namespace py = pybind11;


// 进程信息结构体
struct ProcessInfo {
    std::string name;
    unsigned long pid;
    std::string title;  // 新增窗口标题字段
    
    bool operator<(const ProcessInfo& other) const {
        return pid < other.pid;
    }
};

// 获取活动窗口进程（过滤后台服务）
std::vector<ProcessInfo> get_active_processes() {
    std::unordered_map<DWORD, ProcessInfo> processMap;  // 使用pid作为键去重
    
    // 枚举所有顶级窗口
    EnumWindows([](HWND hwnd, LPARAM lparam) -> BOOL {
        auto& map = *reinterpret_cast<std::unordered_map<DWORD, ProcessInfo>*>(lparam);
        
        // 检查窗口可见性（过滤后台服务）
        if (!IsWindowVisible(hwnd)) {
            return TRUE;
        }
        
        // 获取窗口标题
        char title[256];
        GetWindowTextA(hwnd, title, sizeof(title));
        // 转换标题编码（默认为GBK）

        // 跳过无标题窗口
        if (strlen(title) == 0) {
            return TRUE;
        }
        
        DWORD pid;
        GetWindowThreadProcessId(hwnd, &pid);
        
        // 跳过系统进程
        if (pid == 0) {
            return TRUE;
        }
        
        // 如果该pid已存在，只更新标题（合并多窗口）
        if (auto it = map.find(pid); it != map.end()) {
            // 追加标题（使用分隔符）
            if (!it->second.title.empty()) {
                it->second.title += " | ";
            }
            it->second.title += title;
            return TRUE;
        }
        
        // 新进程：获取进程名
        HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
        if (!hProcess) {
            return TRUE;
        }
        
        char filename[MAX_PATH];
        if (GetModuleFileNameExA(hProcess, NULL, filename, MAX_PATH)) {
            // 提取进程名
            std::string fullPath(filename);
            size_t lastSep = fullPath.find_last_of("\\/");
            std::string processName = (lastSep == std::string::npos) 
                ? fullPath 
                : fullPath.substr(lastSep + 1);
            // 添加到map
            map[pid] = {processName, pid, title};
        }
        CloseHandle(hProcess);
        return TRUE;
    }, reinterpret_cast<LPARAM>(&processMap));
    
    // 转换为vector
    std::vector<ProcessInfo> result;
    for (auto& [pid, info] : processMap) {
        result.push_back(info);
    }
    return result;
}

// 更新Pybind11绑定
PYBIND11_MODULE(Time_collection_tools, m) {
    py::class_<ProcessInfo>(m, "ProcessInfo")
        .def_readonly("name", &ProcessInfo::name)
        .def_readonly("pid", &ProcessInfo::pid)
        .def_readonly("title", &ProcessInfo::title)  // 添加标题字段
        .def("__repr__", [](const ProcessInfo& p) {
            
            return "ProcessInfo(name='" + p.name + "', pid=" + std::to_string(p.pid) 
                   + ", title='" + p.title + "')";
        });
    
    m.def("get_active_processes", &get_active_processes, 
          "获取所有不重复的前台活动进程信息（包含窗口标题）");
    m.def("monitor_process_exit", &MonitorProcessExit,"监控进程退出事件");
}