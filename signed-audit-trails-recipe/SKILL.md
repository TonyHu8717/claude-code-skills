---
name: signed-audit-trails-recipe
description: 为 Claude Code 工具调用设置加密签名审计跟踪的分步指南。在解释、评估或演示该模式（在承诺使用 protect-mcp 运行时钩子之前）时使用。涵盖 Cedar 策略、Ed25519 收据、离线验证、篡改检测、CI/CD 集成和 SLSA 组合。
---

# Claude Code 工具调用的签名审计跟踪

为每个 Claude Code 工具调用提供加密签名收据的指南式演练。这是教学技能。如需运行时实现，请安装 [`protect-mcp`](../../protect-mcp/) 插件。

## 您将获得什么

每个工具调用（`Bash`、`Edit`、`Write`、`WebFetch`）都会：

1. **执行前根据 Cedar 策略进行评估**。如果策略拒绝调用，工具不会运行。
2. **执行后作为 Ed25519 收据签名**。收据是 JCS 规范化的、哈希链式的，并且可以由任何拥有公钥的人离线验证。

审计员、监管机构或交易对手可以稍后使用单个 CLI 命令（`npx @veritasacta/verify receipts/*.json`）验证整个链条。无需网络调用、无需供应商查询、无需信任操作员。

## 何时使用此模式

- **受监管环境**（金融、医疗保健、关键基础设施），需要代理行为的防篡改证据
- **CI/CD 管道**，需要证明策略网关对每个自动化构建步骤都有效
- **多方协作**，交易对手希望在不信任您的操作员的情况下验证您的代理行为
- **合规上下文**（欧盟人工智能法案第 12 条、代理构建软件的 SLSA 来源），标准日志记录不足

## 步骤 1：安装钩子配置

在项目根目录创建 `.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hook": {
          "type": "command",
          "command": "npx protect-mcp@latest evaluate --policy ./protect.cedar --tool \"$TOOL_NAME\" --input \"$TOOL_INPUT\" --fail-on-missing-policy false"
        }
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hook": {
          "type": "command",
          "command": "npx protect-mcp@latest sign --tool \"$TOOL_NAME\" --input \"$TOOL_INPUT\" --output \"$TOOL_OUTPUT\" --receipts ./receipts/ --key ./protect-mcp.key"
        }
      }
    ]
  }
}
```

`protect-mcp sign` 的首次运行会生成 `./protect-mcp.key`（Ed25519 私钥）（如果尚不存在）。提交**公钥**指纹（可在任何收据的 `public_key` 字段中查看）；不要提交私钥。

将私钥和收据目录添加到 `.gitignore`：

```bash
echo "./protect-mcp.key" >> .gitignore
echo "./receipts/" >> .gitignore
```

## 步骤 2：编写 Cedar 策略

创建 `./protect.cedar`：

```cedar
// 默认允许所有面向读取的工具。
permit (
    principal,
    action in [Action::"Read", Action::"Glob", Action::"Grep", Action::"WebSearch"],
    resource
);

// 仅允许来自安全列表的 Bash 命令。
permit (
    principal,
    action == Action::"Bash",
    resource
) when {
    context.command_pattern in [
        "git", "npm", "pnpm", "yarn", "ls", "cat", "pwd",
        "echo", "test", "node", "python", "make"
    ]
};

// 明确拒绝破坏性命令。Cedar deny 具有权威性。
forbid (
    principal,
    action == Action::"Bash",
    resource
) when {
    context.command_pattern in ["rm -rf", "dd", "mkfs", "shred"]
};

// 限制写入到项目目录。
permit (
    principal,
    action in [Action::"Write", Action::"Edit"],
    resource
) when {
    context.path_starts_with == "./"
};
```

四条规则：

- 面向读取的工具始终允许
- `Bash` 允许安全命令模式（`git`、`npm` 等）
- `Bash rm -rf` 和类似破坏性命令被明确拒绝
- 写入仅允许在项目内（`./` 前缀）

Cedar `forbid` 规则优先于 `permit` 规则，因此破坏性命令无法被后续的许可规则绕过。

## 步骤 3：正常使用 Claude Code

启动 Claude Code。每个工具调用都经过两个钩子：

```
您：请读取 README 并总结它。

Claude：我将读取 README.md。
  [PreToolUse: Read ./README.md -> allow]
  [Tool: Read executes]
  [PostToolUse: receipt rcpt-a8f3c9d2 signed to ./receipts/]

... README 的总结 ...
```

一个包含 20 个工具调用的会话产生 20 个收据，每个都哈希链接到其前一个。

## 步骤 4：检查收据

```bash
cat ./receipts/$(ls -t ./receipts/ | head -1)
```

```json
{
  "receipt_id": "rcpt-a8f3c9d2",
  "receipt_version": "1.0",
  "issuer_id": "claude-code-protect-mcp",
  "event_time": "2026-04-17T12:34:56.123Z",
  "tool_name": "Read",
  "input_hash": "sha256:a3f8c9d2e1b7465f...",
  "decision": "allow",
  "policy_id": "protect.cedar",
  "policy_digest": "sha256:b7e2f4a6c8d0e1f3...",
  "parent_receipt_id": "rcpt-3d1ab7c2",
  "public_key": "4437ca56815c0516...",
  "signature": "4cde814b7889e987..."
}
```

除 `signature` 和 `public_key` 外的每个字段都被 Ed25519 签名覆盖。签名后修改任何字段都会使签名失效。

## 步骤 5：验证收据链

```bash
npx @veritasacta/verify ./receipts/*.json
```

退出代码：

| 代码 | 含义 |
|------|------|
| `0`  | 所有收据已验证；链条完整 |
| `1`  | 收据签名验证失败（被篡改或密钥错误） |
| `2`  | 收据格式错误 |

## 步骤 6：演示篡改检测

修改任何收据的 `decision` 字段从 `allow` 到 `deny`：

```bash
python3 -c "
import json, os
path = './receipts/' + sorted(os.listdir('./receipts'))[-1]
r = json.loads(open(path).read())
r['decision'] = 'deny'
open(path, 'w').write(json.dumps(r))
"

npx @veritasacta/verify ./receipts/*.json
```

验证器以代码 `1` 退出并报告哪个收据失败。Ed25519 签名不再与被篡改载荷的 JCS 规范字节匹配。

恢复字段后验证再次通过。

## 加密工作原理

三个不变量使收据可以在任何一致实现之间离线验证：

1. **JCS 规范化（RFC 8785）**在签名之前。键排序、空白最小化、字符串 NFC 规范化。两个独立实现为相同收据内容产生字节相同的签名载荷。
2. **Ed25519 签名（RFC 8032）**覆盖规范字节。确定性、固定大小、无随机数依赖。
3. **哈希链链接。**每个收据的 `parent_receipt_hash` 是前一个收据规范形式的 SHA-256。插入、删除和重新排序会破坏后续收据。

有关正式线路格式，请参阅
[draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)。

## 跨实现互操作

收据格式目前有四个独立实现：

| 实现 | 语言 | 用例 |
|------|------|------|
| [protect-mcp](https://www.npmjs.com/package/protect-mcp) | TypeScript | Claude Code、Cursor、MCP 主机 |
| [protect-mcp-adk](https://pypi.org/project/protect-mcp-adk/) | Python | Google Agent Development Kit |
| [sb-runtime](https://github.com/ScopeBlind/sb-runtime) | Rust | OS 级沙箱（Landlock + seccomp） |
| APS 治理钩子 | Python | CrewAI、LangChain |

其中任何一个产生的收据都可以通过
[`@veritasacta/verify`](https://www.npmjs.com/package/@veritasacta/verify) 验证。
审计员不需要信任操作员的工具选择：格式就是契约。

## CI/CD 集成

在收据链验证上网关合并，使没有构建能带着损坏的证据链落地：

```yaml
# .github/workflows/verify-receipts.yml
name: Verify Decision Receipts
on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - name: Run governed agent
        run: python scripts/run_agent.py > receipts.jsonl
      - name: Verify receipt chain
        run: npx @veritasacta/verify receipts.jsonl
```

将收据归档为工件，使链条在作业运行后得以保留：

```yaml
      - name: Upload receipts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: decision-receipts
          path: receipts/
```

## 与 SLSA 来源的组合（代理构建软件）

当 Claude Code 构建和发布软件（运行 `npm install`、`npm build`、`npm publish` 作为工具调用）时，收据链是逐步构建日志。SLSA Provenance v1 有一个扩展点：`byproducts` 字段可以在构建证明旁边引用收据链。

[agent-commit build type](https://refs.arewm.com/agent-commit/v0.2)
使用 ResourceDescriptor 形状记录了该模式：

```json
{
  "name": "decision-receipts",
  "digest": { "sha256": "..." },
  "uri": "oci://registry/org/build-xyz/receipts:sha256-...",
  "annotations": {
    "predicateType": "https://veritasacta.com/attestation/decision-receipt/v0.1",
    "signerRole": "supervisor-hook"
  }
}
```

SLSA 来源由构建者身份签名；收据证明由 supervisor-hook 身份签名。两个信任域，在副产品层交叉引用。参见
[slsa-framework/slsa#1594](https://github.com/slsa-framework/slsa/issues/1594)
了解组合讨论。

## 常见陷阱

**版本控制中的私钥。**生成的 `./protect-mcp.key` 不得提交。上面的示例将其添加到 `.gitignore`。如果密钥被意外提交，请立即轮换（删除密钥文件并让钩子在下次运行时重新生成）。

**钩子命令引号。**钩子接收 `$TOOL_NAME` 和 `$TOOL_INPUT` 作为环境变量。保持引号为 `"$TOOL_INPUT"`，以便带有空格或特殊字符的输入能完整传递。

**CI 中的收据目录。**如果 Claude Code 在 CI 中运行，在作业结束时将收据作为工件上传，否则链条在作业结束时丢失。

**策略缺失。**示例 `PreToolUse` 钩子使用 `--fail-on-missing-policy false`，因此缺失的 `./protect.cedar` 不会破坏开箱即用的 Claude Code。在生产环境中移除此标志，使缺失的策略被视为硬故障。

## 本市场中的相关项

- [`protect-mcp`](../../protect-mcp/) — 运行时钩子实现（在生产中使用此插件）
- [`review-agent-governance`](../../review-agent-governance/) — 在审查表面操作前要求人工批准；与 protect-mcp 组合使用

## 参考资料

- [`draft-farley-acta-signed-receipts`](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/) — IETF 草案，收据线路格式
- [RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032) — Ed25519
- [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785) — JCS
- [Cedar 策略语言](https://docs.cedarpolicy.com/)
- [protect-mcp on npm](https://www.npmjs.com/package/protect-mcp)
- [@veritasacta/verify on npm](https://www.npmjs.com/package/@veritasacta/verify)
- [in-toto/attestation#549](https://github.com/in-toto/attestation/pull/549) — Decision Receipt 谓词提案
- [agent-commit build type](https://refs.arewm.com/agent-commit/v0.2) — 代理产生提交的 SLSA 来源
- [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) (`examples/protect-mcp-governed/`)
- [AWS Cedar for Agents](https://github.com/cedar-policy/cedar-for-agents)
