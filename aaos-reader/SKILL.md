---
name: aaos-reader
description: |
  阅读 AAOS (Android Automotive OS) 本地代码目录，生成交互式 HTML 教程并保存到 aaos 目录下。适用于用户给出一个本地绝对路径（如 Y:\GuaMaster\aaos\frameworks\native\services\surfaceflinger），要求阅读代码、生成教程/课程/学习资料的场景。触发词：aaos reader, aaos 教程, aaos 代码阅读, 阅读这个模块, 分析这个代码, 生成教程, 代码教程。当用户提供一个包含 aaos 的绝对路径并要求生成教程时自动触发。支持多级子模块、Java 包识别、Android.bp 依赖分析。
---

# AAOS Code Reader

将 AAOS 代码目录转化为精美的交互式 HTML 教程。本技能是 `module-to-course` 的 AAOS 领域适配层——负责路径映射、领域知识注入、Android.bp 依赖分析和 Java 包识别，实际的模块树划分、教程生成、导航链接由 `module-to-course` 完成。

## 工作流程

### 步骤 1：解析输入路径

从用户输入中提取：
- 源码绝对路径（`src_path`），如 `Y:\GuaMaster\aaos\frameworks\native\services\surfaceflinger`
- AAOS 根目录前缀（通常是 `Y:\GuaMaster\aaos\`）
- 模块相对路径（去掉根目录前缀后的部分）
- 模块名（路径最后一级，如 `surfaceflinger`）

### 步骤 2：映射输出路径

将源路径中的 AAOS 根目录前缀替换为 `D:\claude\aaos\`：

| 源路径 | 输出路径 |
|--------|----------|
| `Y:\GuaMaster\aaos\frameworks\native\services\surfaceflinger` | `D:\claude\aaos\frameworks\native\services\surfaceflinger` |
| `Y:\GuaMaster\aaos\frameworks\base\services\core\...` | `D:\claude\aaos\frameworks\base\services\core\...` |

### 步骤 3：扫描 Android.bp 与 Java 包（AAOS 特有）

这是 AAOS 独有的分析步骤，在委托给 module-to-course 之前完成。

**Android.bp 依赖分析：**
- 扫描源目录及其子目录下的所有 `Android.bp` 文件
- 提取 `shared_libs`、`static_libs`、`header_libs`、`exports` 字段
- 提取 `srcs` 中引用的本地库（如 `libsurfaceflinger`、`libbinder` 等）
- 生成依赖图，将结果保存到 `{output_path}/dependencies.md`

**Java 包识别：**
- 如果目录下有 `Android.bp` 或 `AndroidManifest.xml`，扫描所有 `.java` 文件
- 按 Java 包名（`package com.android.server.wm`）分组
- 每个唯一包名识别为一个逻辑子模块
- 如果 Java 包有对应的 JNI 实现（`com_android_server_wm.cpp/h`），标注关联关系
- 将 Java 包分析结果保存到 `{output_path}/java-packages.md`

这些分析结果会作为 `domainContext` 的一部分传递给 module-to-course，帮助在生成教程时准确描述模块间的依赖关系和 JNI 绑定。

### 步骤 4：构造 AAOS 领域上下文

根据代码所在层级，构造对应的领域知识上下文：

**Native 层（frameworks/native/）：**
```
这是 AAOS (Android Automotive OS) Native 层源码。重点关注：
- Binder IPC 通信机制（libbinder、IServiceManager）
- SurfaceFlinger 合成流程（BufferQueue、Layer、HWComposer）
- HWC HAL 硬件合成（HIDL/AIDL HAL 接口）
- 共享内存机制（ashmem、ion、dmabuf）
- Android.bp 构建系统中的 shared_libs、static_libs、header_libs 依赖关系
```

**Framework 层（frameworks/base/）：**
```
这是 AAOS (Android Automotive OS) Framework 层源码。重点关注：
- SystemServer 启动流程和系统服务注册
- WMS（WindowManagerService）、AMS（ActivityManagerService）核心实现
- AIDL 接口定义和 Binder 事务
- Handler/Looper 消息机制
- 进程间通信和权限管理
```

**HAL 层（hardware/）：**
```
这是 AAOS (Android Automotive OS) HAL 层源码。重点关注：
- HIDL/AIDL HAL 接口定义
- HwBinder 通信机制
- passthrough 和 binderized 模式
- HAL 服务注册和发现
```

如果代码跨多个层级，合并相关上下文。

### 步骤 5：委托给 module-to-course

调用 `module-to-course` 技能，传入以下参数：

```
调用 module-to-course，参数：
  - 代码路径: {src_path}
  - outputRoot: D:\claude\aaos\
  - domainContext: "{步骤4构造的领域上下文}\n\n额外上下文：\n- Android.bp 依赖见 {output_path}/dependencies.md\n- Java 包分析见 {output_path}/java-packages.md\n- 教程生成时请重点分析代码中的 Binder 接口、HAL 调用、Android 系统服务注册等 AAOS 特有模式"
  - extraExcludeDirs: ["fuzzer", "generated", "out", "obj", "include"]
  - userLeafPaths: {用户指定的叶子模块路径（如有）}
```

之后的所有工作（模块树划分、教程生成、导航链接、索引更新）由 `module-to-course` 自动完成，无需 aaos-reader 再介入。

### 步骤 6：检查与报告

`module-to-course` 完成后：
1. 读取 `{output_path}/dependencies.md`，将依赖图内容补充到根模块教程的相关部分（如果 module-to-course 未覆盖）
2. 向用户报告：
   - 生成的模块树结构
   - 教程入口：`{output_path}/index.html`
   - 依赖分析摘要

## AAOS 特有的目录排除规则

除 module-to-course 的默认排除目录外，AAOS 场景额外排除：

```
fuzzer, generated, out, obj, include (仅当其不包含 .java/.cpp 等源码时)
```

`include/` 目录特殊处理：如果只包含 `.h` 头文件而无实现文件，视为排除；如果有 `.cpp` 实现，保留。

## 设计风格

教程使用暖色调，teal（`#2A7B9B`）作为 AAOS 系统级模块的默认强调色。所有界面文字为中文，代码保留英文原文。

## 增量更新

当 `module-to-course` 检测到输出目录已存在时，其内置的中断恢复机制会自动加载已保存的模块树（`.module-tree.json`），跳过已完成的模块，仅生成未完成的部分。aaos-reader 无需额外处理增量逻辑。
