---
name: project-session-manager
description: 以工作树为先的开发环境管理器，用于 issues、PRs 和功能，可选 tmux 会话
aliases: [psm]
level: 2
---

# 项目会话管理器（PSM）技能

`psm` 是此规范技能入口的兼容性别名。

> **快速开始（以工作树为先）：** 从 `omc teleport` 开始，当你想要一个隔离的 issue/PR/feature 工作树时：
> ```bash
> omc teleport #123          # 为 issue/PR 创建工作树
> omc teleport my-feature    # 为功能创建工作树
> omc teleport list          # 列出工作树
> ```
> 详情参见下方[Teleport 命令](#teleport-命令)。

使用 git 工作树和 tmux 会话通过 Claude Code 自动化隔离的开发环境。支持跨多个任务、项目和仓库的并行工作。

规范斜杠命令：`/oh-my-claudecode:project-session-manager`（别名：`/oh-my-claudecode:psm`）。

## 命令

| 命令 | 描述 | 示例 |
|---------|-------------|---------|
| `review <ref>` | PR 审查会话 | `/psm review omc#123` |
| `fix <ref>` | Issue 修复会话 | `/psm fix omc#42` |
| `feature <proj> <name>` | 功能开发 | `/psm feature omc add-webhooks` |
| `list [project]` | 列出活动会话 | `/psm list` |
| `attach <session>` | 附加到会话 | `/psm attach omc:pr-123` |
| `kill <session>` | 终止会话 | `/psm kill omc:pr-123` |
| `cleanup` | 清理已合并/关闭的 | `/psm cleanup` |
| `status` | 当前会话信息 | `/psm status` |

## 项目引用

支持的格式：
- **别名**：`omc#123`（需要 `~/.psm/projects.json`）
- **完整**：`owner/repo#123`
- **URL**：`https://github.com/owner/repo/pull/123`
- **当前**：`#123`（使用当前目录的仓库）

## 配置

### 项目别名（`~/.psm/projects.json`）

```json
{
  "aliases": {
    "omc": {
      "repo": "Yeachan-Heo/oh-my-claudecode",
      "local": "~/Workspace/oh-my-claudecode",
      "default_base": "main"
    }
  },
  "defaults": {
    "worktree_root": "~/.psm/worktrees",
    "cleanup_after_days": 14
  }
}
```

## 提供者

PSM 支持多个 issue 跟踪提供者：

| 提供者 | 需要 CLI | 引用格式 | 命令 |
|----------|--------------|-------------------|----------|
| GitHub（默认） | `gh` | `owner/repo#123`、`alias#123`、GitHub URLs | review、fix、feature |
| Jira | `jira` | `PROJ-123`（如 PROJ 已配置）、`alias#123` | fix、feature |

### Jira 配置

要使用 Jira，添加带有 `jira_project` 和 `provider: "jira"` 的别名：

```json
{
  "aliases": {
    "mywork": {
      "jira_project": "MYPROJ",
      "repo": "mycompany/my-project",
      "local": "~/Workspace/my-project",
      "default_base": "develop",
      "provider": "jira"
    }
  }
}
```

**重要：** `repo` 字段仍然需要用于克隆 git 仓库。Jira 跟踪 issues，但你在 git 仓库中工作。

对于非 GitHub 仓库，使用 `clone_url` 代替：
```json
{
  "aliases": {
    "private": {
      "jira_project": "PRIV",
      "clone_url": "git@gitlab.internal:team/repo.git",
      "local": "~/Workspace/repo",
      "provider": "jira"
    }
  }
}
```

### Jira 引用检测

PSM 仅在 `PROJ` 在你的别名中明确配置为 `jira_project` 时才将 `PROJ-123` 格式识别为 Jira。这防止了来自分支名如 `FIX-123` 的误报。

### Jira 示例

```bash
# 修复 Jira issue（MYPROJ 必须已配置）
psm fix MYPROJ-123

# 使用别名修复（推荐）
psm fix mywork#123

# 功能开发（与 GitHub 相同）
psm feature mywork add-webhooks

# 注意：Jira 不支持 'psm review'（无 PR 概念）
# 对 Jira issues 使用 'psm fix'
```

### Jira CLI 设置

安装 Jira CLI：
```bash
# macOS
brew install ankitpokhrel/jira-cli/jira-cli

# Linux
# 参见：https://github.com/ankitpokhrel/jira-cli#installation

# 配置（交互式）
jira init
```

Jira CLI 与 PSM 分开处理认证。

## 目录结构

```
~/.psm/
├── projects.json       # 项目别名
├── sessions.json       # 活动会话注册表
└── worktrees/          # 工作树存储
    └── <project>/
        └── <type>-<id>/
```

## 会话命名

| 类型 | Tmux 会话 | 工作树目录 |
|------|--------------|--------------|
| PR 审查 | `psm:omc:pr-123` | `~/.psm/worktrees/omc/pr-123` |
| Issue 修复 | `psm:omc:issue-42` | `~/.psm/worktrees/omc/issue-42` |
| 功能 | `psm:omc:feat-auth` | `~/.psm/worktrees/omc/feat-auth` |

---

## 实现协议

当用户调用 PSM 命令时，遵循此协议：

### 解析参数

解析 `{{ARGUMENTS}}` 以确定：
1. **子命令**：review、fix、feature、list、attach、kill、cleanup、status
2. **引用**：project#number、URL 或会话 ID
3. **选项**：--branch、--base、--no-claude、--no-tmux 等

### 子命令：`review <ref>`

**目的**：创建 PR 审查会话

**步骤**：

1. **解析引用**：
   ```bash
   # 读取项目别名
   cat ~/.psm/projects.json 2>/dev/null || echo '{"aliases":{}}'

   # 解析 ref 格式：alias#num、owner/repo#num 或 URL
   # 提取：project_alias、repo (owner/repo)、pr_number、local_path
   ```

2. **获取 PR 信息**：
   ```bash
   gh pr view <pr_number> --repo <repo> --json number,title,author,headRefName,baseRefName,body,files,url
   ```

3. **确保本地仓库存在**：
   ```bash
   # 如果本地路径不存在，克隆
   if [[ ! -d "$local_path" ]]; then
     git clone "https://github.com/$repo.git" "$local_path"
   fi
   ```

4. **创建工作树**：
   ```bash
   worktree_path="$HOME/.psm/worktrees/$project_alias/pr-$pr_number"

   # 获取 PR 分支
   cd "$local_path"
   git fetch origin "pull/$pr_number/head:pr-$pr_number-review"

   # 创建工作树
   git worktree add "$worktree_path" "pr-$pr_number-review"
   ```

5. **创建会话元数据**：
   ```bash
   cat > "$worktree_path/.psm-session.json" << EOF
   {
     "id": "$project_alias:pr-$pr_number",
     "type": "review",
     "project": "$project_alias",
     "ref": "pr-$pr_number",
     "branch": "<head_branch>",
     "base": "<base_branch>",
     "created_at": "$(date -Iseconds)",
     "tmux_session": "psm:$project_alias:pr-$pr_number",
     "worktree_path": "$worktree_path",
     "source_repo": "$local_path",
     "github": {
       "pr_number": $pr_number,
       "pr_title": "<title>",
       "pr_author": "<author>",
       "pr_url": "<url>"
     },
     "state": "active"
   }
   EOF
   ```

6. **更新会话注册表**：
   ```bash
   # 添加到 ~/.psm/sessions.json
   ```

7. **创建 tmux 会话**：
   ```bash
   tmux new-session -d -s "psm:$project_alias:pr-$pr_number" -c "$worktree_path"
   ```

8. **启动 Claude Code**（除非 --no-claude）：
   ```bash
   # --dangerously-skip-permissions 防止"你信任这个目录吗？"提示
   # 和重复的工具批准提示导致会话停滞（issue #2508）。
   tmux send-keys -t "psm:$project_alias:pr-$pr_number" "claude --dangerously-skip-permissions" Enter

   # claude 启动后（PSM_CLAUDE_STARTUP_DELAY，默认 5s），传递任务。
   # 使用 -l（字面量）使特殊字符不会被 tmux 误解。
   sleep "${PSM_CLAUDE_STARTUP_DELAY:-5}"
   tmux send-keys -t "psm:$project_alias:pr-$pr_number" -l \
     "Review PR #$pr_number: \"$pr_title\" by @$pr_author ($head_branch → $base_branch). URL: $pr_url." Enter
   ```

9. **输出会话信息**：
   ```
   Session ready!

     ID: omc:pr-123
     Worktree: ~/.psm/worktrees/omc/pr-123
     Tmux: psm:omc:pr-123

   To attach: tmux attach -t psm:omc:pr-123
   ```

### 子命令：`fix <ref>`

**目的**：创建 issue 修复会话

**步骤**：

1. **解析引用**（同 review）

2. **获取 issue 信息**：
   ```bash
   gh issue view <issue_number> --repo <repo> --json number,title,body,labels,url
   ```

3. **创建功能分支**：
   ```bash
   cd "$local_path"
   git fetch origin master
   branch_name="fix/$issue_number-$(echo "$title" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | head -c 30)"
   git checkout -b "$branch_name" origin/master
   ```

4. **创建工作树**：
   ```bash
   worktree_path="$HOME/.psm/worktrees/$project_alias/issue-$issue_number"
   git worktree add "$worktree_path" "$branch_name"
   ```

5. **创建会话元数据**（类似 review，type="fix"）

6. **更新注册表、创建 tmux、启动 claude**：
   同 review，但将 issue 上下文作为初始任务提示传递：
   ```bash
   tmux send-keys -t "psm:$project_alias:issue-$issue_number" "claude --dangerously-skip-permissions" Enter
   # claude 启动后，传递任务（参见 PSM_CLAUDE_STARTUP_DELAY）：
   tmux send-keys -t "psm:$project_alias:issue-$issue_number" -l \
     "Fix issue #$issue_number: \"$issue_title\". URL: $issue_url. Branch: $branch_name." Enter
   ```

### 子命令：`feature <project> <name>`

**目的**：开始功能开发

**步骤**：

1. **解析项目**（从别名或路径）

2. **创建功能分支**：
   ```bash
   cd "$local_path"
   git fetch origin master
   branch_name="feature/$feature_name"
   git checkout -b "$branch_name" origin/master
   ```

3. **创建工作树**：
   ```bash
   worktree_path="$HOME/.psm/worktrees/$project_alias/feat-$feature_name"
   git worktree add "$worktree_path" "$branch_name"
   ```

4. **创建会话、tmux、启动 claude**，将功能上下文作为初始提示：
   ```bash
   tmux send-keys -t "psm:$project_alias:feat-$feature_name" "claude --dangerously-skip-permissions" Enter
   tmux send-keys -t "psm:$project_alias:feat-$feature_name" -l \
     "Implement feature \"$feature_name\" for project $project. Branch: $branch_name." Enter
   ```

### 子命令：`list [project]`

**目的**：列出活动会话

**步骤**：

1. **读取会话注册表**：
   ```bash
   cat ~/.psm/sessions.json 2>/dev/null || echo '{"sessions":{}}'
   ```

2. **检查 tmux 会话**：
   ```bash
   tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "^psm:"
   ```

3. **检查工作树**：
   ```bash
   ls -la ~/.psm/worktrees/*/ 2>/dev/null
   ```

4. **格式化输出**：
   ```
   Active PSM Sessions:

   ID                 | Type    | Status   | Worktree
   -------------------|---------|----------|---------------------------
   omc:pr-123        | review  | active   | ~/.psm/worktrees/omc/pr-123
   omc:issue-42      | fix     | detached | ~/.psm/worktrees/omc/issue-42
   ```

### 子命令：`attach <session>`

**目的**：附加到现有会话

**步骤**：

1. **解析会话 ID**：`project:type-number`

2. **验证会话存在**：
   ```bash
   tmux has-session -t "psm:$session_id" 2>/dev/null
   ```

3. **附加**：
   ```bash
   tmux attach -t "psm:$session_id"
   ```

### 子命令：`kill <session>`

**目的**：终止会话并清理

**步骤**：

1. **终止 tmux 会话**：
   ```bash
   tmux kill-session -t "psm:$session_id" 2>/dev/null
   ```

2. **移除工作树**：
   ```bash
   worktree_path=$(jq -r ".sessions[\"$session_id\"].worktree" ~/.psm/sessions.json)
   source_repo=$(jq -r ".sessions[\"$session_id\"].source_repo" ~/.psm/sessions.json)

   cd "$source_repo"
   git worktree remove "$worktree_path" --force
   ```

3. **更新注册表**：
   ```bash
   # 从 sessions.json 移除
   ```

### 子命令：`cleanup`

**目的**：清理已合并的 PRs 和已关闭的 issues

**步骤**：

1. **读取所有会话**

2. **对于每个 PR 会话，检查是否已合并**：
   ```bash
   gh pr view <pr_number> --repo <repo> --json merged,state
   ```

3. **对于每个 issue 会话，检查是否已关闭**：
   ```bash
   gh issue view <issue_number> --repo <repo> --json closed,state
   ```

4. **清理已合并/已关闭的会话**：
   - 终止 tmux 会话
   - 移除工作树
   - 更新注册表

5. **报告**：
   ```
   Cleanup complete:
     Removed: omc:pr-123 (merged)
     Removed: omc:issue-42 (closed)
     Kept: omc:feat-auth (active)
   ```

### 子命令：`status`

**目的**：显示当前会话信息

**步骤**：

1. **从 tmux 或 cwd 检测当前会话**：
   ```bash
   tmux display-message -p "#{session_name}" 2>/dev/null
   # 或检查 cwd 是否在工作树内
   ```

2. **读取会话元数据**：
   ```bash
   cat .psm-session.json 2>/dev/null
   ```

3. **显示状态**：
   ```
   Current Session: omc:pr-123
   Type: review
   PR: #123 - Add webhook support
   Branch: feature/webhooks
   Created: 2 hours ago
   ```

---

## 错误处理

| 错误 | 解决方案 |
|-------|------------|
| 工作树已存在 | 提供：附加、重建或中止 |
| PR 未找到 | 验证 URL/编号，检查权限 |
| 无 tmux | 警告并跳过会话创建 |
| 无 gh CLI | 报错并提供安装说明 |

## Teleport 命令

`omc teleport` 命令提供了一种轻量级的替代方案来替代完整的 PSM 会话。它创建 git 工作树而无需 tmux 会话管理 -- 非常适合快速隔离开发。

### 用法

```bash
# 为 issue 或 PR 创建工作树
omc teleport #123
omc teleport owner/repo#123
omc teleport https://github.com/owner/repo/issues/42

# 为功能创建工作树
omc teleport my-feature

# 列出现有工作树
omc teleport list

# 移除工作树
omc teleport remove issue/my-repo-123
omc teleport remove --force feat/my-repo-my-feature
```

### 选项

| 标志 | 描述 | 默认值 |
|------|-------------|---------|
| `--worktree` | 创建工作树（默认，保留用于兼容性） | `true` |
| `--path <path>` | 自定义工作树根目录 | `~/Workspace/omc-worktrees/` |
| `--base <branch>` | 创建所基于的基础分支 | `main` |
| `--json` | 以 JSON 输出 | `false` |

### 工作树布局

```
~/Workspace/omc-worktrees/
├── issue/
│   └── my-repo-123/        # Issue 工作树
├── pr/
│   └── my-repo-456/        # PR 审查工作树
└── feat/
    └── my-repo-my-feature/ # 功能工作树
```

### PSM vs Teleport

| 功能 | PSM | Teleport |
|---------|-----|----------|
| Git 工作树 | 是 | 是 |
| Tmux 会话 | 是 | 否 |
| Claude Code 启动 | 是 | 否 |
| 会话注册表 | 是 | 否 |
| 自动清理 | 是 | 否 |
| 项目别名 | 是 | 否（使用当前仓库） |

使用 **PSM** 获取完整托管会话。使用 **teleport** 进行快速工作树创建。

---

## 要求

必需：
- `git` - 版本控制（需要 worktree 支持 v2.5+）
- `jq` - JSON 解析
- `tmux` - 会话管理（可选，但推荐）

可选（按提供者）：
- `gh` - GitHub CLI（用于 GitHub 工作流）
- `jira` - Jira CLI（用于 Jira 工作流）

## 初始化

首次运行时，创建默认配置：

```bash
mkdir -p ~/.psm/worktrees ~/.psm/logs

# 如果不存在则创建默认 projects.json
if [[ ! -f ~/.psm/projects.json ]]; then
  cat > ~/.psm/projects.json << 'EOF'
{
  "aliases": {
    "omc": {
      "repo": "Yeachan-Heo/oh-my-claudecode",
      "local": "~/Workspace/oh-my-claudecode",
      "default_base": "main"
    }
  },
  "defaults": {
    "worktree_root": "~/.psm/worktrees",
    "cleanup_after_days": 14,
    "auto_cleanup_merged": true
  }
}
EOF
fi

# 如果不存在则创建 sessions.json
if [[ ! -f ~/.psm/sessions.json ]]; then
  echo '{"version":1,"sessions":{},"stats":{"total_created":0,"total_cleaned":0}}' > ~/.psm/sessions.json
fi
```
