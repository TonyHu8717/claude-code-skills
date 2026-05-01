---
name: binary-analysis-patterns
description: 掌握二进制分析模式，包括反汇编、反编译、控制流分析和代码模式识别。适用于分析可执行文件、理解编译后的代码或对二进制文件进行静态分析。
---

# 二进制分析模式

用于分析编译后的二进制文件、理解汇编代码和重建程序逻辑的综合模式与技术。

## 反汇编基础

### x86-64 指令模式

#### 函数序言/尾声

```asm
; 标准序言
push rbp           ; 保存基址指针
mov rbp, rsp       ; 设置栈帧
sub rsp, 0x20      ; 分配局部变量

; 叶函数（无调用）
; 可能跳过帧指针设置
sub rsp, 0x18      ; 仅分配局部变量

; 标准尾声
mov rsp, rbp       ; 恢复栈指针
pop rbp            ; 恢复基址指针
ret

; leave 指令（等效）
leave              ; mov rsp, rbp; pop rbp
ret
```

#### 调用约定

**System V AMD64（Linux、macOS）**

```asm
; 参数：RDI、RSI、RDX、RCX、R8、R9，然后是栈
; 返回：RAX（128位时还有 RDX）
; 调用者保存：RAX、RCX、RDX、RSI、RDI、R8-R11
; 被调用者保存：RBX、RBP、R12-R15

; 示例：func(a, b, c, d, e, f, g)
mov rdi, [a]       ; 第1个参数
mov rsi, [b]       ; 第2个参数
mov rdx, [c]       ; 第3个参数
mov rcx, [d]       ; 第4个参数
mov r8, [e]        ; 第5个参数
mov r9, [f]        ; 第6个参数
push [g]           ; 第7个参数在栈上
call func
```

**Microsoft x64（Windows）**

```asm
; 参数：RCX、RDX、R8、R9，然后是栈
; 影子空间：栈上保留32字节
; 返回：RAX

; 示例：func(a, b, c, d, e)
sub rsp, 0x28      ; 影子空间 + 对齐
mov rcx, [a]       ; 第1个参数
mov rdx, [b]       ; 第2个参数
mov r8, [c]        ; 第3个参数
mov r9, [d]        ; 第4个参数
mov [rsp+0x20], [e] ; 第5个参数在栈上
call func
add rsp, 0x28
```

### ARM 汇编模式

#### ARM64（AArch64）调用约定

```asm
; 参数：X0-X7
; 返回：X0（128位时还有 X1）
; 帧指针：X29
; 链接寄存器：X30

; 函数序言
stp x29, x30, [sp, #-16]!  ; 保存 FP 和 LR
mov x29, sp                 ; 设置帧指针

; 函数尾声
ldp x29, x30, [sp], #16    ; 恢复 FP 和 LR
ret
```

#### ARM32 调用约定

```asm
; 参数：R0-R3，然后是栈
; 返回：R0（64位时还有 R1）
; 链接寄存器：LR（R14）

; 函数序言
push {fp, lr}
add fp, sp, #4

; 函数尾声
pop {fp, pc}    ; 通过弹出 PC 返回
```

## 控制流模式

### 条件分支

```asm
; if (a == b)
cmp eax, ebx
jne skip_block
; ... if 主体 ...
skip_block:

; if (a < b) - 有符号
cmp eax, ebx
jge skip_block    ; 大于或等于时跳转
; ... if 主体 ...
skip_block:

; if (a < b) - 无符号
cmp eax, ebx
jae skip_block    ; 高于或等于时跳转
; ... if 主体 ...
skip_block:
```

### 循环模式

```asm
; for (int i = 0; i < n; i++)
xor ecx, ecx           ; i = 0
loop_start:
cmp ecx, [n]           ; i < n
jge loop_end
; ... 循环主体 ...
inc ecx                ; i++
jmp loop_start
loop_end:

; while (condition)
jmp loop_check
loop_body:
; ... 主体 ...
loop_check:
cmp eax, ebx
jl loop_body

; do-while
loop_body:
; ... 主体 ...
cmp eax, ebx
jl loop_body
```

### switch 语句模式

```asm
; 跳转表模式
mov eax, [switch_var]
cmp eax, max_case
ja default_case
jmp [jump_table + eax*8]

; 顺序比较（小型 switch）
cmp eax, 1
je case_1
cmp eax, 2
je case_2
cmp eax, 3
je case_3
jmp default_case
```

## 数据结构模式

### 数组访问

```asm
; array[i] - 4字节元素
mov eax, [rbx + rcx*4]        ; rbx=基址, rcx=索引

; array[i] - 8字节元素
mov rax, [rbx + rcx*8]

; 多维数组 array[i][j]
; arr[i][j] = base + (i * cols + j) * element_size
imul eax, [cols]
add eax, [j]
mov edx, [rbx + rax*4]
```

### 结构体访问

```c
struct Example {
    int a;      // 偏移 0
    char b;     // 偏移 4
    // 填充     // 偏移 5-7
    long c;     // 偏移 8
    short d;    // 偏移 16
};
```

```asm
; 访问结构体字段
mov rdi, [struct_ptr]
mov eax, [rdi]         ; s->a（偏移 0）
movzx eax, byte [rdi+4] ; s->b（偏移 4）
mov rax, [rdi+8]       ; s->c（偏移 8）
movzx eax, word [rdi+16] ; s->d（偏移 16）
```

### 链表遍历

```asm
; while (node != NULL)
list_loop:
test rdi, rdi          ; node == NULL?
jz list_done
; ... 处理节点 ...
mov rdi, [rdi+8]       ; node = node->next（假设 next 在偏移 8 处）
jmp list_loop
list_done:
```

## 常见代码模式

### 字符串操作

```asm
; strlen 模式
xor ecx, ecx
strlen_loop:
cmp byte [rdi + rcx], 0
je strlen_done
inc ecx
jmp strlen_loop
strlen_done:
; ecx 包含长度

; strcpy 模式
strcpy_loop:
mov al, [rsi]
mov [rdi], al
test al, al
jz strcpy_done
inc rsi
inc rdi
jmp strcpy_loop
strcpy_done:

; 使用 rep movsb 的 memcpy
mov rdi, dest
mov rsi, src
mov rcx, count
rep movsb
```

### 算术模式

```asm
; 常量乘法
; x * 3
lea eax, [rax + rax*2]

; x * 5
lea eax, [rax + rax*4]

; x * 10
lea eax, [rax + rax*4]  ; x * 5
add eax, eax            ; * 2

; 2的幂次除法（有符号）
mov eax, [x]
cdq                     ; 符号扩展到 EDX:EAX
and edx, 7              ; 用于除以 8
add eax, edx            ; 负数调整
sar eax, 3              ; 算术右移

; 2的幂次取模
and eax, 7              ; x % 8
```

### 位操作

```asm
; 测试特定位
test eax, 0x80          ; 测试第7位
jnz bit_set

; 设置位
or eax, 0x10            ; 设置第4位

; 清除位
and eax, ~0x10          ; 清除第4位

; 翻转位
xor eax, 0x10           ; 翻转第4位

; 计算前导零
bsr eax, ecx            ; 反向位扫描
xor eax, 31             ; 转换为前导零数

; 人口计数（popcnt）
popcnt eax, ecx         ; 计算已设置的位数
```

## 反编译模式

### 变量恢复

```asm
; rbp-8 处的局部变量
mov qword [rbp-8], rax  ; 存储到局部变量
mov rax, [rbp-8]        ; 从局部变量加载

; 栈分配的数组
lea rax, [rbp-0x40]     ; 数组从 rbp-0x40 开始
mov [rax], edx          ; array[0] = value
mov [rax+4], ecx        ; array[1] = value
```

### 函数签名恢复

```asm
; 通过寄存器使用识别参数
func:
    ; rdi 用作第一个参数（System V）
    mov [rbp-8], rdi    ; 保存参数到局部变量
    ; rsi 用作第二个参数
    mov [rbp-16], rsi
    ; 通过末尾的 RAX 识别返回值
    mov rax, [result]
    ret
```

### 类型恢复

```asm
; 1字节操作暗示 char/bool
movzx eax, byte [rdi]   ; 零扩展字节
movsx eax, byte [rdi]   ; 符号扩展字节

; 2字节操作暗示 short
movzx eax, word [rdi]
movsx eax, word [rdi]

; 4字节操作暗示 int/float
mov eax, [rdi]
movss xmm0, [rdi]       ; 浮点数

; 8字节操作暗示 long/double/指针
mov rax, [rdi]
movsd xmm0, [rdi]       ; 双精度浮点数
```

## Ghidra 分析技巧

### 改进反编译

```java
// 在 Ghidra 脚本中
// 修复函数签名
Function func = getFunctionAt(toAddr(0x401000));
func.setReturnType(IntegerDataType.dataType, SourceType.USER_DEFINED);

// 创建结构体类型
StructureDataType struct = new StructureDataType("MyStruct", 0);
struct.add(IntegerDataType.dataType, "field_a", null);
struct.add(PointerDataType.dataType, "next", null);

// 应用到内存
createData(toAddr(0x601000), struct);
```

### 模式匹配脚本

```python
# 查找所有对危险函数的调用
for func in currentProgram.getFunctionManager().getFunctions(True):
    for ref in getReferencesTo(func.getEntryPoint()):
        if func.getName() in ["strcpy", "sprintf", "gets"]:
            print(f"Dangerous call at {ref.getFromAddress()}")
```

## IDA Pro 模式

### IDAPython 分析

```python
import idaapi
import idautils
import idc

# 查找所有函数调用
def find_calls(func_name):
    for func_ea in idautils.Functions():
        for head in idautils.Heads(func_ea, idc.find_func_end(func_ea)):
            if idc.print_insn_mnem(head) == "call":
                target = idc.get_operand_value(head, 0)
                if idc.get_func_name(target) == func_name:
                    print(f"Call to {func_name} at {hex(head)}")

# 基于字符串自动重命名函数
def auto_rename():
    for s in idautils.Strings():
        for xref in idautils.XrefsTo(s.ea):
            func = idaapi.get_func(xref.frm)
            if func and "sub_" in idc.get_func_name(func.start_ea):
                # 使用字符串作为命名提示
                pass
```

## 最佳实践

### 分析工作流程

1. **初步分类**：文件类型、架构、导入/导出
2. **字符串分析**：识别有趣的字符串、错误消息
3. **函数识别**：入口点、导出、交叉引用
4. **控制流映射**：理解程序结构
5. **数据结构恢复**：识别结构体、数组、全局变量
6. **算法识别**：加密、哈希、压缩
7. **文档化**：注释、重命名的符号、类型定义

### 常见陷阱

- **优化器产物**：代码可能与源代码结构不匹配
- **内联函数**：函数可能被内联展开
- **尾调用优化**：使用 `jmp` 代替 `call` + `ret`
- **死代码**：优化产生的不可达代码
- **位置无关代码**：RIP 相对寻址
