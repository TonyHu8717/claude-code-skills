---
name: lark-event
version: 1.0.0
description: "飞书/Lark 实时事件监听/订阅/消费：通过 `lark-cli event consume <EventKey>` 以 NDJSON 格式流式接收事件（涵盖即时通讯消息接收、表情回复、群成员变更等）。适用于飞书机器人、实时消息处理、长期运行的订阅者、流式 webhook/push 处理器。支持 `--max-events` / `--timeout` 有界运行和 stderr 就绪标记协议——专为以子进程方式运行的 AI agent 设计。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli event --help"
---

# 飞书事件

> **前置条件：** 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md) 了解认证、`--as user/bot` 身份切换、`Permission denied` 错误处理和安全规则。

## 核心命令

| 命令 | 用途 |
|------|------|
| `lark-cli event list [--json]` | 列出所有可订阅的 EventKey |
| `lark-cli event schema <EventKey> [--json]` | 显示 EventKey 的参数和输出 schema |
| `lark-cli event consume <EventKey> [flags]` | 阻塞式消费；事件输出到 stdout NDJSON |
| `lark-cli event status [--json] [--fail-on-orphan]` | 查看本地总线守护进程状态 |
| `lark-cli event stop [--all] [--force]` | 停止总线守护进程 |


## 通用标志

| 标志 | 说明 |
|---|---|
| `--param key=value` / `-p` | 业务参数（可重复；多值用逗号分隔）。未知 key 会报错并列出有效名称 |
| `--jq <expr>` | jq 表达式，用于过滤/转换每个事件；输出为空则跳过该事件 |
| `--max-events N` | 收到 N 个事件后退出。默认 0 = 无限制 |
| `--timeout D` | 经过时长 D 后退出（如 `30s`、`2m`）。默认 0 = 无超时。`--max-events` / `--timeout` 哪个先触发就以哪个为准 |
| `--output-dir <dir>` | 将每个事件写入文件（仅限相对路径；防止路径遍历） |
| `--quiet` | 禁止 stderr 诊断输出。**AI 不应使用此选项**——它会静默掉就绪标记 |
| `--as user\|bot\|auto` | 会话身份（见 lark-shared） |


## 示例

```bash
# 默认：流式接收该 key 的所有事件（无过滤、无投影）
lark-cli event consume im.message.receive_v1 --as bot

# 获取一个样本事件以检查 payload 结构
lark-cli event consume im.message.receive_v1 --max-events 1 --timeout 30s --as bot

# 运行 10 分钟后自动退出
lark-cli event consume im.message.receive_v1 --timeout 10m --as bot

# 并发消费多个 EventKey（每个进程一个 shape，无 dispatcher）
lark-cli event consume im.message.receive_v1          --as bot > receive.ndjson &
lark-cli event consume im.message.reaction.created_v1 --as bot > reaction.ndjson &
wait

```

## 调用流程

1. `lark-cli event list --json` → 选取一个合法的 key
2. `lark-cli event schema <key> --json` → 读取 `resolved_output_schema` + `jq_root_path` 以确定字段路径
3. `lark-cli event consume <key> [--jq '<expr>']` → 消费

## 子进程协议

### 就绪标记

`event consume` 的 stderr 会输出一行固定的 `[event] ready event_key=<key>`。**父进程应在 stderr 上阻塞直到此行出现，然后再开始读取 stdout。** 不要回退到使用 `sleep`。

### stdin EOF = 优雅退出

`event consume` 将 stdin 关闭视为关闭信号（为 AI 子进程调用者设计）。`< /dev/null` / `nohup` / systemd 默认的 `StandardInput=null` 会触发立即优雅退出（stderr 输出 `reason: signal`）。要保持运行：

- 给 stdin 提供一个永不 EOF 的来源：`< <(tail -f /dev/null)`
- 或者使用有界运行：`--max-events N` / `--timeout D`

### 退出码与原因

退出时，stderr 最后一行是 `[event] exited — received N event(s) in Xs (reason: ...)`。

| 退出码 | 原因 | 触发条件 |
|---|---|---|
| 0 | `reason: limit` | 达到 `--max-events` |
| 0 | `reason: timeout` | 达到 `--timeout` |
| 0 | `reason: signal` | Ctrl+C / SIGTERM / stdin EOF |
| 非 0 | `Error: ...`（无 `exited` 行） | 启动/运行时失败（权限、网络、参数、配置） |

编排器应将 `reason: limit/timeout/signal`（全部退出码 0）视为"业务完成"，非零视为"失败"。

### 禁止 `kill -9`

**避免对 consume 进程使用 `kill -9`**：对于带有 **PreConsume 钩子** 的 EventKey（那些通过 OAPI 注册服务端订阅的），`kill -9` 会跳过 OAPI 取消订阅并泄露服务端订阅（症状：重启时提示"subscription already exists"、事件重复投递）。优先使用 SIGTERM 或关闭 stdin。

### 一次消费一个 EventKey（多 key = 多 shell）

该命令只接受一个位置参数；不支持 `k1,k2` 和通配符。监听 N 个 key 意味着 N 个子进程——这是**有意为之**的：

- 每个进程 stdout 只有一种 shape；AI 无需 dispatcher 逻辑
- 故障隔离（一个 key 失败不影响其他 key）
- 每个 key 可独立配置 `--as` / `--jq` / `--max-events` / `--timeout`

所有 N 个消费者共享一个总线守护进程（UDS 本地 IPC），因此开销很小

## 通过 schema 编写 jq

`event schema <key> --json` 是编写 `--jq` 的权威来源。需要关注四个方面：

**(1) 字段起始位置** — 查看 `jq_root_path`

- 值为 `"."` → 字段在顶层，写 `.chat_id`
- 值为 `".event"` → 字段在 V2 信封内，写 `.event.chat_id`

**(2) 字段列表和类型** — 查看 `resolved_output_schema.properties.<name>`

每个字段携带 `type` / `description`，部分还有 `format`。片段（来自 `event schema im.message.receive_v1 --json`）：

```json
{
  "chat_id":     {"type":"string", "format":"chat_id",      "description":"Chat ID, prefixed with oc_"},
  "sender_id":   {"type":"string", "format":"open_id",      "description":"Sender open_id, prefixed with ou_"},
  "create_time": {"type":"string", "format":"timestamp_ms", "description":"Send time as ms-epoch string"}
}
```

**(3) 字段语义** — 查看 `format` 标签

飞书自定义的语义标签（**不是** JSON Schema 标准的 `format`）。常见值：`open_id` / `chat_id` / `message_id` / `timestamp_ms` / `email`。用途：区分"相同字符串类型、不同含义"的字段，以便通过 API 反查或转换格式。

**(4) 解码状态** — 读取字段的 `description`

`event consume` 运行的 Process 钩子可能预先解码了部分 payload 字段（展平 V2 信封、将 `.content` 渲染为纯文本等）——行为与原始 OAPI 不同。**编写 jq 前务必读取字段的 `description`**，特别是 `content` / `data` / `body` / `payload` 等通用字段名。

**为什么重要**：对已解码的文本字段盲目应用 `fromjson` 会导致 jq 在每个事件上报错并静默丢弃——消费者看起来在运行但不输出任何内容，只在 stderr 上有一行 `WARN`。（这是一般行为：任何 jq 运行时错误都会跳过该事件并输出一行 WARN；循环不会中止。）

**不要跳过 schema**：用 jq 投影 `event schema --json` 时，不要从 `properties` 中剥离 `.description`——这是告诉你字段是否已解码的字段。输出完整的属性对象，而不仅仅是 key。

---

**附注**：`--param` 的有效参数也在 schema 中——`params` 部分列出了 `name` / `type` / `required` / `enum` / `default` / `description`；**如果该部分缺失，则此 key 不接受 `--param`**。

## 主题索引

| 主题 | 参考文档 | 覆盖范围 |
|---|---|---|
| 即时通讯 | [`references/lark-event-im.md`](references/lark-event-im.md) | 11 个 IM EventKey 目录 + shape 说明（扁平 vs V2 信封）+ `im.message.receive_v1` 字段注意事项（`sender_id` 仅限 open_id；`.content` 为纯文本，`interactive` 卡片除外）+ 常用 jq 配方（按 chat_type / message_type / sender 过滤） |
