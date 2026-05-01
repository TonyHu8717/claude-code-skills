---
name: protect-mcp-setup
description: 为 Claude Code 工具调用配置 Cedar 策略执行和 Ed25519 签名收据。在设置需要加密审计跟踪、策略门控工具执行或合规就绪的代理操作证据的项目时使用。
---

# protect-mcp — 策略执行 + 签名收据

每个 Claude Code 工具调用的加密治理。每次调用都根据 Cedar 策略进行评估，并产生一个任何人都可以离线验证的 Ed25519 签名收据。

## 概述

Claude Code 运行强大的工具：`Bash`、`Edit`、`Write`、`WebFetch`。默认情况下没有审计跟踪，没有策略执行，也无法事后证明决策。`protect-mcp` 弥补了这三个缺口：

- **Cedar 策略**（AWS 的开放授权引擎）在执行前评估每个工具调用。Cedar 拒绝是权威性的。
- **Ed25519 收据**记录每个决策及其输入、治理策略和结果。收据是哈希链式的。
- **离线验证**通过 `npx @veritasacta/verify`。无需服务器、无需账户、无需信任操作者。

## 问题

AI 代理做出影响金钱、安全和权利的决策。Claude Code 会话日志记录了发生的事情，但日志是：

- 可变的 — 任何有访问权限的人都可以编辑
- 未签名的 — 无法证明完整性
- 绑定操作者 — 验证需要信任持有日志的人

对于合规环境（金融、医疗、受监管研究），这不够。你需要防篡改的证据，可以由第三方验证而无需信任你。

## 解决方案

将 `protect-mcp` 添加到你的 Claude Code 项目：

```bash
# 1. Install the plugin (adds hooks + skill to your project)
claude plugin install wshobson/agents/protect-mcp

# 2. Configure hooks in .claude/settings.json (see below)

# 3. Start the receipt-signing server (runs locally, no external calls)
npx protect-mcp@latest serve --enforce

# 4. Use Claude Code normally. Every tool call is now policy-evaluated
#    and produces a signed receipt in ./receipts/
```

## Hook 配置

将以下内容添加到项目的 `.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hook": {
          "type": "command",
          "command": "npx protect-mcp@latest evaluate --policy ./protect.cedar --tool \"$TOOL_NAME\" --input \"$TOOL_INPUT\" || exit 2"
        }
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hook": {
          "type": "command",
          "command": "npx protect-mcp@latest sign --tool \"$TOOL_NAME\" --input \"$TOOL_INPUT\" --output \"$TOOL_OUTPUT\" --receipts ./receipts/"
        }
      }
    ]
  }
}
```

### 每个 hook 的作用

**PreToolUse** — 在工具执行之前运行。根据你的 Cedar 策略文件评估工具调用。如果 Cedar 返回 `deny`，hook 以代码 2 退出，Claude Code 完全阻止工具调用。

**PostToolUse** — 在工具完成后运行。签名一个包含工具名称、输入哈希、输出哈希、决策、策略摘要和时间戳的收据。将收据写入 `./receipts/<timestamp>.json`。

## Cedar 策略文件

在项目根目录创建 `./protect.cedar`：

```cedar
// Allow read-only tools by default
permit (
    principal,
    action in [Action::"Read", Action::"Glob", Action::"Grep", Action::"WebFetch"],
    resource
);

// Require explicit allow for destructive tools
permit (
    principal,
    action == Action::"Bash",
    resource
) when {
    // Allow safe commands only
    context.command_pattern in ["git", "npm", "ls", "cat", "echo", "pwd", "test"]
};

// Never allow recursive deletion
forbid (
    principal,
    action == Action::"Bash",
    resource
) when {
    context.command_pattern == "rm -rf"
};

// Require confirmation for writes outside the project
forbid (
    principal,
    action in [Action::"Edit", Action::"Write"],
    resource
) when {
    context.path_starts_with != "."
};
```

## 验证

验证单个收据：

```bash
npx @veritasacta/verify receipts/2026-04-15T10-30-00Z.json
# Exit 0 = valid
# Exit 1 = tampered
# Exit 2 = malformed
```

验证整个链：

```bash
npx @veritasacta/verify receipts/*.json
```

在 Claude Code 中使用插件的斜杠命令：

```
/verify-receipt receipts/latest.json
/audit-chain ./receipts/ --last 20
```

## 收据格式

每个收据是具有此结构的 JSON 文件：

```json
{
  "receipt_id": "rec_8f92a3b1",
  "receipt_version": "1.0",
  "issuer_id": "claude-code-protect-mcp",
  "event_time": "2026-04-15T10:30:00.000Z",
  "tool_name": "Bash",
  "input_hash": "sha256:a3f8...",
  "decision": "allow",
  "policy_id": "autoresearch-safe",
  "policy_digest": "sha256:b7e2...",
  "parent_receipt_id": "rec_3d1ab7c2",
  "public_key": "4437ca56815c0516...",
  "signature": "4cde814b7889e987..."
}
```

- **Ed25519** 签名（RFC 8032）
- **JCS 规范化**（RFC 8785）签名前
- **哈希链式** 通过 `parent_receipt_id` 链接到前一个收据
- **离线可验证** — 无需网络调用、无需供应商查找

## 为什么这很重要

| 之前 | 之后 |
|--------|-------|
| 「相信我，代理只读取了文件」 | 加密可证明：每个 Read 都被记录和签名 |
| 「日志显示它发生了」 | 收据证明它发生了，没有人可以编辑 |
| 「你必须审计我们的系统」 | 任何人都可以离线验证每个收据 |
| 「日志现在可能不同了」 | Ed25519 签名在签名时锁定记录 |

## 标准

- **Ed25519** — RFC 8032（数字签名）
- **JCS** — RFC 8785（确定性 JSON 规范化）
- **Cedar** — AWS 的开放授权策略语言
- **IETF 草案** — [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)

## 相关

- **npm**: [protect-mcp](https://www.npmjs.com/package/protect-mcp) (v0.5.5, 10K+ 月下载量)
- **验证 CLI**: [@veritasacta/verify](https://www.npmjs.com/package/@veritasacta/verify)
- **源码**: [github.com/ScopeBlind/scopeblind-gateway](https://github.com/ScopeBlind/scopeblind-gateway)
- **协议**: [veritasacta.com](https://veritasacta.com)
- **集成**: Microsoft Agent Governance Toolkit (PR #667), AWS cedar-policy/cedar-for-agents (PR #64)
