---
name: memory-forensics
description: 掌握内存取证技术，包括内存获取、进程分析和使用 Volatility 及相关工具进行工件提取。当分析内存转储、调查事件或从 RAM 捕获中进行恶意软件分析时使用。
---

# 内存取证

用于事件响应和恶意软件分析的内存转储获取、分析和工件提取的全面技术。

## 内存获取

### 在线获取工具

#### Windows

```powershell
# WinPmem（推荐）
winpmem_mini_x64.exe memory.raw

# DumpIt
DumpIt.exe

# Belkasoft RAM Capturer
# 基于 GUI，输出 raw 格式

# Magnet RAM Capture
# 基于 GUI，输出 raw 格式
```

#### Linux

```bash
# LiME（Linux 内存提取器）
sudo insmod lime.ko "path=/tmp/memory.lime format=lime"

# /dev/mem（有限，需要权限）
sudo dd if=/dev/mem of=memory.raw bs=1M

# /proc/kcore（ELF 格式）
sudo cp /proc/kcore memory.elf
```

#### macOS

```bash
# osxpmem
sudo ./osxpmem -o memory.raw

# MacQuisition（商业工具）
```

### 虚拟机内存

```bash
# VMware：.vmem 文件即为原始内存
cp vm.vmem memory.raw

# VirtualBox：使用调试控制台
vboxmanage debugvm "VMName" dumpvmcore --filename memory.elf

# QEMU
virsh dump <domain> memory.raw --memory-only

# Hyper-V
# 检查点包含内存状态
```

## Volatility 3 框架

### 安装和设置

```bash
# 安装 Volatility 3
pip install volatility3

# 安装符号表（Windows）
# 从 https://downloads.volatilityfoundation.org/volatility3/symbols/ 下载

# 基本用法
vol -f memory.raw <plugin>

# 带符号路径
vol -f memory.raw -s /path/to/symbols windows.pslist
```

### 核心插件

#### 进程分析

```bash
# 列出进程
vol -f memory.raw windows.pslist

# 进程树（父子关系）
vol -f memory.raw windows.pstree

# 隐藏进程检测
vol -f memory.raw windows.psscan

# 进程内存转储
vol -f memory.raw windows.memmap --pid <PID> --dump

# 进程环境变量
vol -f memory.raw windows.envars --pid <PID>

# 命令行参数
vol -f memory.raw windows.cmdline
```

#### 网络分析

```bash
# 网络连接
vol -f memory.raw windows.netscan

# 网络连接状态
vol -f memory.raw windows.netstat
```

#### DLL 和模块分析

```bash
# 每个进程加载的 DLL
vol -f memory.raw windows.dlllist --pid <PID>

# 查找隐藏/注入的 DLL
vol -f memory.raw windows.ldrmodules

# 内核模块
vol -f memory.raw windows.modules

# 模块转储
vol -f memory.raw windows.moddump --pid <PID>
```

#### 内存注入检测

```bash
# 检测代码注入
vol -f memory.raw windows.malfind

# VAD（虚拟地址描述符）分析
vol -f memory.raw windows.vadinfo --pid <PID>

# 转储可疑内存区域
vol -f memory.raw windows.vadyarascan --yara-rules rules.yar
```

#### 注册表分析

```bash
# 列出注册表配置单元
vol -f memory.raw windows.registry.hivelist

# 打印注册表键
vol -f memory.raw windows.registry.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"

# 转储注册表配置单元
vol -f memory.raw windows.registry.hivescan --dump
```

#### 文件系统工件

```bash
# 扫描文件对象
vol -f memory.raw windows.filescan

# 从内存转储文件
vol -f memory.raw windows.dumpfiles --pid <PID>

# MFT 分析
vol -f memory.raw windows.mftscan
```

### Linux 分析

```bash
# 进程列表
vol -f memory.raw linux.pslist

# 进程树
vol -f memory.raw linux.pstree

# Bash 历史
vol -f memory.raw linux.bash

# 网络连接
vol -f memory.raw linux.sockstat

# 已加载的内核模块
vol -f memory.raw linux.lsmod

# 挂载点
vol -f memory.raw linux.mount

# 环境变量
vol -f memory.raw linux.envars
```

### macOS 分析

```bash
# 进程列表
vol -f memory.raw mac.pslist

# 进程树
vol -f memory.raw mac.pstree

# 网络连接
vol -f memory.raw mac.netstat

# 内核扩展
vol -f memory.raw mac.lsmod
```

## 分析工作流

### 恶意软件分析工作流

```bash
# 1. 初始进程概览
vol -f memory.raw windows.pstree > processes.txt
vol -f memory.raw windows.pslist > pslist.txt

# 2. 网络连接
vol -f memory.raw windows.netscan > network.txt

# 3. 检测注入
vol -f memory.raw windows.malfind > malfind.txt

# 4. 分析可疑进程
vol -f memory.raw windows.dlllist --pid <PID>
vol -f memory.raw windows.handles --pid <PID>

# 5. 转储可疑可执行文件
vol -f memory.raw windows.pslist --pid <PID> --dump

# 6. 从转储中提取字符串
strings -a pid.<PID>.exe > strings.txt

# 7. YARA 扫描
vol -f memory.raw windows.yarascan --yara-rules malware.yar
```

### 事件响应工作流

```bash
# 1. 事件时间线
vol -f memory.raw windows.timeliner > timeline.csv

# 2. 用户活动
vol -f memory.raw windows.cmdline
vol -f memory.raw windows.consoles

# 3. 持久化机制
vol -f memory.raw windows.registry.printkey \
    --key "Software\Microsoft\Windows\CurrentVersion\Run"

# 4. 服务
vol -f memory.raw windows.svcscan

# 5. 计划任务
vol -f memory.raw windows.scheduled_tasks

# 6. 最近文件
vol -f memory.raw windows.filescan | grep -i "recent"
```

## 数据结构

### Windows 进程结构

```c
// EPROCESS（执行进程）
typedef struct _EPROCESS {
    KPROCESS Pcb;                    // 内核进程块
    EX_PUSH_LOCK ProcessLock;
    LARGE_INTEGER CreateTime;
    LARGE_INTEGER ExitTime;
    // ...
    LIST_ENTRY ActiveProcessLinks;   // 双向链表
    ULONG_PTR UniqueProcessId;       // PID
    // ...
    PEB* Peb;                        // 进程环境块
    // ...
} EPROCESS;

// PEB（进程环境块）
typedef struct _PEB {
    BOOLEAN InheritedAddressSpace;
    BOOLEAN ReadImageFileExecOptions;
    BOOLEAN BeingDebugged;           // 反调试检查
    // ...
    PVOID ImageBaseAddress;          // 可执行文件基地址
    PPEB_LDR_DATA Ldr;              // 加载器数据（DLL 列表）
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters;
    // ...
} PEB;
```

### VAD（虚拟地址描述符）

```c
typedef struct _MMVAD {
    MMVAD_SHORT Core;
    union {
        ULONG LongFlags;
        MMVAD_FLAGS VadFlags;
    } u;
    // ...
    PVOID FirstPrototypePte;
    PVOID LastContiguousPte;
    // ...
    PFILE_OBJECT FileObject;
} MMVAD;

// 内存保护标志
#define PAGE_EXECUTE           0x10
#define PAGE_EXECUTE_READ      0x20
#define PAGE_EXECUTE_READWRITE 0x40
#define PAGE_EXECUTE_WRITECOPY 0x80
```

## 检测模式

### 进程注入指标

```python
# Malfind 指标
# - PAGE_EXECUTE_READWRITE 保护（可疑）
# - 非镜像 VAD 区域中的 MZ 头
# - 分配起始处的 Shellcode 模式

# 常见注入技术
# 1. 经典 DLL 注入
#    - VirtualAllocEx + WriteProcessMemory + CreateRemoteThread

# 2. 进程镂空
#    - CreateProcess（SUSPENDED）+ NtUnmapViewOfSection + WriteProcessMemory

# 3. APC 注入
#    - QueueUserAPC 目标为可告警线程

# 4. 线程执行劫持
#    - SuspendThread + SetThreadContext + ResumeThread
```

### Rootkit 检测

```bash
# 比较进程列表
vol -f memory.raw windows.pslist > pslist.txt
vol -f memory.raw windows.psscan > psscan.txt
diff pslist.txt psscan.txt  # 隐藏进程

# 检查 DKOM（直接内核对象操作）
vol -f memory.raw windows.callbacks

# 检测钩子函数
vol -f memory.raw windows.ssdt  # 系统服务描述符表

# 驱动分析
vol -f memory.raw windows.driverscan
vol -f memory.raw windows.driverirp
```

### 凭据提取

```bash
# 转储哈希（需要先运行 hivelist）
vol -f memory.raw windows.hashdump

# LSA 机密
vol -f memory.raw windows.lsadump

# 缓存的域凭据
vol -f memory.raw windows.cachedump

# Mimikatz 风格提取
# 需要特定插件/工具
```

## YARA 集成

### 编写内存 YARA 规则

```yara
rule Suspicious_Injection
{
    meta:
        description = "检测常见注入 shellcode"

    strings:
        // 常见 shellcode 模式
        $mz = { 4D 5A }
        $shellcode1 = { 55 8B EC 83 EC }  // 函数序言
        $api_hash = { 68 ?? ?? ?? ?? 68 ?? ?? ?? ?? E8 }  // 压入哈希，调用

    condition:
        $mz at 0 or any of ($shellcode*)
}

rule Cobalt_Strike_Beacon
{
    meta:
        description = "检测内存中的 Cobalt Strike beacon"

    strings:
        $config = { 00 01 00 01 00 02 }
        $sleep = "sleeptime"
        $beacon = "%s (admin)" wide

    condition:
        2 of them
}
```

### 扫描内存

```bash
# 扫描所有进程内存
vol -f memory.raw windows.yarascan --yara-rules rules.yar

# 扫描特定进程
vol -f memory.raw windows.yarascan --yara-rules rules.yar --pid 1234

# 扫描内核内存
vol -f memory.raw windows.yarascan --yara-rules rules.yar --kernel
```

## 字符串分析

### 提取字符串

```bash
# 基本字符串提取
strings -a memory.raw > all_strings.txt

# Unicode 字符串
strings -el memory.raw >> all_strings.txt

# 从进程转储中定向提取
vol -f memory.raw windows.memmap --pid 1234 --dump
strings -a pid.1234.dmp > process_strings.txt

# 模式匹配
grep -E "(https?://|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})" all_strings.txt
```

### FLOSS 用于混淆字符串

```bash
# FLOSS 提取混淆字符串
floss malware.exe > floss_output.txt

# 从内存转储
floss pid.1234.dmp
```

## 最佳实践

### 获取最佳实践

1. **最小化足迹**：使用轻量级获取工具
2. **记录一切**：记录时间、工具和捕获的哈希值
3. **验证完整性**：捕获后立即计算内存转储的哈希值
4. **监管链**：维护正确的取证处理流程

### 分析最佳实践

1. **从广到深**：先获取概览再深入分析
2. **交叉引用**：对相同数据使用多个插件
3. **时间线关联**：将内存发现与磁盘/网络关联
4. **记录发现**：保留详细笔记和截图
5. **验证结果**：通过多种方法验证发现

### 常见陷阱

- **过时数据**：内存是易失的，应及时分析
- **不完整转储**：验证转储大小与预期 RAM 匹配
- **符号问题**：确保符号文件与操作系统版本匹配
- **涂抹**：获取期间内存可能发生变化
- **加密**：某些数据在内存中可能是加密的
