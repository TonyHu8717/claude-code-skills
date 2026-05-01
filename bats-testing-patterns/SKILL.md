---
name: bats-testing-patterns
description: 掌握 Bash 自动化测试系统（Bats），用于全面的 Shell 脚本测试。用于编写 Shell 脚本的测试、CI/CD 流水线或需要测试驱动开发 Shell 工具时使用。
---

# Bats 测试模式

全面指导如何使用 Bats（Bash 自动化测试系统）为 Shell 脚本编写全面的单元测试，包括测试模式、测试夹具和生产级 Shell 测试的最佳实践。

## 何时使用此技能

- 为 Shell 脚本编写单元测试
- 为脚本实现测试驱动开发（TDD）
- 在 CI/CD 流水线中设置自动化测试
- 测试边界情况和错误条件
- 验证不同 Shell 环境中的行为
- 为脚本构建可维护的测试套件
- 为复杂测试场景创建夹具
- 测试多种 Shell 方言（bash、sh、dash）

## Bats 基础

### 什么是 Bats？

Bats（Bash 自动化测试系统）是一个符合 TAP（Test Anything Protocol）的 Shell 脚本测试框架，提供：

- 简单、自然的测试语法
- 与 CI 系统兼容的 TAP 输出格式
- 夹具和 setup/teardown 支持
- 断言辅助函数
- 并行测试执行

### 安装

```bash
# macOS 使用 Homebrew
brew install bats-core

# Ubuntu/Debian
git clone https://github.com/bats-core/bats-core.git
cd bats-core
./install.sh /usr/local

# 通过 npm（Node.js）
npm install --global bats

# 验证安装
bats --version
```

### 文件结构

```
project/
├── bin/
│   ├── script.sh
│   └── helper.sh
├── tests/
│   ├── test_script.bats
│   ├── test_helper.sh
│   ├── fixtures/
│   │   ├── input.txt
│   │   └── expected_output.txt
│   └── helpers/
│       └── mocks.bash
└── README.md
```

## 基本测试结构

### 简单测试文件

```bash
#!/usr/bin/env bats

# 加载测试辅助文件（如果存在）
load test_helper

# setup 在每个测试前运行
setup() {
    export TMPDIR=$(mktemp -d)
}

# teardown 在每个测试后运行
teardown() {
    rm -rf "$TMPDIR"
}

# 测试：简单断言
@test "Function returns 0 on success" {
    run my_function "input"
    [ "$status" -eq 0 ]
}

# 测试：输出验证
@test "Function outputs correct result" {
    run my_function "test"
    [ "$output" = "expected output" ]
}

# 测试：错误处理
@test "Function returns 1 on missing argument" {
    run my_function
    [ "$status" -eq 1 ]
}
```

## 断言模式

### 退出码断言

```bash
#!/usr/bin/env bats

@test "Command succeeds" {
    run true
    [ "$status" -eq 0 ]
}

@test "Command fails as expected" {
    run false
    [ "$status" -ne 0 ]
}

@test "Command returns specific exit code" {
    run my_function --invalid
    [ "$status" -eq 127 ]
}

@test "Can capture command result" {
    run echo "hello"
    [ $status -eq 0 ]
    [ "$output" = "hello" ]
}
```

### 输出断言

```bash
#!/usr/bin/env bats

@test "Output matches string" {
    result=$(echo "hello world")
    [ "$result" = "hello world" ]
}

@test "Output contains substring" {
    result=$(echo "hello world")
    [[ "$result" == *"world"* ]]
}

@test "Output matches pattern" {
    result=$(date +%Y)
    [[ "$result" =~ ^[0-9]{4}$ ]]
}

@test "Multi-line output" {
    run printf "line1\nline2\nline3"
    [ "$output" = "line1
line2
line3" ]
}

@test "Lines variable contains output" {
    run printf "line1\nline2\nline3"
    [ "${lines[0]}" = "line1" ]
    [ "${lines[1]}" = "line2" ]
    [ "${lines[2]}" = "line3" ]
}
```

### 文件断言

```bash
#!/usr/bin/env bats

@test "File is created" {
    [ ! -f "$TMPDIR/output.txt" ]
    my_function > "$TMPDIR/output.txt"
    [ -f "$TMPDIR/output.txt" ]
}

@test "File contents match expected" {
    my_function > "$TMPDIR/output.txt"
    [ "$(cat "$TMPDIR/output.txt")" = "expected content" ]
}

@test "File is readable" {
    touch "$TMPDIR/test.txt"
    [ -r "$TMPDIR/test.txt" ]
}

@test "File has correct permissions" {
    touch "$TMPDIR/test.txt"
    chmod 644 "$TMPDIR/test.txt"
    [ "$(stat -f %OLp "$TMPDIR/test.txt")" = "644" ]
}

@test "File size is correct" {
    echo -n "12345" > "$TMPDIR/test.txt"
    [ "$(wc -c < "$TMPDIR/test.txt")" -eq 5 ]
}
```

## Setup 和 Teardown 模式

### 基本 Setup 和 Teardown

```bash
#!/usr/bin/env bats

setup() {
    # 创建测试目录
    TEST_DIR=$(mktemp -d)
    export TEST_DIR

    # 引入被测脚本
    source "${BATS_TEST_DIRNAME}/../bin/script.sh"
}

teardown() {
    # 清理临时目录
    rm -rf "$TEST_DIR"
}

@test "Test using TEST_DIR" {
    touch "$TEST_DIR/file.txt"
    [ -f "$TEST_DIR/file.txt" ]
}
```

### 带资源的 Setup

```bash
#!/usr/bin/env bats

setup() {
    # 创建目录结构
    mkdir -p "$TMPDIR/data/input"
    mkdir -p "$TMPDIR/data/output"

    # 创建测试夹具
    echo "line1" > "$TMPDIR/data/input/file1.txt"
    echo "line2" > "$TMPDIR/data/input/file2.txt"

    # 初始化环境
    export DATA_DIR="$TMPDIR/data"
    export INPUT_DIR="$DATA_DIR/input"
    export OUTPUT_DIR="$DATA_DIR/output"
}

teardown() {
    rm -rf "$TMPDIR/data"
}

@test "Processes input files" {
    run my_process_script "$INPUT_DIR" "$OUTPUT_DIR"
    [ "$status" -eq 0 ]
    [ -f "$OUTPUT_DIR/file1.txt" ]
}
```

### 全局 Setup/Teardown

```bash
#!/usr/bin/env bats

# 从 test_helper.sh 加载共享设置
load test_helper

# setup_file 在所有测试前运行一次
setup_file() {
    export SHARED_RESOURCE=$(mktemp -d)
    echo "Expensive setup" > "$SHARED_RESOURCE/data.txt"
}

# teardown_file 在所有测试后运行一次
teardown_file() {
    rm -rf "$SHARED_RESOURCE"
}

@test "First test uses shared resource" {
    [ -f "$SHARED_RESOURCE/data.txt" ]
}

@test "Second test uses shared resource" {
    [ -d "$SHARED_RESOURCE" ]
}
```

## 模拟和打桩模式

### 函数模拟

```bash
#!/usr/bin/env bats

# 模拟外部命令
my_external_tool() {
    echo "mocked output"
    return 0
}

@test "Function uses mocked tool" {
    export -f my_external_tool
    run my_function
    [[ "$output" == *"mocked output"* ]]
}
```

### 命令打桩

```bash
#!/usr/bin/env bats

setup() {
    # 创建桩目录
    STUBS_DIR="$TMPDIR/stubs"
    mkdir -p "$STUBS_DIR"

    # 添加到 PATH
    export PATH="$STUBS_DIR:$PATH"
}

create_stub() {
    local cmd="$1"
    local output="$2"
    local code="${3:-0}"

    cat > "$STUBS_DIR/$cmd" <<EOF
#!/bin/bash
echo "$output"
exit $code
EOF
    chmod +x "$STUBS_DIR/$cmd"
}

@test "Function works with stubbed curl" {
    create_stub curl "{ \"status\": \"ok\" }" 0
    run my_api_function
    [ "$status" -eq 0 ]
}
```

### 变量打桩

```bash
#!/usr/bin/env bats

@test "Function handles environment override" {
    export MY_SETTING="override_value"
    run my_function
    [ "$status" -eq 0 ]
    [[ "$output" == *"override_value"* ]]
}

@test "Function uses default when var unset" {
    unset MY_SETTING
    run my_function
    [ "$status" -eq 0 ]
    [[ "$output" == *"default"* ]]
}
```

## 夹具管理

### 使用夹具文件

```bash
#!/usr/bin/env bats

# 夹具目录：tests/fixtures/

setup() {
    FIXTURES_DIR="${BATS_TEST_DIRNAME}/fixtures"
    WORK_DIR=$(mktemp -d)
    export WORK_DIR
}

teardown() {
    rm -rf "$WORK_DIR"
}

@test "Process fixture file" {
    # 将夹具复制到工作目录
    cp "$FIXTURES_DIR/input.txt" "$WORK_DIR/input.txt"

    # 运行函数
    run my_process_function "$WORK_DIR/input.txt"

    # 比较输出
    diff "$WORK_DIR/output.txt" "$FIXTURES_DIR/expected_output.txt"
}
```

### 动态夹具生成

```bash
#!/usr/bin/env bats

generate_fixture() {
    local lines="$1"
    local file="$2"

    for i in $(seq 1 "$lines"); do
        echo "Line $i content" >> "$file"
    done
}

@test "Handle large input file" {
    generate_fixture 1000 "$TMPDIR/large.txt"
    run my_function "$TMPDIR/large.txt"
    [ "$status" -eq 0 ]
    [ "$(wc -l < "$TMPDIR/large.txt")" -eq 1000 ]
}
```

## 高级模式

### 测试错误条件

```bash
#!/usr/bin/env bats

@test "Function fails with missing file" {
    run my_function "/nonexistent/file.txt"
    [ "$status" -ne 0 ]
    [[ "$output" == *"not found"* ]]
}

@test "Function fails with invalid input" {
    run my_function ""
    [ "$status" -ne 0 ]
}

@test "Function fails with permission denied" {
    touch "$TMPDIR/readonly.txt"
    chmod 000 "$TMPDIR/readonly.txt"
    run my_function "$TMPDIR/readonly.txt"
    [ "$status" -ne 0 ]
    chmod 644 "$TMPDIR/readonly.txt"  # 清理
}

@test "Function provides helpful error message" {
    run my_function --invalid-option
    [ "$status" -ne 0 ]
    [[ "$output" == *"Usage:"* ]]
}
```

### 带依赖的测试

```bash
#!/usr/bin/env bats

setup() {
    # 检查必需工具
    if ! command -v jq &>/dev/null; then
        skip "jq is not installed"
    fi

    export SCRIPT="${BATS_TEST_DIRNAME}/../bin/script.sh"
}

@test "JSON parsing works" {
    skip_if ! command -v jq &>/dev/null
    run my_json_parser '{"key": "value"}'
    [ "$status" -eq 0 ]
}
```

### 测试 Shell 兼容性

```bash
#!/usr/bin/env bats

@test "Script works in bash" {
    bash "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
}

@test "Script works in sh (POSIX)" {
    sh "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
}

@test "Script works in dash" {
    if command -v dash &>/dev/null; then
        dash "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
    else
        skip "dash not installed"
    fi
}
```

### 并行执行

```bash
#!/usr/bin/env bats

@test "Multiple independent operations" {
    run bash -c 'for i in {1..10}; do
        my_operation "$i" &
    done
    wait'
    [ "$status" -eq 0 ]
}

@test "Concurrent file operations" {
    for i in {1..5}; do
        my_function "$TMPDIR/file$i" &
    done
    wait
    [ -f "$TMPDIR/file1" ]
    [ -f "$TMPDIR/file5" ]
}
```

## 测试辅助模式

### test_helper.sh

```bash
#!/usr/bin/env bash

# 引入被测脚本
export SCRIPT_DIR="${BATS_TEST_DIRNAME%/*}/bin"

# 通用测试工具
assert_file_exists() {
    if [ ! -f "$1" ]; then
        echo "Expected file to exist: $1"
        return 1
    fi
}

assert_file_equals() {
    local file="$1"
    local expected="$2"

    if [ ! -f "$file" ]; then
        echo "File does not exist: $file"
        return 1
    fi

    local actual=$(cat "$file")
    if [ "$actual" != "$expected" ]; then
        echo "File contents do not match"
        echo "Expected: $expected"
        echo "Actual: $actual"
        return 1
    fi
}

# 创建临时测试目录
setup_test_dir() {
    export TEST_DIR=$(mktemp -d)
}

cleanup_test_dir() {
    rm -rf "$TEST_DIR"
}
```

## 与 CI/CD 集成

### GitHub Actions 工作流

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install Bats
        run: |
          npm install --global bats

      - name: Run Tests
        run: |
          bats tests/*.bats

      - name: Run Tests with Tap Reporter
        run: |
          bats tests/*.bats --tap | tee test_output.tap
```

### Makefile 集成

```makefile
.PHONY: test test-verbose test-tap

test:
	bats tests/*.bats

test-verbose:
	bats tests/*.bats --verbose

test-tap:
	bats tests/*.bats --tap

test-parallel:
	bats tests/*.bats --parallel 4

coverage: test
	# 可选：生成覆盖率报告
```

## 最佳实践

1. **每个测试只测试一件事** - 单一职责原则
2. **使用描述性测试名称** - 清楚说明正在测试什么
3. **测试后清理** - 始终在 teardown 中删除临时文件
4. **同时测试成功和失败路径** - 不要只测试正常路径
5. **模拟外部依赖** - 隔离被测单元
6. **对复杂数据使用夹具** - 使测试更具可读性
7. **在 CI/CD 中运行测试** - 尽早发现回归
8. **跨 Shell 方言测试** - 确保可移植性
9. **保持测试快速** - 尽可能并行运行
10. **记录复杂的测试设置** - 解释不寻常的模式
