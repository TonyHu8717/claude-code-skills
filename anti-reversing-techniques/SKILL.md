---
name: anti-reversing-techniques
description: 理解软件分析中遇到的反逆向、混淆和保护技术。在分析恶意软件规避技术、为 CTF 挑战实现反调试保护、逆向工程加壳二进制文件或构建需要检测虚拟化环境的安全研究工具时使用此技能。
---

> **仅限授权使用**：此技能包含双重用途安全技术。在进行任何绕过或分析之前：
>
> 1. **验证授权**：确认你拥有软件所有者的明确书面许可，或在合法安全上下文中操作（CTF、授权渗透测试、恶意软件分析、安全研究）
> 2. **记录范围**：确保你的活动在授权定义的范围内
> 3. **法律合规**：理解未经授权绕过软件保护可能违反法律（CFAA、DMCA 反规避等）
>
> **合法用例**：恶意软件分析、授权渗透测试、CTF 竞赛、学术安全研究、分析你拥有/有权使用的软件

# 反逆向技术

理解在授权软件分析、安全研究和恶意软件分析中遇到的保护机制。此知识帮助分析师绕过保护以完成合法分析任务。

高级技术参见 [references/advanced-techniques.md](references/advanced-techniques.md)

---

## 输入 / 输出

**你提供：**

- **二进制路径或样本**：正在分析的可执行文件、DLL 或固件镜像
- **平台**：Windows x86/x64、Linux、macOS、ARM — 影响哪些检查适用
- **目标**：绕过动态分析、识别保护类型、构建检测代码、为 CTF 实现

**此技能产出：**

- **保护识别**：命名技术（如 RDTSC 时序检查、PEB BeingDebugged）及在二进制中的位置
- **绕过策略**：特定的补丁地址、钩子点或工具命令以中和每项检查
- **分析报告**：结构化发现，列出每层保护、严重性和推荐绕过方法
- **代码产物**：Python/IDAPython 脚本、GDB 命令序列或用于绕过或实现检查的 C 桩代码

---

## 反调试技术

### Windows 反调试

#### 基于 API 的检测

```c
// IsDebuggerPresent
if (IsDebuggerPresent()) {
    exit(1);
}

// CheckRemoteDebuggerPresent
BOOL debugged = FALSE;
CheckRemoteDebuggerPresent(GetCurrentProcess(), &debugged);
if (debugged) exit(1);

// NtQueryInformationProcess
typedef NTSTATUS (NTAPI *pNtQueryInformationProcess)(
    HANDLE, PROCESSINFOCLASS, PVOID, ULONG, PULONG);

DWORD debugPort = 0;
NtQueryInformationProcess(
    GetCurrentProcess(),
    ProcessDebugPort,        // 7
    &debugPort,
    sizeof(debugPort),
    NULL
);
if (debugPort != 0) exit(1);

// Debug flags
DWORD debugFlags = 0;
NtQueryInformationProcess(
    GetCurrentProcess(),
    ProcessDebugFlags,       // 0x1F
    &debugFlags,
    sizeof(debugFlags),
    NULL
);
if (debugFlags == 0) exit(1);  // 0 means being debugged
```

**绕过：** 在 x64dbg 中使用 ScyllaHide 插件（自动修补所有常见检查）。手动：强制 `IsDebuggerPresent` 返回 0，将 `PEB.BeingDebugged` 修补为 0，钩取 `NtQueryInformationProcess`。在 IDA 中：`ida_bytes.patch_byte(check_addr, 0x90)`。

#### 基于 PEB 的检测

```c
// Direct PEB access
#ifdef _WIN64
    PPEB peb = (PPEB)__readgsqword(0x60);
#else
    PPEB peb = (PPEB)__readfsdword(0x30);
#endif

// BeingDebugged flag
if (peb->BeingDebugged) exit(1);

// NtGlobalFlag
// Debugged: 0x70 (FLG_HEAP_ENABLE_TAIL_CHECK |
//                 FLG_HEAP_ENABLE_FREE_CHECK |
//                 FLG_HEAP_VALIDATE_PARAMETERS)
if (peb->NtGlobalFlag & 0x70) exit(1);

// Heap flags
PDWORD heapFlags = (PDWORD)((PBYTE)peb->ProcessHeap + 0x70);
if (*heapFlags & 0x50000062) exit(1);
```

**绕过：** 在 x64dbg 中，在 dump 中跟踪 `gs:[60]`（x64）或 `fs:[30]`（x86）。将 `BeingDebugged`（偏移 +2）设为 0；清除 `NtGlobalFlag`（x64 上偏移 +0xBC）。

#### 基于时序的检测

```c
// RDTSC timing
uint64_t start = __rdtsc();
// ... some code ...
uint64_t end = __rdtsc();
if ((end - start) > THRESHOLD) exit(1);

// QueryPerformanceCounter
LARGE_INTEGER start, end, freq;
QueryPerformanceFrequency(&freq);
QueryPerformanceCounter(&start);
// ... code ...
QueryPerformanceCounter(&end);
double elapsed = (double)(end.QuadPart - start.QuadPart) / freq.QuadPart;
if (elapsed > 0.1) exit(1);  // Too slow = debugger

// GetTickCount
DWORD start = GetTickCount();
// ... code ...
if (GetTickCount() - start > 1000) exit(1);
```

**Python 脚本 — 基于时序的反调试检测扫描器：**

```python
#!/usr/bin/env python3
"""Scan a binary for common timing-based anti-debug patterns."""
import re
import sys

PATTERNS = {
    "RDTSC":              rb"\x0f\x31",                    # RDTSC opcode
    "RDTSCP":             rb"\x0f\x01\xf9",                # RDTSCP opcode
    "GetTickCount":       rb"GetTickCount\x00",
    "QueryPerfCounter":   rb"QueryPerformanceCounter\x00",
    "NtQuerySysInfo":     rb"NtQuerySystemInformation\x00",
}

def scan(path: str) -> None:
    data = open(path, "rb").read()
    print(f"Scanning: {path} ({len(data)} bytes)\n")
    for name, pattern in PATTERNS.items():
        hits = [m.start() for m in re.finditer(re.escape(pattern), data)]
        if hits:
            offsets = ", ".join(hex(h) for h in hits[:5])
            print(f"  [{name}] found at: {offsets}")
    print("\nDone. Cross-reference offsets in IDA/Ghidra to find check logic.")

if __name__ == "__main__":
    scan(sys.argv[1])
```

**绕过：** 使用硬件断点（无 INT3 开销），NOP 化比较+条件跳转，通过虚拟机管理程序冻结 RDTSC，或钩取时序 API 返回一致值。

#### 基于异常的检测

```c
// SEH: if debugger is attached it consumes the INT3 exception
// and execution falls through to exit(1) instead of the __except handler
__try { __asm { int 3 } }
__except(EXCEPTION_EXECUTE_HANDLER) { return; }  // Clean: exception handled here
exit(1);  // Dirty: debugger swallowed the exception

// VEH: register handler that self-handles INT3 (increments RIP past INT3)
// Debugger intercepts first, handler never runs → detected
LONG CALLBACK VectoredHandler(PEXCEPTION_POINTERS ep) {
    if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_BREAKPOINT) {
        ep->ContextRecord->Rip++;
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    return EXCEPTION_CONTINUE_SEARCH;
}
```

**绕过**：在 x64dbg 中，为 EXCEPTION_BREAKPOINT 设置"将异常传递给程序"（选项 → 异常 → 添加 0x80000003）。

### Linux 反调试

```c
// ptrace self-trace
if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) == -1) {
    // Already being traced
    exit(1);
}

// /proc/self/status
FILE *f = fopen("/proc/self/status", "r");
char line[256];
while (fgets(line, sizeof(line), f)) {
    if (strncmp(line, "TracerPid:", 10) == 0) {
        int tracer_pid = atoi(line + 10);
        if (tracer_pid != 0) exit(1);
    }
}

// Parent process check
if (getppid() != 1 && strcmp(get_process_name(getppid()), "bash") != 0) {
    // Unusual parent (might be debugger)
}
```

**绕过（LD_PRELOAD 钩子）：**

```bash
# hook.c: long ptrace(int request, ...) { return 0; }
# gcc -shared -fPIC -o hook.so hook.c
LD_PRELOAD=./hook.so ./target
```

**GDB 绕过命令序列：**

```gdb
# 1. Make ptrace(PTRACE_TRACEME) always return 0 (success)
catch syscall ptrace
commands
  silent
  set $rax = 0
  continue
end

# 2. Bypass check after ptrace call: find "cmp rax, 0xffffffff; je <exit>"
#    Clear ZF so the conditional jump is not taken:
#    set $eflags = $eflags & ~0x40

# 3. Bypass /proc/self/status TracerPid check at the open() level
catch syscall openat
commands
  silent
  # If arg contains "status", patch the fd result to /dev/null equivalent
  continue
end

# 4. Bypass parent process name check
set follow-fork-mode child
set detach-on-fork off
```

---

## 反虚拟机检测

### 硬件指纹

```c
// CPUID-based detection
int cpuid_info[4];
__cpuid(cpuid_info, 1);
// Check hypervisor bit (bit 31 of ECX)
if (cpuid_info[2] & (1 << 31)) {
    // Running in hypervisor
}

// CPUID brand string
__cpuid(cpuid_info, 0x40000000);
char vendor[13] = {0};
memcpy(vendor, &cpuid_info[1], 12);
// "VMwareVMware", "Microsoft Hv", "KVMKVMKVM", "VBoxVBoxVBox"

// MAC address prefix
// VMware: 00:0C:29, 00:50:56
// VirtualBox: 08:00:27
// Hyper-V: 00:15:5D
```

### 注册表/文件检测

```c
// Windows registry keys
// HKLM\SOFTWARE\VMware, Inc.\VMware Tools
// HKLM\SOFTWARE\Oracle\VirtualBox Guest Additions
// HKLM\HARDWARE\ACPI\DSDT\VBOX__

// Files
// C:\Windows\System32\drivers\vmmouse.sys
// C:\Windows\System32\drivers\vmhgfs.sys
// C:\Windows\System32\drivers\VBoxMouse.sys

// Processes
// vmtoolsd.exe, vmwaretray.exe
// VBoxService.exe, VBoxTray.exe
```

### 基于时序的虚拟机检测

```c
// VM exits cause timing anomalies
uint64_t start = __rdtsc();
__cpuid(cpuid_info, 0);  // Causes VM exit
uint64_t end = __rdtsc();
if ((end - start) > 500) {
    // Likely in VM (CPUID takes longer)
}
```

**绕过：** 使用裸机环境，加固虚拟机（移除客户工具、随机化 MAC、删除产物文件），在二进制中修补检测分支，或使用带加固设置的 FLARE-VM/REMnux。

高级虚拟机检测（RDTSC 增量校准、VMware 后门端口、虚拟机管理程序叶枚举、客户驱动产物检查）参见 [references/advanced-techniques.md](references/advanced-techniques.md)。

---

## 代码混淆

### 控制流混淆

#### 控制流平坦化

```c
// Original
if (cond) {
    func_a();
} else {
    func_b();
}
func_c();

// Flattened
int state = 0;
while (1) {
    switch (state) {
        case 0:
            state = cond ? 1 : 2;
            break;
        case 1:
            func_a();
            state = 3;
            break;
        case 2:
            func_b();
            state = 3;
            break;
        case 3:
            func_c();
            return;
    }
}
```

**分析方法：**

- 识别状态变量
- 映射状态转换
- 重建原始流程
- 工具：D-810（IDA）、SATURN

#### 不透明谓词

```c
int x = rand();
if ((x * x) >= 0) { real_code(); }   // Always true  → junk_code() is dead
if ((x*(x+1)) % 2 == 1) { junk(); }  // Always false → consecutive product is even
```

**分析方法：** 通过符号执行（angr、Triton）识别不变表达式，或模式匹配已知不透明形式并修剪它们。

### 数据混淆

#### 字符串加密

```c
// XOR encryption
char decrypt_string(char *enc, int len, char key) {
    char *dec = malloc(len + 1);
    for (int i = 0; i < len; i++) {
        dec[i] = enc[i] ^ key;
    }
    dec[len] = 0;
    return dec;
}

// Stack strings
char url[20];
url[0] = 'h'; url[1] = 't'; url[2] = 't'; url[3] = 'p';
url[4] = ':'; url[5] = '/'; url[6] = '/';
// ...
```

**分析方法：**

```python
# FLOSS for automatic string deobfuscation
floss malware.exe

# IDAPython string decryption
def decrypt_xor(ea, length, key):
    result = ""
    for i in range(length):
        byte = ida_bytes.get_byte(ea + i)
        result += chr(byte ^ key)
    return result
```

#### API 混淆

```c
// Dynamic API resolution
typedef HANDLE (WINAPI *pCreateFileW)(LPCWSTR, DWORD, DWORD,
    LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE);

HMODULE kernel32 = LoadLibraryA("kernel32.dll");
pCreateFileW myCreateFile = (pCreateFileW)GetProcAddress(
    kernel32, "CreateFileW");

// API hashing
DWORD hash_api(char *name) {
    DWORD hash = 0;
    while (*name) {
        hash = ((hash >> 13) | (hash << 19)) + *name++;
    }
    return hash;
}
// Resolve by hash comparison instead of string
```

**分析方法：** 识别哈希算法，构建已知 API 名称哈希数据库，使用 IDA 的 HashDB 插件，或在调试器下运行让二进制在运行时解析调用。

### 指令级混淆

```asm
; Dead code insertion — semantically inert but pollutes disassembly
push ebx / mov eax, 1 / pop ebx / xor ecx, ecx / add ecx, ecx

; Instruction substitution — same semantics, different encoding
xor eax, eax  →  sub eax, eax  |  mov eax, 0  |  and eax, 0
mov eax, 1    →  xor eax, eax; inc eax  |  push 1; pop eax
```

高级反汇编技巧（重叠指令、垃圾字节插入、自修改代码、ROP 作为混淆）参见 [references/advanced-techniques.md](references/advanced-techniques.md)。

---

## 绕过策略总结

### 通用原则

1. **理解保护**：识别使用了什么技术
2. **找到检查**：在二进制中定位保护代码
3. **修补或钩取**：修改检查使其始终通过
4. **使用适当工具**：ScyllaHide、x64dbg 插件
5. **记录发现**：保留绕过保护的笔记

### 工具推荐

```
Anti-debug bypass:    ScyllaHide, TitanHide
Unpacking:           x64dbg + Scylla, OllyDumpEx
Deobfuscation:       D-810, SATURN, miasm
VM analysis:         VMAttack, NoVmp, manual tracing
String decryption:   FLOSS, custom scripts
Symbolic execution:  angr, Triton
```

### 伦理考量

此知识应仅用于：

- 授权安全研究
- 恶意软件分析（防御性）
- CTF 竞赛
- 为合法目的理解保护
- 教育目的

切勿用于绕过保护以进行：软件盗版、未经授权访问或恶意目的。

---

## 故障排除

**检测技术在 x86 上有效但在 ARM 上无效**

RDTSC 和 CPUID 仅限 x86。在 ARM 上，使用 `MRS x0, PMCCNTR_EL0`（需要内核 PMU 访问）或 `clock_gettime(CLOCK_MONOTONIC)`。PEB/TEB 在 ARM 上不存在 — 替换为 `/proc/self/status`（Linux）或 `task_info`（macOS）。使用平台特定 API 重建检测逻辑。

**对合法调试器或分析工具的误报**

当 Process Monitor 或 AV 钩子增加系统调用延迟时，时序检查会触发。在启动时校准阈值：测量受保护路径 3 次并使用 `mean + 3*stddev`。对于 ptrace 检查，在退出前通过 `/proc/<pid>/comm` 验证 TracerPid comm 名称 — 它可能是不相关的监控工具，而非调试器。

**绕过补丁导致崩溃而非继续执行**

在 NOP 化条件跳转之前，完整跟踪"检测到"的分支。如果它初始化或释放了后续需要的堆状态，修补跳转会跳过该设置并损坏状态。改为将比较操作数修补为预期的"干净"值，或在断点上使用 x64dbg 的"将条件设为始终为假"而非修改字节。

---

## 相关技能

- `binary-analysis-patterns` — ELF/PE/Mach-O 的静态和动态分析工作流
- `memory-forensics` — 进程内存获取、产物提取和实时分析
- `protocol-reverse-engineering` — 解码自定义二进制协议和加密网络流量
