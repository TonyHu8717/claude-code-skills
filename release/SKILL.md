---
name: release
description: 通用发布助手 -- 分析仓库发布规则，缓存到 .omc/RELEASE_RULE.md，然后引导发布流程
level: 3
---

# 发布技能

一个轻量级的、感知仓库的发布助手。首次运行时检查项目和 CI 以推导发布规则，存储到 `.omc/RELEASE_RULE.md` 供未来使用，然后使用这些规则引导你完成发布。

## 用法

```
/oh-my-claudecode:release [version]
```

- `version` 是可选的。如果省略，技能会询问。接受 `patch`、`minor`、`major` 或显式语义版本如 `2.4.0`。
- 添加 `--refresh` 强制重新分析仓库，即使缓存的规则文件已存在。

## 执行流程

### 步骤 0 -- 加载或构建发布规则

检查 `.omc/RELEASE_RULE.md` 是否存在。

**如果不存在（或传入了 `--refresh`）：** 运行下方完整的仓库分析并写入文件。

**如果存在：** 读取文件。然后进行快速差异检查 -- 扫描 `.github/workflows/`（或等效 CI 目录：`.circleci/`、`.travis.yml`、`Jenkinsfile`、`bitbucket-pipelines.yml`、`gitlab-ci.yml`）中比规则文件中 `last-analyzed` 时间戳更新的修改。如果相关工作流文件已更改，重新运行这些部分的分析并更新文件。报告更改内容。

---

### 步骤 1 -- 仓库分析（首次运行或 --refresh）

检查仓库并回答以下问题。将答案写入 `.omc/RELEASE_RULE.md`。

#### 1a. 版本来源

- 定位所有包含与 `package.json` / `pyproject.toml` / `Cargo.toml` / `build.gradle` / `VERSION` 文件等中当前版本匹配的版本字符串的文件。
- 列出每个文件和用于查找版本的字段或正则表达式模式。
- 检测是否有发布自动化脚本（例如 `scripts/release.*`、`Makefile release` 目标、`bump2version`、`release-it`、`semantic-release`、`changesets`、`goreleaser`）。

#### 1b. 注册表 / 分发

- npm（`package.json` 带 `publishConfig` 或 CI 中的 `npm publish`）、PyPI（`pyproject.toml` + `twine`/`flit`）、Cargo（`Cargo.toml`）、Docker（`Dockerfile` + 推送步骤）、GitHub Packages、其他。
- 是否有在标签推送时自动发布的 CI 步骤？哪个工作流文件和作业？

#### 1c. 发布触发器

- 识别什么启动发布：标签推送（`v*`）、手动触发（`workflow_dispatch`）、合并到 main/master、发布分支合并、提交消息模式。

#### 1d. 测试门控

- 识别测试命令和它在 CI 中运行的位置。
- 发布前是否需要通过测试？注意任何绕过标志。

#### 1e. 发布说明 / 变更日志

- 是否存在 `CHANGELOG.md` 或 `CHANGELOG.rst`？
- 使用什么约定：Keep a Changelog、Conventional Commits、GitHub 自动生成、无？
- 是否有在标签前提交的发布正文文件（例如 `.github/release-body.md`）？

#### 1f. 首次用户检查

- `.github/workflows/`（或等效目录）中是否存在发布工作流？如果不存在，标记并提供创建建议。
- `.gitignore` 中是否有防止构建产物被提交的条目？如果没有，标记。
- 是否使用 git 标签？运行 `git tag --list` 检查。如果不存在标签，标记并解释最佳实践。

---

### 步骤 2 -- 写入 `.omc/RELEASE_RULE.md`

使用此结构创建或覆盖文件：

```markdown
# 发布规则
<!-- last-analyzed: YYYY-MM-DDTHH:MM:SSZ -->

## 版本来源
<!-- 文件列表 + 模式 -->

## 发布触发器
<!-- 什么触发发布 -->

## 测试门控
<!-- 命令 + CI 作业名称 -->

## 注册表 / 分发
<!-- npm、PyPI、Docker 等 + 发布的 CI 作业 -->

## 发布说明策略
<!-- 约定 + 文件 -->

## CI 工作流文件
<!-- 相关工作流文件路径 -->

## 首次设置缺口
<!-- 分析期间发现的缺失部分，或"无" -->
```

---

### 步骤 3 -- 确定版本

如果用户提供了版本参数，使用它。否则：

1. 显示当前版本（从主版本文件）。
2. 显示 `patch`、`minor` 和 `major` 会产生什么。
3. 询问用户使用哪个。

验证所选版本是有效的语义版本字符串。

---

### 步骤 4 -- 发布前检查清单

展示从发布规则推导的检查清单。至少包括：

- [ ] 此发布预期的所有更改已提交并推送
- [ ] 目标分支上 CI 是绿色的
- [ ] 测试在本地通过（运行测试门控命令）
- [ ] 版本号已应用到所有版本来源文件
- [ ] 发布说明 / 变更日志已准备（见步骤 5）

请用户确认后继续，或如果他们说"继续"则运行每个步骤。

---

### 步骤 5 -- 发布说明指导

帮助用户编写好的发布说明。应用仓库使用的任何约定。未检测到约定时的默认指导：

**好的发布说明要素：**
- 以**用户看到的变化**开头，而不是内部实现细节。
- 按类型分组：`新功能`、`Bug 修复`、`破坏性更改`、`弃用`、`内部/杂项`。
- 每项：一句话，链接到 PR 或 issue，如果是外部贡献者则注明。
- **破坏性更改**放在最前面，必须包含迁移路径。
- 省略用户看不到的更改（重构、CI 调整、仅测试更改），除非它们影响构建可重复性。

**示例条目格式：**
```
### Bug 修复
- 修复令牌过期时会话断开的问题（#123）— @contributor
```

如果仓库使用 Conventional Commits，从 `git log <prev-tag>..HEAD --no-merges --format="%s"` 按提交类型分组生成变更日志草稿。展示给用户并让他们编辑。

---

### 步骤 6 -- 执行发布

使用发现的规则，逐步执行：

1. **提升版本** -- 应用到每个版本来源文件。
2. **运行测试** -- 执行测试门控命令。
3. **提交** -- `git add <version files> CHANGELOG.md` 并以 `chore(release): bump version to vX.Y.Z` 提交。
4. **打标签** -- `git tag -a vX.Y.Z -m "vX.Y.Z"`（注释标签优于轻量标签）。
5. **推送** -- `git push origin <branch> && git push origin vX.Y.Z`。
6. **CI 接管** -- 如果发布触发器是标签推送，提醒用户 CI 将处理其余部分（发布、GitHub Release 创建）。显示预期的 CI 工作流文件。
7. **手动发布** -- 如果没有 CI 自动化，列出手动发布命令（例如 `npm publish --access public`、`twine upload dist/*`）。

---

### 步骤 7 -- 首次设置建议

如果在步骤 1f 中发现缺口，提供具体帮助：

**无发布工作流：**
> 你的仓库没有发布 CI 工作流。在 `v*` 标签推送时触发的 GitHub Actions 工作流是最常见的最佳实践。它可以：
> - 运行测试
> - 发布到 npm/PyPI 等
> - 使用你的发布说明创建 GitHub Release
>
> 要我为你的技术栈创建一个 `.github/workflows/release.yml` 吗？

**无 git 标签：**
> 这似乎是首次发布。Git 标签让 GitHub、npm 和其他工具理解你的版本历史。我们将在步骤 6 中创建你的第一个标签。

**构建产物未被 gitignore：**
> 构建产物存在于 git 历史中或未被 gitignore。这会膨胀仓库大小并产生合并冲突。要我将它们添加到 `.gitignore` 吗？

---

### 步骤 8 -- 验证

推送后：
- 检查 CI 状态：`gh run list --workflow=<release workflow> --limit=3`（如果 `gh` 可用）。
- 几分钟后检查注册表（npm、PyPI）是否有新版本。
- 确认 GitHub Release 已创建：`gh release view vX.Y.Z`。

报告成功或标记任何失败。

---

## 注意事项

- 此技能**不**硬编码任何项目特定的版本文件或命令。一切从仓库检查推导。
- `.omc/RELEASE_RULE.md` 是本地缓存。如果你想与团队共享推导的规则，将其提交到仓库；如果希望保持本地，添加到 `.gitignore`。
- 对于复杂的 monorepo 或多包工作空间，技能将检测工作空间模式（npm 工作空间、pnpm 工作空间、Cargo 工作空间）并相应调整。
