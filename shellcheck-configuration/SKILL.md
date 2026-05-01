---
name: shellcheck-configuration
description: 掌握 ShellCheck 静态分析配置和使用，提升 Shell 脚本质量。在设置代码检查基础设施、修复代码问题或确保脚本可移植性时使用。
---

# ShellCheck 配置和静态分析

配置和使用 ShellCheck 的全面指南，用于提升 Shell 脚本质量、捕获常见陷阱，并通过静态代码分析强制执行最佳实践。

## 何时使用此技能

- 在 CI/CD 管道中为 Shell 脚本设置代码检查
- 分析现有 Shell 脚本的问题
- 理解 ShellCheck 错误代码和警告
- 为特定项目需求配置 ShellCheck
- 将 ShellCheck 集成到开发工作流中
- 抑制误报和配置规则集
- 强制执行一致的代码质量标准
- 迁移脚本以满足质量门控

## ShellCheck 基础

### 什么是 ShellCheck？

ShellCheck 是一个静态分析工具，用于分析 Shell 脚本并检测有问题的模式。它支持：

- Bash、sh、dash、ksh 和其他 POSIX Shell
- 超过 100 种不同的警告和错误
- 针对目标 Shell 和标志的配置
- 与编辑器和 CI/CD 系统集成

### 安装

```bash
# macOS 使用 Homebrew
brew install shellcheck

# Ubuntu/Debian
apt-get install shellcheck

# 从源码安装
git clone https://github.com/koalaman/shellcheck.git
cd shellcheck
make build
make install

# 验证安装
shellcheck --version
```

## 配置文件

### .shellcheckrc（项目级）

在项目根目录创建 `.shellcheckrc`：

```
# 指定目标 Shell
shell=bash

# 启用可选检查
enable=avoid-nullary-conditions
enable=require-variable-braces

# 禁用特定警告
disable=SC1091
disable=SC2086
```

### 环境变量

```bash
# 设置默认 Shell 目标
export SHELLCHECK_SHELL=bash

# 启用严格模式
export SHELLCHECK_STRICT=true

# 指定配置文件位置
export SHELLCHECK_CONFIG=~/.shellcheckrc
```

## 常见 ShellCheck 错误代码

### SC1000-1099：解析器错误

```bash
# SC1004: 反斜杠续行后未跟换行符
echo hello\
world  # 错误 - 需要行续接

# SC1008: 运算符 `==' 的数据无效
if [[ $var =  "value" ]]; then  # == 前有多余空格
    true
fi
```

### SC2000-2099：Shell 问题

```bash
# SC2009: 考虑使用 pgrep 或 pidof 代替 grep|grep
ps aux | grep -v grep | grep myprocess  # 应使用 pgrep

# SC2012: `ls` 仅用于查看。使用 `find` 获取可靠输出
for file in $(ls -la)  # 更好：使用 find 或 globbing

# SC2015: 避免使用 && 和 || 代替 if-then-else
[[ -f "$file" ]] && echo "found" || echo "not found"  # 不够清晰

# SC2016: 单引号中的表达式不会展开
echo '$VAR'  # 字面 $VAR，不是变量展开

# SC2026: 此词非标准。在用于其他 Shell 的脚本时设置 POSIXLY_CORRECT
```

### SC2100-2199：引号问题

```bash
# SC2086: 使用双引号防止 globbing 和分词
for i in $list; do  # 应为：for i in $list 或 for i in "$list"
    echo "$i"
done

# SC2115: 路径中的字面波浪号未展开。使用 $HOME 代替
~/.bashrc  # 在字符串中，使用 "$HOME/.bashrc"

# SC2181: 使用 `if` 直接检查退出码，不要间接在列表中检查
some_command
if [ $? -eq 0 ]; then  # 更好：if some_command; then

# SC2206: 引用以防止分词或设置 IFS
array=( $items )  # 应使用：array=( $items )
```

### SC3000-3999：POSIX 合规性问题

```bash
# SC3010: 在 POSIX sh 中，使用 'case' 代替 'cond && foo'
[[ $var == "value" ]] && do_something  # 非 POSIX

# SC3043: 在 POSIX sh 中，使用 'local' 是未定义的
function my_func() {
    local var=value  # 在某些 Shell 中非 POSIX
}
```

## 实际配置示例

### 最小配置（严格 POSIX）

```bash
#!/bin/bash
# 配置最大可移植性

shellcheck \
  --shell=sh \
  --external-sources \
  --check-sourced \
  script.sh
```

### 开发配置（Bash，宽松规则）

```bash
#!/bin/bash
# 配置 Bash 开发

shellcheck \
  --shell=bash \
  --exclude=SC1091,SC2119 \
  --enable=all \
  script.sh
```

### CI/CD 集成配置

```bash
#!/bin/bash
set -Eeuo pipefail

# 分析所有 Shell 脚本并在有问题时失败
find . -type f -name "*.sh" | while read -r script; do
    echo "Checking: $script"
    shellcheck \
        --shell=bash \
        --format=gcc \
        --exclude=SC1091 \
        "$script" || exit 1
done
```

### 项目 .shellcheckrc

```
# 要分析的 Shell 方言
shell=bash

# 启用可选检查
enable=avoid-nullary-conditions,require-variable-braces,check-unassigned-uppercase

# 禁用特定警告
# SC1091: 不跟踪源文件（许多误报）
disable=SC1091

# SC2119: 使用 function_name 代替 function_name --（参数）
disable=SC2119

# 要源入的外部文件以获取上下文
external-sources=true
```

## 集成模式

### 预提交钩子配置

```bash
#!/bin/bash
# .git/hooks/pre-commit

#!/bin/bash
set -e

# 查找此提交中更改的所有 Shell 脚本
git diff --cached --name-only | grep '\.sh$' | while read -r script; do
    echo "Linting: $script"

    if ! shellcheck "$script"; then
        echo "ShellCheck failed on $script"
        exit 1
    fi
done
```

### GitHub Actions 工作流

```yaml
name: ShellCheck

on: [push, pull_request]

jobs:
  shellcheck:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run ShellCheck
        run: |
          sudo apt-get install shellcheck
          find . -type f -name "*.sh" -exec shellcheck {} \;
```

### GitLab CI 管道

```yaml
shellcheck:
  stage: lint
  image: koalaman/shellcheck-alpine
  script:
    - find . -type f -name "*.sh" -exec shellcheck {} \;
  allow_failure: false
```

## 处理 ShellCheck 违规

### 抑制特定警告

```bash
#!/bin/bash

# 禁用整行的警告
# shellcheck disable=SC2086
for file in $(ls -la); do
    echo "$file"
done

# 禁用整个脚本的警告
# shellcheck disable=SC1091,SC2119

# 禁用多个警告（格式不同）
command_that_fails() {
    # shellcheck disable=SC2015
    [ -f "$1" ] && echo "found" || echo "not found"
}

# 禁用源指令的特定检查
# shellcheck source=./helper.sh
source helper.sh
```

### 常见违规和修复

#### SC2086：使用双引号防止分词

```bash
# 问题
for i in $list; do done

# 解决方案
for i in $list; do done  # 如果 $list 已引用，或
for i in "${list[@]}"; do done  # 如果 list 是数组
```

#### SC2181：直接检查退出码

```bash
# 问题
some_command
if [ $? -eq 0 ]; then
    echo "success"
fi

# 解决方案
if some_command; then
    echo "success"
fi
```

#### SC2015：使用 if-then 代替 && ||

```bash
# 问题
[ -f "$file" ] && echo "exists" || echo "not found"

# 解决方案 - 更清晰的意图
if [ -f "$file" ]; then
    echo "exists"
else
    echo "not found"
fi
```

#### SC2016：单引号中的表达式不会展开

```bash
# 问题
echo 'Variable value: $VAR'

# 解决方案
echo "Variable value: $VAR"
```

#### SC2009：使用 pgrep 代替 grep

```bash
# 问题
ps aux | grep -v grep | grep myprocess

# 解决方案
pgrep -f myprocess
```

## 性能优化

### 检查多个文件

```bash
#!/bin/bash

# 顺序检查
for script in *.sh; do
    shellcheck "$script"
done

# 并行检查（更快）
find . -name "*.sh" -print0 | \
    xargs -0 -P 4 -n 1 shellcheck
```

### 缓存结果

```bash
#!/bin/bash

CACHE_DIR=".shellcheck_cache"
mkdir -p "$CACHE_DIR"

check_script() {
    local script="$1"
    local hash
    local cache_file

    hash=$(sha256sum "$script" | cut -d' ' -f1)
    cache_file="$CACHE_DIR/$hash"

    if [[ ! -f "$cache_file" ]]; then
        if shellcheck "$script" > "$cache_file" 2>&1; then
            touch "$cache_file.ok"
        else
            return 1
        fi
    fi

    [[ -f "$cache_file.ok" ]]
}

find . -name "*.sh" | while read -r script; do
    check_script "$script" || exit 1
done
```

## 输出格式

### 默认格式

```bash
shellcheck script.sh

# 输出：
# script.sh:1:3: warning: foo is referenced but not assigned. [SC2154]
```

### GCC 格式（用于 CI/CD）

```bash
shellcheck --format=gcc script.sh

# 输出：
# script.sh:1:3: warning: foo is referenced but not assigned.
```

### JSON 格式（用于解析）

```bash
shellcheck --format=json script.sh

# 输出：
# [{"file": "script.sh", "line": 1, "column": 3, "level": "warning", "code": 2154, "message": "..."}]
```

### 静默格式

```bash
shellcheck --format=quiet script.sh

# 发现问题时返回非零，否则无输出
```

## 最佳实践

1. **在 CI/CD 中运行 ShellCheck** - 在合并前捕获问题
2. **为您的目标 Shell 配置** - 不要将 bash 分析为 sh
3. **记录排除项** - 解释为什么抑制违规
4. **解决违规** - 不要只是禁用警告
5. **启用严格模式** - 使用 `--enable=all` 并谨慎排除
6. **定期更新** - 保持 ShellCheck 最新以获取新检查
7. **使用预提交钩子** - 在推送前本地捕获问题
8. **与编辑器集成** - 在开发过程中获得实时反馈
