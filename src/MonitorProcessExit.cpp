#include <windows.h>
#include <tlhelp32.h>
#include <iostream>
#include "MonitorProcessExit.h"

// 在进程运行时获取其创建时间
static ULONGLONG GetProcessCreateTime(DWORD pid) {
    HANDLE hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    if (hProcess == NULL) return 0;

    FILETIME createTime, exitTime, kernelTime, userTime;
    if (!GetProcessTimes(hProcess, &createTime, &exitTime, &kernelTime, &userTime)) {
        CloseHandle(hProcess);
        return 0;
    }

    ULARGE_INTEGER ulCreate;
    ulCreate.LowPart = createTime.dwLowDateTime;
    ulCreate.HighPart = createTime.dwHighDateTime;
    
    CloseHandle(hProcess);
    return ulCreate.QuadPart;
}

double MonitorProcessExit(DWORD targetPid) {
    // 在进程运行时获取其创建时间
    ULONGLONG createTime = GetProcessCreateTime(targetPid);
    if (createTime == 0) {
        std::cerr << "无法获取进程创建时间\n";
        return -1.0;
    }

    while (true) {
        HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (hSnapshot == INVALID_HANDLE_VALUE) {
            std::cerr << "CreateToolhelp32Snapshot失败\n";
            return -1.0;
        }

        PROCESSENTRY32 pe;
        pe.dwSize = sizeof(PROCESSENTRY32);
        bool processExists = false;

        if (Process32First(hSnapshot, &pe)) {
            do {
                if (pe.th32ProcessID == targetPid) {
                    processExists = true;
                    break;
                }
            } while (Process32Next(hSnapshot, &pe));
        }
        CloseHandle(hSnapshot);

        if (!processExists) {
            // 进程已退出 - 使用预存的创建时间计算运行时长
            FILETIME currentTime;
            GetSystemTimeAsFileTime(&currentTime);
            
            ULARGE_INTEGER ulCurrent;
            ulCurrent.LowPart = currentTime.dwLowDateTime;
            ulCurrent.HighPart = currentTime.dwHighDateTime;

            ULONGLONG diff = ulCurrent.QuadPart - createTime;
            double seconds = static_cast<double>(diff) / 10000000.0; // 转换为秒
            return seconds;
        }

        Sleep(1000);
    }
}