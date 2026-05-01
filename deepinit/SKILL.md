---
name: deepinit
description: 使用分层 AGENTS.md 文档进行深度代码库初始化
level: 4
---

# 深度初始化技能

在整个代码库中创建全面的分层 AGENTS.md 文档。

## 核心概念

AGENTS.md 文件作为**AI 可读文档**，帮助代理理解：
- 每个目录包含什么
- 组件如何相互关联
- 在该区域工作的特殊说明
- 依赖和关系

## 分层标记系统

每个 AGENTS.md（根目录除外）都包含父引用标签：

```markdown
<!-- Parent: ../AGENTS.md -->
```

这创建了一个可导航的层次结构：
```
/AGENTS.md                          ← 根（无父标签）
├── src/AGENTS.md                   ← <!-- Parent: ../AGENTS.md -->
│   ├── src/components/AGENTS.md    ← <!-- Parent: ../AGENTS.md -->
│   └── src/utils/AGENTS.md         ← <!-- Parent: ../AGENTS.md -->
└── docs/AGENTS.md                  ← <!-- Parent: ../AGENTS.md -->
```

## AGENTS.md 模板

```markdown
<!-- Parent: {relative_path_to_parent}/AGENTS.md -->
<!-- Generated: {timestamp} | Updated: {timestamp} -->

# {Directory Name}

## Purpose
{此目录包含内容及其角色的段落描述}

## Key Files
{列出每个重要文件及其一行描述}

| File | Description |
|------|-------------|
| `file.ts` | 用途简述 |

## Subdirectories
{列出每个子目录及其简要用途}

| Directory | Purpose |
|-----------|---------|
| `subdir/` | 包含内容（参见 `subdir/AGENTS.md`） |

## For AI Agents

### Working In This Directory
{AI 代理在此目录修改文件的特殊说明}

### Testing Requirements
{如何测试此目录中的更改}

### Common Patterns
{此处使用的代码模式或约定}

## Dependencies

### Internal
{此依赖的代码库其他部分引用}

### External
{使用的关键外部包/库}

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
```

## 执行工作流程

### 步骤 1：映射目录结构

```
Task(subagent_type="explore", model="haiku",
  prompt="List all directories recursively. Exclude: node_modules, .git, dist, build, __pycache__, .venv, coverage, .next, .nuxt")
```

### 步骤 2：创建工作计划

为每个目录生成待办事项，按深度级别组织：

```
Level 0: / (root)
Level 1: /src, /docs, /tests
Level 2: /src/components, /src/utils, /docs/api
...
```

### 步骤 3：逐级生成

**重要**：在子级之前生成父级，以确保父引用有效。

对于每个目录：
1. 读取目录中的所有文件
2. 分析用途和关系
3. 生成 AGENTS.md 内容
4. 写入带有正确父引用的文件

### 步骤 4：比较和更新（如果已存在）

当 AGENTS.md 已存在时：

1. **读取现有内容**
2. **识别部分**：
   - 自动生成的部分（可更新）
   - 手动部分（`<!-- MANUAL -->` 保留）
3. **比较**：
   - 添加了新文件？
   - 移除了文件？
   - 结构改变了？
4. **合并**：
   - 更新自动生成的内容
   - 保留手动注释
   - 更新时间戳

### 步骤 5：验证层次结构

生成后，运行验证检查：

| 检查项 | 验证方法 | 纠正措施 |
|--------|----------|----------|
| 父引用可解析 | 读取每个 AGENTS.md，检查 `<!-- Parent: -->` 路径存在 | 修复路径或移除孤立项 |
| 无孤立 AGENTS.md | 比较 AGENTS.md 位置与目录结构 | 删除孤立文件 |
| 完整性 | 列出所有目录，检查是否有 AGENTS.md | 生成缺失文件 |
| 时间戳最新 | 检查 `<!-- Generated: -->` 日期 | 重新生成过时文件 |

验证脚本模式：
```bash
# 查找所有 AGENTS.md 文件
find . -name "AGENTS.md" -type f

# 检查父引用
grep -r "<!-- Parent:" --include="AGENTS.md" .
```

## 智能委派

| 任务 | 代理 |
|------|------|
| 目录映射 | `explore` |
| 文件分析 | `architect` |
| 内容生成 | `writer` |
| AGENTS.md 写入 | `writer` |

## 空目录处理

遇到空目录或近乎空的目录时：

| 条件 | 操作 |
|------|------|
| 无文件，无子目录 | **跳过** — 不创建 AGENTS.md |
| 无文件，有子目录 | 创建仅包含子目录列表的最小 AGENTS.md |
| 仅有生成文件（*.min.js、*.map） | 跳过或最小 AGENTS.md |
| 仅有配置文件 | 创建描述配置用途的 AGENTS.md |

目录容器的最小 AGENTS.md 示例：
```markdown
<!-- Parent: ../AGENTS.md -->
# {Directory Name}

## Purpose
用于组织相关模块的容器目录。

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `subdir/` | 描述（参见 `subdir/AGENTS.md`） |
```

## 并行化规则

1. **同级目录**：并行处理
2. **不同级别**：顺序处理（父级优先）
3. **大型目录**：为每个目录生成专用代理
4. **小型目录**：将多个批处理到一个代理中

## 质量标准

### 必须包含
- [ ] 准确的文件描述
- [ ] 正确的父引用
- [ ] 子目录链接
- [ ] AI 代理指令

### 必须避免
- [ ] 通用模板
- [ ] 不正确的文件名
- [ ] 损坏的父引用
- [ ] 遗漏重要文件

## 示例输出

### 根 AGENTS.md
```markdown
<!-- Generated: 2024-01-15 | Updated: 2024-01-15 -->

# my-project

## Purpose
用于管理用户任务的 Web 应用，具有实时协作功能。

## Key Files
| File | Description |
|------|-------------|
| `package.json` | 项目依赖和脚本 |
| `tsconfig.json` | TypeScript 配置 |
| `.env.example` | 环境变量模板 |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `src/` | 应用源代码（参见 `src/AGENTS.md`） |
| `docs/` | 文档（参见 `docs/AGENTS.md`） |
| `tests/` | 测试套件（参见 `tests/AGENTS.md`） |

## For AI Agents

### Working In This Directory
- 修改项目清单后始终安装依赖
- 使用 TypeScript 严格模式
- 遵循 ESLint 规则

### Testing Requirements
- 提交前运行测试
- 确保 >80% 覆盖率

### Common Patterns
- 使用桶导出 (index.ts)
- 优先使用函数组件

## Dependencies

### External
- React 18.x - UI 框架
- TypeScript 5.x - 类型安全
- Vite - 构建工具

<!-- MANUAL: Custom project notes can be added below -->
```

### 嵌套 AGENTS.md
```markdown
<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2024-01-15 | Updated: 2024-01-15 -->

# components

## Purpose
按功能和复杂度组织的可复用 React 组件。

## Key Files
| File | Description |
|------|-------------|
| `index.ts` | 所有组件的桶导出 |
| `Button.tsx` | 主按钮组件 |
| `Modal.tsx` | 模态对话框组件 |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `forms/` | 表单相关组件（参见 `forms/AGENTS.md`） |
| `layout/` | 布局组件（参见 `layout/AGENTS.md`） |

## For AI Agents

### Working In This Directory
- 每个组件有自己的文件
- 使用 CSS 模块进行样式设置
- 通过 index.ts 导出

### Testing Requirements
- `__tests__/` 子目录中的单元测试
- 使用 React Testing Library

### Common Patterns
- Props 接口定义在组件上方
- 对暴露 DOM 的组件使用 forwardRef

## Dependencies

### Internal
- `src/hooks/` - 组件使用的自定义钩子
- `src/utils/` - 工具函数

### External
- `clsx` - 条件类名
- `lucide-react` - 图标

<!-- MANUAL: -->
```

## 触发更新模式

在已有 AGENTS.md 文件的现有代码库上运行时：

1. 首先检测现有文件
2. 读取并解析现有内容
3. 分析当前目录状态
4. 生成现有与当前之间的差异
5. 应用更新同时保留手动部分

## 性能考虑

- **缓存目录列表** — 不要重新扫描相同目录
- **批处理小型目录** — 一次处理多个
- **跳过未更改的** — 如果目录未更改，跳过重新生成
- **并行写入** — 多个代理同时写入不同文件
