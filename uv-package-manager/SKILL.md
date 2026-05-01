---
name: uv-package-manager
description: 掌握 uv 包管理器，用于快速 Python 依赖管理、虚拟环境和现代 Python 项目工作流。适用于设置 Python 项目、管理依赖或使用 uv 优化 Python 开发工作流。
---

# UV 包管理器

使用 uv（用 Rust 编写的极速 Python 包安装器和解析器）进行现代 Python 项目管理和依赖工作流的综合指南。

## 何时使用此技能

- 快速设置新 Python 项目
- 比 pip 更快地管理 Python 依赖
- 创建和管理虚拟环境
- 安装 Python 解释器
- 高效解决依赖冲突
- 从 pip/pip-tools/poetry 迁移
- 加速 CI/CD 管道
- 管理 monorepo Python 项目
- 使用锁文件实现可复现构建
- 优化 Docker 构建中的 Python 依赖

## 核心概念

### 1. 什么是 uv？

- **超快的包安装器**：比 pip 快 10-100 倍
- **用 Rust 编写**：利用 Rust 的性能
- **pip 的直接替代品**：兼容 pip 工作流
- **虚拟环境管理器**：创建和管理 venvs
- **Python 安装器**：下载和管理 Python 版本
- **解析器**：高级依赖解析
- **锁文件支持**：可复现的安装

### 2. 关键特性

- 极快的安装速度
- 全局缓存节省磁盘空间
- 兼容 pip、pip-tools、poetry
- 全面的依赖解析
- 跨平台支持（Linux、macOS、Windows）
- 安装不需要 Python
- 内置虚拟环境支持

### 3. UV vs 传统工具

- **vs pip**：快 10-100 倍，更好的解析器
- **vs pip-tools**：更快、更简单、更好的用户体验
- **vs poetry**：更快、更轻量、更灵活
- **vs conda**：更快、专注于 Python

## 安装

### 快速安装

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 使用 pip（如果已有 Python）
pip install uv

# 使用 Homebrew (macOS)
brew install uv

# 使用 cargo（如果有 Rust）
cargo install --git https://github.com/astral-sh/uv uv
```

### 验证安装

```bash
uv --version
# uv 0.x.x
```

## 快速开始

### 创建新项目

```bash
# 创建带虚拟环境的新项目
uv init my-project
cd my-project

# 或在当前目录创建
uv init .

# 初始化会创建：
# - .python-version（Python 版本）
# - pyproject.toml（项目配置）
# - README.md
# - .gitignore
```

### 安装依赖

```bash
# 安装包（如需要会创建 venv）
uv add requests pandas

# 安装开发依赖
uv add --dev pytest black ruff

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 从 pyproject.toml 安装
uv sync
```

## 虚拟环境管理

### 模式 1：创建虚拟环境

```bash
# 使用 uv 创建虚拟环境
uv venv

# 使用特定 Python 版本创建
uv venv --python 3.12

# 使用自定义名称创建
uv venv my-env

# 使用系统站点包创建
uv venv --system-site-packages

# 指定位置
uv venv /path/to/venv
```

### 模式 2：激活虚拟环境

```bash
# Linux/macOS
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# 或使用 uv run（无需激活）
uv run python script.py
uv run pytest
```

### 模式 3：使用 uv run

```bash
# 运行 Python 脚本（自动激活 venv）
uv run python app.py

# 运行已安装的 CLI 工具
uv run black .
uv run pytest

# 使用特定 Python 版本运行
uv run --python 3.11 python script.py

# 传递参数
uv run python script.py --arg value
```

## 包管理

### 模式 4：添加依赖

```bash
# 添加包（添加到 pyproject.toml）
uv add requests

# 添加带版本约束的包
uv add "django>=4.0,<5.0"

# 添加多个包
uv add numpy pandas matplotlib

# 添加开发依赖
uv add --dev pytest pytest-cov

# 添加可选依赖组
uv add --optional docs sphinx

# 从 git 添加
uv add git+https://github.com/user/repo.git

# 从 git 添加特定引用
uv add git+https://github.com/user/repo.git@v1.0.0

# 从本地路径添加
uv add ./local-package

# 添加可编辑的本地包
uv add -e ./local-package
```

### 模式 5：移除依赖

```bash
# 移除包
uv remove requests

# 移除开发依赖
uv remove --dev pytest

# 移除多个包
uv remove numpy pandas matplotlib
```

### 模式 6：升级依赖

```bash
# 升级特定包
uv add --upgrade requests

# 升级所有包
uv sync --upgrade

# 升级包到最新版本
uv add --upgrade requests

# 显示可升级的内容
uv tree --outdated
```

### 模式 7：锁定依赖

```bash
# 生成 uv.lock 文件
uv lock

# 更新锁文件
uv lock --upgrade

# 仅锁定不安装
uv lock --no-install

# 锁定特定包
uv lock --upgrade-package requests
```

## Python 版本管理

### 模式 8：安装 Python 版本

```bash
# 安装 Python 版本
uv python install 3.12

# 安装多个版本
uv python install 3.11 3.12 3.13

# 安装最新版本
uv python install

# 列出已安装版本
uv python list

# 查找可用版本
uv python list --all-versions
```

### 模式 9：设置 Python 版本

```bash
# 为项目设置 Python 版本
uv python pin 3.12

# 这会创建/更新 .python-version 文件

# 为命令使用特定 Python 版本
uv --python 3.11 run python script.py

# 使用特定版本创建 venv
uv venv --python 3.12
```

## 项目配置

### 模式 10：使用 uv 的 pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
docs = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    # uv 管理的额外开发依赖
]

[tool.uv.sources]
# 自定义包源
my-package = { git = "https://github.com/user/repo.git" }
```

### 模式 11：在现有项目中使用 uv

```bash
# 从 requirements.txt 迁移
uv add -r requirements.txt

# 从 poetry 迁移
# 已有 pyproject.toml，直接使用：
uv sync

# 导出到 requirements.txt
uv pip freeze > requirements.txt

# 带哈希值导出
uv pip freeze --require-hashes > requirements.txt
```

有关高级工作流（包括 Docker 集成、锁文件管理、性能优化、工具比较、常见工作流、工具集成、故障排除、最佳实践、迁移指南和命令参考），请参阅 [references/advanced-patterns.md](references/advanced-patterns.md)
