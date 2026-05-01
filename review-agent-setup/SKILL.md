---
name: review-agent-setup
description: 在 Claude Code 中为 AI 代理审查操作配置人工审批门控。当设置一个代理可能发布 PR 审查、评论、合并或编辑 CI 配置的项目时使用，并且您需要具有密码学可审计审批跟踪和 Cedar 强制执行的门控。
---

# review-agent-governance — 设置

将 AI 代理审查操作（PR 审查、评论、合并、CI 编辑）置于显式人工审批之后。每次尝试（无论批准还是拒绝）都会产生一个 Ed25519 签名的收据。

## 何时使用此插件

在以下项目的 Claude Code 代理中安装：

- 审查、评论或合并拉取请求（`gh pr review`、`gh pr merge`）
- 分诊问题（`gh issue comment`、`gh issue close`）
- 发布版本（`gh release create`）
- 修改 CI 配置（`.github/workflows/`、`.gitlab-ci.yml`）
- 推送到受保护分支（`main`、`master`、`release`、`production`）
- 发布到外部通知渠道（Slack webhooks、Discord）

如果代理仅执行本地文件编辑和运行测试，则此插件过于繁琐。使用 `protect-mcp` 进行通用工具调用策略执行，跳过此插件。

## 一次性设置

### 1. 安装插件

```bash
claude plugin install wshobson/agents/review-agent-governance
```

### 2. 将默认策略复制到您的项目

```bash
cp .claude/plugins/review-agent-governance/policies/review-agent-governance.cedar \
   ./review-governance.cedar
```

您可以编辑此文件以匹配项目的特定规则。参见 `../agents/review-policy-author.md` 获取审查策略编写指南。

### 3. 创建收据目录和签名密钥

```bash
mkdir -p ./review-receipts
echo "./review-receipts/" >> .gitignore
echo "./review-governance.key" >> .gitignore
echo "./.review-approved" >> .gitignore
```

首次调用 `protect-mcp sign` 将创建密钥。提交第一个收据中的公钥，以便审计人员稍后验证。

## 每会话工作流

Cedar 策略无条件拒绝审查表面操作。要批准特定操作，请在其之前打开批准窗口并在其之后关闭。

### 标志文件（最简单）

```bash
# 在您要批准的操作之前
touch ./.review-approved

# 让 Claude Code 运行审查/评论/合并

# 之后立即执行
rm ./.review-approved
```

### 斜杠命令（在 Claude Code 内）

```
/approve-review "Reviewing PR #123 authored by contributor X"
```

这将创建 `./.review-approved`，并将给定原因作为注释嵌入，同时向链中写入一个人工批准的收据。仍需要后续的 `rm` 来关闭窗口。

### 试运行一切（强制完整策略评估）

如果您希望每个工具调用都通过 Cedar 而不进行批准绕过：

```bash
export REVIEW_APPROVAL_FLAG=./.never-approve
```

任何匹配禁止规则的工具调用都将被拒绝；批准窗口无效。适用于 CI 或锁定的审计运行。

## 验证链

列出所有收据：

```bash
ls -la ./review-receipts/
```

离线验证整个链：

```bash
npx @veritasacta/verify ./review-receipts/*.json
```

退出码 0 表示每个收据都是真实的且链完整。退出码 1 表示某个收据被篡改。退出码 2 表示收据格式错误。

查看最近的拒绝：

```
/list-pending
```

在 Claude Code 中，此斜杠命令遍历收据链并打印任何最近的 `decision: deny` 条目，包括工具名称、命令模式和时间戳。

## 示例：批准 PR 审查

```bash
# 1. 人工审查代理提出的评论
$ /list-pending
  Recent denials:
  - 2026-04-17T14:23:01Z  Bash "gh pr review 42 --approve --body 'LGTM'"
  - 2026-04-17T14:23:02Z  Bash "gh pr comment 42 --body 'Looking good'"

# 2. 人工决定第一个是合适的，批准它
$ /approve-review "Approving LGTM on PR 42 after visual inspection"
  ./.review-approved created

# 3. 代理重试操作；这次成功了
$ agent: gh pr review 42 --approve --body "LGTM"
  [receipt: rec_XXX, decision=allow, reason=human_approved]

# 4. 人工关闭窗口
$ rm ./.review-approved
```

每一步都在收据链中。该链可供监管机构、交易对手或下游审计人员离线验证，以确认没有审查操作绕过人工门控。

## 与 protect-mcp 组合使用

如果两个插件都已安装，请并行运行它们：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "npx protect-mcp@0.5.5 evaluate --policy ./protect.cedar --tool \"$TOOL_NAME\" --input \"$TOOL_INPUT\" --fail-on-missing-policy false"
          }
        ]
      },
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "if [ -f ./.review-approved ]; then exit 0; fi; npx protect-mcp@0.5.5 evaluate --policy ./review-governance.cedar --tool \"$TOOL_NAME\" --input \"$TOOL_INPUT\" --fail-on-missing-policy false"
          }
        ]
      }
    ]
  }
}
```

两个钩子都必须通过才能继续执行工具调用。任一策略中的 Cedar 拒绝都会阻止它。

## 标准

- **Ed25519** — RFC 8032（数字签名）
- **JCS** — RFC 8785（确定性 JSON 规范化）
- **Cedar** — AWS 的开放授权策略语言
- **IETF 草案** — [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)
