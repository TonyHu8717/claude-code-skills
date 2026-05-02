---
name: changelog-automation
description: 从提交、PR 和发布自动生成变更日志，遵循 Keep a Changelog 格式。在设置发布工作流、生成发布说明或标准化提交规范时使用。
---

# 变更日志自动化

自动化变更日志生成、发布说明和版本管理的模式和工具，遵循行业标准。

## 使用场景

- 设置自动化变更日志生成
- 实施约定式提交（Conventional Commits）
- 创建发布说明工作流
- 标准化提交消息格式
- 生成 GitHub/GitLab 发布说明
- 管理语义化版本控制

## 核心概念

### 1. Keep a Changelog 格式

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New feature X

## [1.2.0] - 2024-01-15

### Added

- User profile avatars
- Dark mode support

### Changed

- Improved loading performance by 40%

### Deprecated

- Old authentication API (use v2)

### Removed

- Legacy payment gateway

### Fixed

- Login timeout issue (#123)

### Security

- Updated dependencies for CVE-2024-1234

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
```

### 2. 约定式提交

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

| 类型 | 描述 | 变更日志分区 |
|------|------|--------------|
| `feat` | 新功能 | Added |
| `fix` | Bug 修复 | Fixed |
| `docs` | 文档 | （通常排除） |
| `style` | 格式化 | （通常排除） |
| `refactor` | 代码重构 | Changed |
| `perf` | 性能 | Changed |
| `test` | 测试 | （通常排除） |
| `chore` | 维护 | （通常排除） |
| `ci` | CI 变更 | （通常排除） |
| `build` | 构建系统 | （通常排除） |
| `revert` | 回滚提交 | Removed |

### 3. 语义化版本控制

```
MAJOR.MINOR.PATCH

MAJOR：破坏性变更（feat! 或 BREAKING CHANGE）
MINOR：新功能（feat）
PATCH：Bug 修复（fix）
```

## 实施方法

### 方法 1：Conventional Changelog（Node.js）

```bash
# 安装工具
npm install -D @commitlint/cli @commitlint/config-conventional
npm install -D husky
npm install -D standard-version
# 或
npm install -D semantic-release

# 设置 commitlint
cat > commitlint.config.js << 'EOF'
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'chore',
        'ci',
        'build',
        'revert',
      ],
    ],
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
    'subject-max-length': [2, 'always', 72],
  },
};
EOF

# 设置 husky
npx husky init
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg
```

### 方法 2：standard-version 配置

```javascript
// .versionrc.js
module.exports = {
  types: [
    { type: "feat", section: "Features" },
    { type: "fix", section: "Bug Fixes" },
    { type: "perf", section: "Performance Improvements" },
    { type: "revert", section: "Reverts" },
    { type: "docs", section: "Documentation", hidden: true },
    { type: "style", section: "Styles", hidden: true },
    { type: "chore", section: "Miscellaneous", hidden: true },
    { type: "refactor", section: "Code Refactoring", hidden: true },
    { type: "test", section: "Tests", hidden: true },
    { type: "build", section: "Build System", hidden: true },
    { type: "ci", section: "CI/CD", hidden: true },
  ],
  commitUrlFormat: "{{host}}/{{owner}}/{{repository}}/commit/{{hash}}",
  compareUrlFormat:
    "{{host}}/{{owner}}/{{repository}}/compare/{{previousTag}}...{{currentTag}}",
  issueUrlFormat: "{{host}}/{{owner}}/{{repository}}/issues/{{id}}",
  userUrlFormat: "{{host}}/{{user}}",
  releaseCommitMessageFormat: "chore(release): {{currentTag}}",
  scripts: {
    prebump: 'echo "Running prebump"',
    postbump: 'echo "Running postbump"',
    prechangelog: 'echo "Running prechangelog"',
    postchangelog: 'echo "Running postchangelog"',
  },
};
```

```json
// package.json scripts
{
  "scripts": {
    "release": "standard-version",
    "release:minor": "standard-version --release-as minor",
    "release:major": "standard-version --release-as major",
    "release:patch": "standard-version --release-as patch",
    "release:dry": "standard-version --dry-run"
  }
}
```

### 方法 3：semantic-release（完全自动化）

```javascript
// release.config.js
module.exports = {
  branches: [
    "main",
    { name: "beta", prerelease: true },
    { name: "alpha", prerelease: true },
  ],
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/changelog",
      {
        changelogFile: "CHANGELOG.md",
      },
    ],
    [
      "@semantic-release/npm",
      {
        npmPublish: true,
      },
    ],
    [
      "@semantic-release/github",
      {
        assets: ["dist/**/*.js", "dist/**/*.css"],
      },
    ],
    [
      "@semantic-release/git",
      {
        assets: ["CHANGELOG.md", "package.json"],
        message:
          "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
      },
    ],
  ],
};
```

### 方法 4：GitHub Actions 工作流

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      release_type:
        description: "Release type"
        required: true
        default: "patch"
        type: choice
        options:
          - patch
          - minor
          - major

permissions:
  contents: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - run: npm ci

      - name: Configure Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release

  # 替代方案：使用 standard-version 的手动发布
  manual-release:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - run: npm ci

      - name: Configure Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Bump version and generate changelog
        run: npx standard-version --release-as ${{ inputs.release_type }}

      - name: Push changes
        run: git push --follow-tags origin master

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: ${{ steps.version.outputs.tag }}
          body_path: RELEASE_NOTES.md
          generate_release_notes: true
```

### 方法 5：git-cliff（基于 Rust，快速）

```toml
# cliff.toml
[changelog]
header = """
# Changelog

All notable changes to this project will be documented in this file.

"""
body = """
{% if version %}\
    ## [{{ version | trim_start_matches(pat="v") }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [Unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | upper_first }}
    {% for commit in commits %}
        - {% if commit.scope %}**{{ commit.scope }}:** {% endif %}\
            {{ commit.message | upper_first }}\
            {% if commit.github.pr_number %} ([#{{ commit.github.pr_number }}](https://github.com/owner/repo/pull/{{ commit.github.pr_number }})){% endif %}\
    {% endfor %}
{% endfor %}
"""
footer = """
{% for release in releases -%}
    {% if release.version -%}
        {% if release.previous.version -%}
            [{{ release.version | trim_start_matches(pat="v") }}]: \
                https://github.com/owner/repo/compare/{{ release.previous.version }}...{{ release.version }}
        {% endif -%}
    {% else -%}
        [unreleased]: https://github.com/owner/repo/compare/{{ release.previous.version }}...HEAD
    {% endif -%}
{% endfor %}
"""
trim = true

[git]
conventional_commits = true
filter_unconventional = true
split_commits = false
commit_parsers = [
    { message = "^feat", group = "Features" },
    { message = "^fix", group = "Bug Fixes" },
    { message = "^doc", group = "Documentation" },
    { message = "^perf", group = "Performance" },
    { message = "^refactor", group = "Refactoring" },
    { message = "^style", group = "Styling" },
    { message = "^test", group = "Testing" },
    { message = "^chore\\(release\\)", skip = true },
    { message = "^chore", group = "Miscellaneous" },
]
filter_commits = false
tag_pattern = "v[0-9]*"
skip_tags = ""
ignore_tags = ""
topo_order = false
sort_commits = "oldest"

[github]
owner = "owner"
repo = "repo"
```

```bash
# 生成变更日志
git cliff -o CHANGELOG.md

# 生成特定范围的变更日志
git cliff v1.0.0..v2.0.0 -o RELEASE_NOTES.md

# 预览但不写入
git cliff --unreleased --dry-run
```

### 方法 6：Python（commitizen）

```toml
# pyproject.toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "1.0.0"
version_files = [
    "pyproject.toml:version",
    "src/__init__.py:__version__",
]
tag_format = "v$version"
update_changelog_on_bump = true
changelog_incremental = true
changelog_start_rev = "v0.1.0"

[tool.commitizen.customize]
message_template = "{{change_type}}{% if scope %}({{scope}}){% endif %}: {{message}}"
schema = "<type>(<scope>): <subject>"
schema_pattern = "^(feat|fix|docs|style|refactor|perf|test|chore)(\\(\\w+\\))?:\\s.*"
bump_pattern = "^(feat|fix|perf|refactor)"
bump_map = {"feat" = "MINOR", "fix" = "PATCH", "perf" = "PATCH", "refactor" = "PATCH"}
```

```bash
# 安装
pip install commitizen

# 交互式创建提交
cz commit

# 升级版本并更新变更日志
cz bump --changelog

# 检查提交
cz check --rev-range HEAD~5..HEAD
```

## 发布说明模板

### GitHub 发布模板

```markdown
## What's Changed

### 🚀 Features

{{ range .Features }}

- {{ .Title }} by @{{ .Author }} in #{{ .PR }}
  {{ end }}

### 🐛 Bug Fixes

{{ range .Fixes }}

- {{ .Title }} by @{{ .Author }} in #{{ .PR }}
  {{ end }}

### 📚 Documentation

{{ range .Docs }}

- {{ .Title }} by @{{ .Author }} in #{{ .PR }}
  {{ end }}

### 🔧 Maintenance

{{ range .Chores }}

- {{ .Title }} by @{{ .Author }} in #{{ .PR }}
  {{ end }}

## New Contributors

{{ range .NewContributors }}

- @{{ .Username }} made their first contribution in #{{ .PR }}
  {{ end }}

**Full Changelog**: https://github.com/owner/repo/compare/v{{ .Previous }}...v{{ .Current }}
```

### 内部发布说明

```markdown
# Release v2.1.0 - January 15, 2024

## 摘要

此版本引入了暗黑模式支持，并将结账性能提升了 40%。还包括重要的安全更新。

## 亮点

### 🌙 暗黑模式

用户现在可以从设置中切换到暗黑模式。偏好设置会自动保存并在设备间同步。

### ⚡ 性能

- 结账流程快 40%
- 包体积减少 15%

## 破坏性变更

此版本无破坏性变更。

## 升级指南

无需特殊步骤。标准部署流程适用。

## 已知问题

- 暗黑模式在初始加载时可能闪烁（修复计划在 v2.1.1）

## 依赖更新

| 包 | 从 | 到 | 原因 |
|----|----|----|------|
| react | 18.2.0 | 18.3.0 | 性能改进 |
| lodash | 4.17.20 | 4.17.21 | 安全补丁 |
```

## 提交消息示例

```bash
# 带范围的功能
feat(auth): add OAuth2 support for Google login

# 带 issue 引用的 bug 修复
fix(checkout): resolve race condition in payment processing

Closes #123

# 破坏性变更
feat(api)!: change user endpoint response format

BREAKING CHANGE: The user endpoint now returns `userId` instead of `id`.
Migration guide: Update all API consumers to use the new field name.

# 多段落
fix(database): handle connection timeouts gracefully

Previously, connection timeouts would cause the entire request to fail
without retry. This change implements exponential backoff with up to
3 retries before failing.

The timeout threshold has been increased from 5s to 10s based on p99
latency analysis.

Fixes #456
Reviewed-by: @alice
```

## 最佳实践

### 应该做的

- **遵循约定式提交** — 启用自动化
- **写清晰的消息** — 未来的你会感谢你
- **引用 issue** — 将提交关联到工单
- **一致使用范围** — 定义团队规范
- **自动化发布** — 减少手动错误

### 不应该做的

- **不要混合变更** — 每次提交一个逻辑变更
- **不要跳过验证** — 使用 commitlint
- **不要手动编辑** — 仅使用生成的变更日志
- **不要忘记破坏性变更** — 用 `!` 或 footer 标记
- **不要忽略 CI** — 在管道中验证提交
