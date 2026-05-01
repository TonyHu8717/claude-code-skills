---
name: bazel-build-optimization
description: 优化大规模单仓库的 Bazel 构建。用于配置 Bazel、实现远程执行或优化企业代码库的构建性能时使用。
---

# Bazel 构建优化

大规模单仓库中 Bazel 的生产模式。

## 何时使用此技能

- 为单仓库设置 Bazel
- 配置远程缓存/执行
- 优化构建时间
- 编写自定义 Bazel 规则
- 调试构建问题
- 迁移到 Bazel

## 核心概念

### 1. Bazel 架构

```
workspace/
├── WORKSPACE.bazel       # 外部依赖
├── .bazelrc              # 构建配置
├── .bazelversion         # Bazel 版本
├── BUILD.bazel           # 根构建文件
├── apps/
│   └── web/
│       └── BUILD.bazel
├── libs/
│   └── utils/
│       └── BUILD.bazel
└── tools/
    └── bazel/
        └── rules/
```

### 2. 关键概念

| 概念 | 描述 |
| ----------- | -------------------------------------- |
| **Target** | 可构建单元（库、二进制文件、测试） |
| **Package** | 包含 BUILD 文件的目录 |
| **Label** | 目标标识符 `//path/to:target` |
| **Rule** | 定义如何构建目标 |
| **Aspect** | 横切构建行为 |

## 模板

### 模板 1：WORKSPACE 配置

```python
# WORKSPACE.bazel
workspace(name = "myproject")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# JavaScript/TypeScript 规则
http_archive(
    name = "aspect_rules_js",
    sha256 = "...",
    strip_prefix = "rules_js-1.34.0",
    url = "https://github.com/aspect-build/rules_js/releases/download/v1.34.0/rules_js-v1.34.0.tar.gz",
)

load("@aspect_rules_js//js:repositories.bzl", "rules_js_dependencies")
rules_js_dependencies()

load("@rules_nodejs//nodejs:repositories.bzl", "nodejs_register_toolchains")
nodejs_register_toolchains(
    name = "nodejs",
    node_version = "20.9.0",
)

load("@aspect_rules_js//npm:repositories.bzl", "npm_translate_lock")
npm_translate_lock(
    name = "npm",
    pnpm_lock = "//:pnpm-lock.yaml",
    verify_node_modules_ignored = "//:.bazelignore",
)

load("@npm//:repositories.bzl", "npm_repositories")
npm_repositories()

# Python 规则
http_archive(
    name = "rules_python",
    sha256 = "...",
    strip_prefix = "rules_python-0.27.0",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.27.0/rules_python-0.27.0.tar.gz",
)

load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()
```

### 模板 2：.bazelrc 配置

```bash
# .bazelrc

# 构建设置
build --enable_platform_specific_config
build --incompatible_enable_cc_toolchain_resolution
build --experimental_strict_conflict_checks

# 性能
build --jobs=auto
build --local_cpu_resources=HOST_CPUS*.75
build --local_ram_resources=HOST_RAM*.75

# 缓存
build --disk_cache=~/.cache/bazel-disk
build --repository_cache=~/.cache/bazel-repo

# 远程缓存（可选）
build:remote-cache --remote_cache=grpcs://cache.example.com
build:remote-cache --remote_upload_local_results=true
build:remote-cache --remote_timeout=3600

# 远程执行（可选）
build:remote-exec --remote_executor=grpcs://remote.example.com
build:remote-exec --remote_instance_name=projects/myproject/instances/default
build:remote-exec --jobs=500

# 平台配置
build:linux --platforms=//platforms:linux_x86_64
build:macos --platforms=//platforms:macos_arm64

# CI 配置
build:ci --config=remote-cache
build:ci --build_metadata=ROLE=CI
build:ci --bes_results_url=https://results.example.com/invocation/
build:ci --bes_backend=grpcs://bes.example.com

# 测试设置
test --test_output=errors
test --test_summary=detailed

# 覆盖率
coverage --combined_report=lcov
coverage --instrumentation_filter="//..."

# 便捷别名
build:opt --compilation_mode=opt
build:dbg --compilation_mode=dbg

# 导入用户设置
try-import %workspace%/user.bazelrc
```

### 模板 3：TypeScript 库 BUILD

```python
# libs/utils/BUILD.bazel
load("@aspect_rules_ts//ts:defs.bzl", "ts_project")
load("@aspect_rules_js//js:defs.bzl", "js_library")
load("@npm//:defs.bzl", "npm_link_all_packages")

npm_link_all_packages(name = "node_modules")

ts_project(
    name = "utils_ts",
    srcs = glob(["src/**/*.ts"]),
    declaration = True,
    source_map = True,
    tsconfig = "//:tsconfig.json",
    deps = [
        ":node_modules/@types/node",
    ],
)

js_library(
    name = "utils",
    srcs = [":utils_ts"],
    visibility = ["//visibility:public"],
)

# 测试
load("@aspect_rules_jest//jest:defs.bzl", "jest_test")

jest_test(
    name = "utils_test",
    config = "//:jest.config.js",
    data = [
        ":utils",
        "//:node_modules/jest",
    ],
    node_modules = "//:node_modules",
)
```

### 模板 4：Python 库 BUILD

```python
# libs/ml/BUILD.bazel
load("@rules_python//python:defs.bzl", "py_library", "py_test", "py_binary")
load("@pip//:requirements.bzl", "requirement")

py_library(
    name = "ml",
    srcs = glob(["src/**/*.py"]),
    deps = [
        requirement("numpy"),
        requirement("pandas"),
        requirement("scikit-learn"),
        "//libs/utils:utils_py",
    ],
    visibility = ["//visibility:public"],
)

py_test(
    name = "ml_test",
    srcs = glob(["tests/**/*.py"]),
    deps = [
        ":ml",
        requirement("pytest"),
    ],
    size = "medium",
    timeout = "moderate",
)

py_binary(
    name = "train",
    srcs = ["train.py"],
    deps = [":ml"],
    data = ["//data:training_data"],
)
```

### 模板 5：Docker 自定义规则

```python
# tools/bazel/rules/docker.bzl
def _docker_image_impl(ctx):
    dockerfile = ctx.file.dockerfile
    base_image = ctx.attr.base_image
    layers = ctx.files.layers

    # 构建镜像
    output = ctx.actions.declare_file(ctx.attr.name + ".tar")

    args = ctx.actions.args()
    args.add("--dockerfile", dockerfile)
    args.add("--output", output)
    args.add("--base", base_image)
    args.add_all("--layer", layers)

    ctx.actions.run(
        inputs = [dockerfile] + layers,
        outputs = [output],
        executable = ctx.executable._builder,
        arguments = [args],
        mnemonic = "DockerBuild",
        progress_message = "Building Docker image %s" % ctx.label,
    )

    return [DefaultInfo(files = depset([output]))]

docker_image = rule(
    implementation = _docker_image_impl,
    attrs = {
        "dockerfile": attr.label(
            allow_single_file = [".dockerfile", "Dockerfile"],
            mandatory = True,
        ),
        "base_image": attr.string(mandatory = True),
        "layers": attr.label_list(allow_files = True),
        "_builder": attr.label(
            default = "//tools/docker:builder",
            executable = True,
            cfg = "exec",
        ),
    },
)
```

### 模板 6：查询和依赖分析

```bash
# 查找目标的所有依赖
bazel query "deps(//apps/web:web)"

# 查找反向依赖（哪些目标依赖于此）
bazel query "rdeps(//..., //libs/utils:utils)"

# 查找包中的所有目标
bazel query "//libs/..."

# 查找自上次提交以来更改的目标
bazel query "rdeps(//..., set($(git diff --name-only HEAD~1 | sed 's/.*/"&"/' | tr '\n' ' ')))"

# 生成依赖图
bazel query "deps(//apps/web:web)" --output=graph | dot -Tpng > deps.png

# 查找所有测试目标
bazel query "kind('.*_test', //...)"

# 查找带有特定标签的目标
bazel query "attr(tags, 'integration', //...)"

# 计算构建图大小
bazel query "deps(//...)" --output=package | wc -l
```

### 模板 7：远程执行设置

```python
# platforms/BUILD.bazel
platform(
    name = "linux_x86_64",
    constraint_values = [
        "@platforms//os:linux",
        "@platforms//cpu:x86_64",
    ],
    exec_properties = {
        "container-image": "docker://gcr.io/myproject/bazel-worker:latest",
        "OSFamily": "Linux",
    },
)

platform(
    name = "remote_linux",
    parents = [":linux_x86_64"],
    exec_properties = {
        "Pool": "default",
        "dockerNetwork": "standard",
    },
)

# toolchains/BUILD.bazel
toolchain(
    name = "cc_toolchain_linux",
    exec_compatible_with = [
        "@platforms//os:linux",
        "@platforms//cpu:x86_64",
    ],
    target_compatible_with = [
        "@platforms//os:linux",
        "@platforms//cpu:x86_64",
    ],
    toolchain = "@remotejdk11_linux//:jdk",
    toolchain_type = "@bazel_tools//tools/jdk:runtime_toolchain_type",
)
```

## 性能优化

```bash
# 分析构建
bazel build //... --profile=profile.json
bazel analyze-profile profile.json

# 识别慢操作
bazel build //... --execution_log_json_file=exec_log.json

# 内存分析
bazel build //... --memory_profile=memory.json

# 跳过分析缓存
bazel build //... --notrack_incremental_state
```

## 最佳实践

### 应该做的

- **使用细粒度目标** - 更好的缓存
- **固定依赖版本** - 可重现的构建
- **启用远程缓存** - 共享构建产物
- **明智地使用可见性** - 强制架构约束
- **每个目录编写 BUILD 文件** - 标准约定

### 不应该做的

- **不要对 deps 使用 glob** - 显式声明更好
- **不要提交 bazel-\* 目录** - 添加到 .gitignore
- **不要跳过 WORKSPACE 设置** - 构建的基础
- **不要忽略构建警告** - 技术债务
