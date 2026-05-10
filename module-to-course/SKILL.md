---
name: module-to-course
description: |
  将代码目录树自动拆分为模块层级，为每个有代码的模块（包括非叶子节点）生成交互式教程，并在模块间建立导航链接。当用户提供代码路径并要求生成教程、把项目变成课程、模块化教程、递归生成教程时触发。也适用于用户说"把这个目录变成教程树"、"按模块生成课程"、"递归教程"、"module-to-course"等。提供路径即可启动，无需额外说明。
---

# Module-to-Course（模块化教程生成器）

将一个代码目录自动拆分为树状模块层级，为每个**有代码的模块**生成交互式教程，无代码的纯容器目录生成导航页，所有模块间建立导航链接。

## 调用参数（供其他技能使用）

其他技能（如 `aaos-reader`）可以调用本技能，并传入以下可选参数来定制行为：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `outputRoot` | 路径 | `中文教程/` | 教程输出根目录。默认输出到 `中文教程/{根模块名}/`，可改为 `D:\claude\aaos\` 等自定义路径 |
| `domainContext` | 字符串 | 无 | 领域知识上下文。在分析代码和生成教程时注入到 Agent 提示中，帮助理解特定领域的代码模式（如 AAOS 的 Binder IPC、HAL 层等） |
| `extraExcludeDirs` | 列表 | `[]` | 额外的目录排除规则，会与默认排除规则合并。如 `["fuzzer", "generated", "out", "obj"]` |
| `extraCodeExtensions` | 列表 | `[]` | 额外的代码文件扩展名。如 AAOS 场景需要 `.bp` 文件被视为代码 |
| `userLeafPaths` | 列表 | `[]` | 用户指定的叶子模块路径（相对于代码根目录）。遇到这些路径时停止递归，直接标记为 LEAF |
| `minCodeFiles` | 数字 | `3` | 叶子模块最少代码文件数。少于这个数的模块会被跳过 |

**调用示例：**

```
调用 module-to-course，参数：
  - 代码路径: D:\work\aaos\frameworks\native\services\surfaceflinger
  - outputRoot: D:\claude\aaos\
  - domainContext: "这是 AAOS (Android Automotive OS) 源码。重点关注 Binder IPC、HIDL/AIDL HAL、SurfaceFlinger 合成流程..."
  - extraExcludeDirs: ["fuzzer", "generated", "out", "obj"]
  - extraCodeExtensions: [".bp"]
```

## 核心概念：三种模块类型

遍历目录后，每个模块会被归类为以下三种类型之一：

| 类型 | 判定条件 | 生成内容 |
|------|---------|---------|
| **叶子模块** | 无子目录（或只有排除目录），有代码文件 | 完整教程 |
| **内容模块** | 有子目录，**且**自身有代码文件 | 教程 + 子模块摘要与链接 |
| **容器模块** | 有子目录，但自身无代码文件（纯转发/组织目录） | 仅导航页 |

**关键逻辑：** 每个目录都需要检查自身是否有代码文件。不能仅凭"有子目录"就跳过教程生成——如果该目录下有 `.py`、`.js`、`.ts`、`.java`、`.cpp` 等源码文件，它就是一个内容模块，需要生成教程。

## 工作流程

### 步骤 1：接收代码路径

用户提供代码路径（如 `D:\work\agents\claude\SmartPerfetto`），或由其他技能通过参数传入。提取路径最后一层目录名作为**根模块名**（如 `SmartPerfetto`）。

**输出根目录：** 默认使用 `中文教程/` 作为输出根目录。如果调用方传入了 `outputRoot` 参数（如 `D:\claude\aaos\`），则使用该路径替代。最终输出到 `{outputRoot}/{根模块名}/`。

**领域上下文：** 如果调用方传入了 `domainContext`，在后续所有分析代码和生成教程的 Agent 提示中注入该上下文，帮助理解领域特定的代码模式。

**额外排除规则：** 如果调用方传入了 `extraExcludeDirs` 或 `extraCodeExtensions`，将其合并到默认的排除规则和代码检测规则中。

在 `{outputRoot}/{根模块名}/` 目录下创建输出结构。

### 步骤 2：递归遍历目录，建立模块树

**恢复检查：** 在开始遍历之前，检查 `中文教程/{根模块名}/.module-tree.json` 是否存在。如果存在，说明之前已确认过模块树，直接跳到步骤 3 的"加载已有模块树"部分。

从代码路径的根目录开始，递归遍历：

1. 列出当前目录下的所有**直接子目录**（排除 `node_modules`、`.git` 等，见"目录排除规则"）
2. 检查当前目录自身是否有**代码文件**（源码文件：`.py`、`.js`、`.ts`、`.jsx`、`.tsx`、`.java`、`.kt`、`.cpp`、`.c`、`.h`、`.go`、`.rs`、`.rb`、`.swift`、`.scala`、`.sh`、`.m`、`.mm` 等；**不算**代码文件的：`.md`、`.txt`、`.json`、`.yaml`、`.yml`、`.toml`、`.cfg`、`.ini`、`.lock`、`.png`、`.jpg`、`.svg`、`.ico`、`.css`（纯样式）、`.html`（纯模板））
3. 根据子目录和代码文件情况，对当前目录自动分类：
   - **无子目录**（或只有排除目录）→ 叶子模块
   - **有子目录 + 有代码** → 内容模块
   - **有子目录 + 无代码** → 容器模块
4. **自动递归进入所有非排除的子目录**，重复步骤 2，无需用户确认。
5. **用户指定叶子模块：** 如果用户在请求中明确指定了某些目录为"叶子模块"（如"把 `XXX/` 当作叶子"），则在遍历时遇到该路径就停止递归，直接标记为 LEAF，不再深入其内部子目录。

**目录遍历伪代码：**

```
function traverse(dir, tree_path, user_leaf_paths, extra_exclude, extra_extensions):
    subdirs = list_subdirs(dir, default_excludes + extra_exclude)
    has_code = has_source_files(dir, default_extensions + extra_extensions)

    # 用户指定的叶子模块：停止递归
    if tree_path in user_leaf_paths:
        mark_as(LEAF)
        return

    # 当前目录类型自动判定
    if not subdirs:
        mark_as(LEAF)
    elif has_code:
        mark_as(CONTENT)
    else:
        mark_as(CONTAINER)

    # 自动递归所有子目录（不询问用户）
    for each subdir in subdirs:
        traverse(subdir, tree_path + [subdir_name], user_leaf_paths, extra_exclude, extra_extensions)
```

### 步骤 3：展示模块树并开始生成

遍历完成后，直接展示模块树作为信息输出，然后自动进入步骤 4 开始生成，**不需要用户确认**。

**加载已有模块树：** 如果步骤 2 中检测到 `中文教程/{根模块名}/.module-tree.json` 存在，直接加载该文件作为模块树，并向用户报告"检测到已保存的模块树，将沿用之前的确认结果"。如果用户要求重新确认，则删除该文件并重新执行步骤 2。

**展示内容：**

1. **模块树结构** — 以缩进树形格式展示所有模块，标注类型（叶子/内容/容器）
2. **每个模块的代码文件数** 
3. **生成计划** — 按自底向上顺序，哪些模块并行、哪些串行

展示格式示例：

```
SmartPerfetto/              ← 内容模块（5 个代码文件）
├── backend/                ← 内容模块（1 个代码文件）
│   ├── src/                ← 内容模块（1 个代码文件）
│   │   ├── agent/          ← 内容模块（6 个代码文件）
│   │   ├── controllers/    ← 叶子模块（7 个代码文件）
│   │   └── services/       ← 内容模块（50 个代码文件）
│   │       ├── adb/        ← 叶子模块
│   │       └── ...         ← ...
│   └── skills/             ← 容器模块（无代码）
├── frontend/               ← 叶子模块（4 个代码文件）
├── rust/                   ← 容器模块（无代码）
│   └── flamegraph-analyzer/ ← 叶子模块（1 个代码文件）
└── scripts/                ← 叶子模块（9 个代码文件）

生成顺序（自底向上）：
  第 1 批（并行）：agent/, controllers/, services/adb/ ... （所有叶子模块）
  第 2 批：services/, src/ ... （子模块已完成的中间内容模块）
  第 N 批：SmartPerfetto/ （根模块）

如需调整模块树，请中断并说明修改要求。
```

展示完毕后直接进入步骤 4 开始生成，无需等待用户确认。如需调整（合并/拆分模块、修改类型），用户可随时中断并要求修改。

**保存模块树：** 遍历完成后，将模块树保存到 `中文教程/{根模块名}/.module-tree.json`，格式如下：

```json
{
  "rootModule": "SmartPerfetto",
  "sourcePath": "D:\\work\\agents\\claude\\SmartPerfetto",
  "confirmedAt": "2026-05-08T10:30:00+08:00",
  "modules": {
    "": { "type": "CONTENT", "codeFiles": 5 },
    "backend": { "type": "CONTENT", "codeFiles": 1 },
    "backend/src": { "type": "CONTENT", "codeFiles": 1 },
    "backend/src/controllers": { "type": "LEAF", "codeFiles": 7 },
    "backend/src/services": { "type": "CONTENT", "codeFiles": 50 },
    "backend/src/services/adb": { "type": "LEAF", "codeFiles": 3 }
  }
}
```

其中 `modules` 的 key 是相对于代码根目录的路径（根模块自身为空字符串）。保存此文件后，下次对同一目录执行时将自动加载，无需重新确认。

### 步骤 4：为叶子模块生成教程

**跳过检查：** 在生成每个模块的教程之前，检查对应的输出目录（`中文教程/{根模块名}/{模块路径}/`）是否已存在且包含有效的 `index.html`。如果 `index.html` 存在且非空（文件大小 > 0），则该模块视为已完成，直接跳过，标记为 COMPLETED，并向用户报告"模块 {名称} 已有完成的教程，跳过生成"。

对每个叶子模块，调用 `codebase-to-course` 的流程生成教程：

1. **分析代码** — 只读取该叶子模块目录下的源码文件。如果存在 `domainContext`，在分析 Agent 的系统提示中注入领域知识，帮助理解领域特定的代码模式（如 AAOS 的 Binder IPC、HAL 层等）
2. **设计课程** — 4-6 个模块
3. **构建课程** — 按 codebase-to-course 的标准流程：
   - 复制 `styles.css`、`main.js`、`_footer.html`、`build.sh` 从 `codebase-to-course/references/`
   - 定制 `_base.html`（加入导航链接）
   - 编写 `modules/*.html`
   - 运行 `build.sh` 生成 `index.html`

### 步骤 5：为内容模块生成教程（含子模块摘要）

内容模块 = 有自身代码 + 有子模块。它的教程需要**同时涵盖**自身代码和子模块的内容。

**前置条件：** 该内容模块的所有子模块必须已完成教程/导航页生成，否则跳过此模块，等子模块完成后再处理。

**跳过检查：** 与步骤 4 相同——检查输出目录中是否已存在有效的 `index.html`，若存在则标记为 COMPLETED 并跳过。

**生成流程：**

1. **分析自身代码** — 读取该目录下的源码文件
2. **提取子模块摘要** — 对每个子模块，快速阅读其代码，提取：
   - 子模块名
   - 一句话核心职责
   - 关键类/函数名（2-3个最重要的）
   - 与当前模块的调用关系
3. **设计课程** — 按以下结构编排：
   - 模块 1：当前模块概述 — 这个模块做什么、为什么重要
   - 模块 2-3：自身代码详解 — 深入当前目录下的源码
   - 模块 4：子模块概览 — 每个子模块的核心逻辑摘要，配导航链接
   - 模块 5-6：自身代码深入 — 如果代码量大，继续深入
4. **子模块概览模块的特殊处理：**
   - 每个子模块一个小节，包含：
     - 子模块名称和一句话描述
     - 核心代码片段（从子模块中提取最关键的 10-20 行）
     - "深入了解 →" 链接到子模块的 `index.html`
   - 使用 `callout-box` 样式突出子模块链接
   - 使用 `flow-animation` 展示当前模块与子模块之间的调用关系
5. **构建课程** — 与叶子模块相同的 build 流程

**子模块摘要不是替代子模块教程**，而是让读者先从上层看到全局，再按需深入。摘要只提取"这个子模块大致做什么"，详细实现留给子模块自己的教程。

### 步骤 6：为容器模块生成导航页

容器模块 = 有子目录但无自身代码。不生成教程，只生成导航页。

**前置条件：** 该容器模块的所有子模块必须已完成教程/导航页生成，否则跳过此模块，等子模块完成后再处理。

**跳过检查：** 与步骤 4 相同——检查输出目录中是否已存在有效的 `index.html`，若存在则标记为 COMPLETED 并跳过。

导航页包含：
1. **模块标题** — 目录名
2. **子模块卡片** — 每个子模块一个卡片，链接到对应的 `index.html`
3. **父级导航** — 返回上级的链接
4. **同级导航** — 同一父级下其他模块的快速链接

导航页模板见 `references/module-nav-template.html`。

### 步骤 7：建立模块间链接

在所有教程和导航页中注入导航链接：

**叶子模块 / 内容模块的教程中：**
- 在 `_base.html` 的 `<nav>` 中添加：
  - **上一级** 链接 → 指向父模块的 `index.html`
  - **同级模块** 下拉菜单 → 指向同一父级下其他模块的 `index.html`
- 在教程末尾添加"相关模块"区域：
  - 链接到同级模块
  - 内容模块还需链接到自己的子模块

**内容模块的子模块概览模块中：**
- 每个子模块摘要后有"深入了解 →"链接到子模块 `index.html`
- 使用 `nav-snippet.html` 中的导航组件

**容器模块的导航页中：**
- 子模块卡片链接到各自的 `index.html`
- 面包屑导航指向祖先模块

**链接规则：**
- 所有链接使用**相对路径**（如 `../core/index.html`、`./parser/index.html`）
- 根模块路径：`中文教程/{根模块名}/index.html`
- 子模块路径：`中文教程/{根模块名}/{path...}/index.html`

### 步骤 8：更新索引

生成完成后，触发 `中文教程索引更新` skill 更新 `中文教程/index.html`，将新生成的教程加入索引。

## 代码文件检测规则

判断一个目录"是否有代码"时：

**算作代码文件（有代码 = 需要生成教程）：**
`.py`、`.js`、`.ts`、`.jsx`、`.tsx`、`.java`、`.kt`、`.cpp`、`.c`、`.h`、`.hpp`、`.go`、`.rs`、`.rb`、`.swift`、`.scala`、`.sh`、`.bash`、`.m`、`.mm`、`.cs`、`.vb`、`.dart`、`.lua`、`.r`、`.R`、`.jl`、`.ex`、`.exs`、`.erl`、`.hs`、`.ml`、`.fs`、`.clj`、`.zig`

**不算代码文件：**
`.md`、`.txt`、`.json`、`.yaml`、`.yml`、`.toml`、`.cfg`、`.ini`、`.env`、`.lock`、`.png`、`.jpg`、`.jpeg`、`.gif`、`.svg`、`.ico`、`.webp`、`.css`、`.html`、`.xml`、`.map`、`.log`、`.csv`、`.tsv`

**特殊情况：**
- 只有 `__init__.py` 或 `index.js` 等纯导出文件，内部无逻辑（只有 import/re-export）→ 视为无代码
- 有 `setup.py`/`pyproject.toml`/`package.json` 但无其他源码 → 视为无代码（这些是配置）
- 测试文件（`test_*.py`、`*_test.go`、`*.spec.ts`）→ 算代码文件

## 导航页设计规范

导航页风格与教程保持一致（暖色调、Bricolage Grotesque 字体、卡片式布局），但更轻量：

- 标题区域：模块名 + 简短描述
- 面包屑：显示从根模块到当前模块的路径
- 子模块网格：每个子模块一张卡片，卡片需标明类型（教程/导航），包含名称、描述、模块数、链接
- 父级返回按钮

卡片类型标记：
- 教程模块（叶子/内容）→ `class="card-type course"` + 绿色标签"教程"
- 导航模块（容器）→ `class="card-type navigation"` + 灰色标签"导航"

## 目录排除规则

遍历时自动跳过以下目录（不视为模块）：

**工具/IDE/构建相关：**
```
node_modules, .git, __pycache__, .venv, venv, dist, build, .next,
target, .idea, .vscode, .cache, .tox, .eggs, *.egg-info, .mypy_cache,
.pytest_cache, .sass-cache, coverage, .nyc_output, out, .output
```

**AI Agent 配置目录：**
```
.claude, .agent, .cursor, .copilot, .aider, .continue
```

**文档/测试/示例目录：**
```
docs, doc, examples, example, tests, test, __tests__, fixtures, mocks
```

**调用方额外排除：** 如果传入了 `extraExcludeDirs` 参数，将其合并到上述默认排除列表中。例如 AAOS 场景可能传入 `["fuzzer", "generated", "obj"]`。

**注意：** `tests`、`docs`、`examples` 等目录默认排除。如果用户明确要求包含这些目录，则尊重用户选择。

如果目录下只有上述排除目录而没有其他子目录，检查当前目录自身是否有代码文件来决定类型。

## 文件排除规则

遍历和代码检测时自动跳过以下文件（不计入代码文件判断）：

**AI Agent 配置文件：**
```
.claude/**, .agent/**, CLAUDE.md, AGENTS.md, .cursorrules, .copilotrc
```

**构建/锁文件：**
```
package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb
```

**Docker/CI 配置：**
```
Dockerfile, docker-compose*.yml, .dockerignore, .github/**, .gitlab-ci.yml
```

## 并行策略与生成顺序

**核心原则：严格遵守自底向上顺序。** 一个内容模块的所有子模块必须全部完成后，才能开始该内容模块的教程生成。容器模块同理——所有子模块完成后才能生成导航页。

**生成顺序规则：**

1. **第 1 层（叶子模块）**：所有叶子模块之间互相独立，可以并行生成（每批最多 3 个 Agent 子代理）
2. **第 2 层（直接父模块）**：当某个内容/容器模块的所有子模块都完成后，才能开始该模块
3. **第 N 层**：逐层向上，根模块最后生成
4. **索引更新**：在所有教程和导航页生成后执行

**依赖检查逻辑：**

```
function can_generate(module):
    if module.type == LEAF:
        return true  # 叶子模块随时可生成
    # 内容模块或容器模块：检查所有子模块是否已完成
    return all(child.status == COMPLETED for child in module.children)
```

**调度策略：**
- 维护一个"就绪队列"，初始包含所有叶子模块
- 每当一个模块完成，检查其父模块是否因此变为就绪（所有子模块完成）
- 就绪的非叶子模块加入队列，按层级顺序执行（同层可并行）
- 容器模块生成导航页时，从已完成的子模块教程中提取标题和描述

## 错误处理与恢复

- 如果某个叶子模块的代码太少（少于 3 个源码文件），跳过该模块并告知用户
- 如果内容模块自身代码量很少（如只有几行胶水代码），仍生成教程，但重点放在子模块概览上
- 如果 `build.sh` 执行失败，检查模块 HTML 是否有语法错误，修复后重试
- 如果用户中断生成流程，已完成的模块保留在输出目录中，下次从断点继续生成

**中断恢复机制：**

由于模块树保存在 `中文教程/{根模块名}/.module-tree.json`，且每个已完成的模块在输出目录中留有 `index.html`，当执行中断后重新运行时：

1. 自动加载已保存的模块树（无需重新确认）
2. 扫描所有模块的输出目录，将已有有效 `index.html` 的模块标记为 COMPLETED
3. 将未完成的模块加入就绪队列，按自底向上规则继续生成
4. 向用户报告恢复状态：哪些模块已完成（跳过），哪些需要继续生成

**完整性判定：** 输出目录存在且 `index.html` 文件大小 > 0 视为已完成。如果 `index.html` 存在但为空（0 字节），视为生成失败，需要重新生成。
