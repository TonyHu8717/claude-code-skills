---
name: lark-im
version: 1.0.0
description: "飞书即时通讯：收发消息和管理群聊。发送和回复消息、搜索聊天记录、管理群聊成员、上传下载图片和文件（支持大文件分片下载）、管理表情回复。当用户需要发消息、查看或搜索聊天记录、下载聊天中的文件、查看群成员时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli im --help"
---

# im (v1)

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理**

## 核心概念

- **消息（Message）**：聊天中的一条消息，通过 `message_id`（om_xxx）标识。支持类型：text、post、image、file、audio、video、sticker、interactive（卡片）、share_chat、share_user、merge_forward 等。
- **群聊（Chat）**：群聊或单聊会话，通过 `chat_id`（oc_xxx）标识。
- **话题（Thread）**：消息下的回复话题，通过 `thread_id`（om_xxx 或 omt_xxx）标识。
- **表情回复（Reaction）**：消息上的表情回复。

## 资源关系

```
Chat (oc_xxx)
├── Message (om_xxx)
│   ├── Thread (回复话题)
│   ├── Reaction (表情)
│   └── Resource (图片 / 文件 / 视频 / 音频)
└── Member (用户 / 机器人)
```

## 重要说明

### 身份与 Token 映射

- `--as user` 表示**用户身份**，使用 `user_access_token`。调用以授权终端用户身份执行，权限取决于应用 scope 和该用户对目标聊天/消息/资源的访问权限。
- `--as bot` 表示**机器人身份**，使用 `tenant_access_token`。调用以应用机器人身份执行，行为取决于机器人的成员身份、应用可见性、可用范围和机器人专属 scope。
- 如果某个 IM API 同时支持 `user` 和 `bot`，token 类型决定了操作者身份。同一个 API 可能在一个身份下成功、在另一个身份下失败，因为所有者/管理员状态、群成员身份、租户边界或应用可用性都是针对当前调用者检查的。

### 机器人身份下的发送者名称解析

使用机器人身份（`--as bot`）获取消息时（如 `+chat-messages-list`、`+threads-messages-list`、`+messages-mget`），发送者名称可能无法解析（显示为 open_id 而非显示名称）。这发生在机器人无法访问用户联系人信息时。

**根本原因**：机器人的应用可见性设置未包含消息发送者，因此联系人 API 不返回名称。

**解决方案**：在飞书开发者后台检查应用的可见性设置——确保应用的可见范围覆盖了需要解析名称的用户。或者，使用 `--as user` 以用户身份获取消息，通常拥有更广泛的联系人访问权限。

### 卡片消息（Interactive）

卡片消息（`interactive` 类型）在事件订阅中尚不支持紧凑转换。将返回原始事件数据，并在 stderr 输出提示。

## Shortcuts（推荐优先使用）

Shortcut 是对常用操作的高级封装（`lark-cli im +<verb> [flags]`）。有 Shortcut 的操作优先使用。

| Shortcut | 说明 |
|----------|------|
| [`+chat-create`](references/lark-im-chat-create.md) | 创建群聊；user/bot；创建私有/公开群，邀请用户/机器人，可设置机器人管理员 |
| [`+chat-messages-list`](references/lark-im-chat-messages-list.md) | 列出群聊或单聊中的消息；user/bot；接受 --chat-id 或 --user-id，解析单聊 chat_id，支持时间范围/排序/分页 |
| [`+chat-search`](references/lark-im-chat-search.md) | 按关键词和/或成员 open_id 搜索可见群聊（如按群名查找 chat_id）；user/bot；支持成员/类型过滤、排序和分页 |
| [`+chat-update`](references/lark-im-chat-update.md) | 更新群聊名称或描述；user/bot；更新群聊的名称或描述 |
| [`+messages-mget`](references/lark-im-messages-mget.md) | 按 ID 批量获取消息；user/bot；最多获取 50 个 om_ 消息 ID，格式化发送者名称，展开话题回复 |
| [`+messages-reply`](references/lark-im-messages-reply.md) | 回复消息（支持话题回复）；user/bot；支持文本/markdown/帖子/媒体回复、话题内回复、幂等 key |
| [`+messages-resources-download`](references/lark-im-messages-resources-download.md) | 从消息中下载图片/文件；user/bot；支持大文件自动分片下载（8MB 分片），自动从 Content-Type 检测文件扩展名 |
| [`+messages-search`](references/lark-im-messages-search.md) | 跨群搜索消息（支持关键词、发送者、时间范围过滤），使用用户身份；仅 user；按聊天/发送者/附件/时间过滤，支持通过 `--page-all` / `--page-limit` 自动分页，通过批量 mget 和 chats batch_query 丰富结果 |
| [`+messages-send`](references/lark-im-messages-send.md) | 向群聊或个人发送消息；user/bot；发送到 chat-id 或 user-id，支持 text/markdown/帖子/媒体，支持幂等 key |
| [`+threads-messages-list`](references/lark-im-threads-messages-list.md) | 列出话题中的消息；user/bot；接受 om_/omt_ 输入，将消息 ID 解析为 thread_id，支持排序/分页 |

## API Resources

```bash
lark-cli schema im.<resource>.<method>   # 调用 API 前必须先查看参数结构
lark-cli im <resource> <method> [flags] # 调用 API
```

> **重要**：使用原生 API 时，必须先运行 `schema` 查看 `--data` / `--params` 参数结构，不要猜测字段格式。

### chats

  - `create` — 创建群。身份：仅 `bot`（`tenant_access_token`）。
  - `get` — 获取群信息。身份：支持 `user` 和 `bot`；调用者必须在目标群中才能获取完整详情，内部群必须属于同一租户。
  - `link` — 获取群分享链接。身份：支持 `user` 和 `bot`；调用者必须在目标群中，群分享限制为群主/管理员时调用者必须是群主/管理员，内部群必须属于同一租户。
  - `list` — 获取用户或机器人所在的群列表。身份：支持 `user` 和 `bot`。
  - `update` — 更新群信息。身份：支持 `user` 和 `bot`。

### chat.members

  - `bots` — 获取群内机器人列表。身份：支持 `user` 和 `bot`；调用者必须在目标群中，内部群必须属于同一租户。
  - `create` — 将用户或机器人拉入群聊。身份：支持 `user` 和 `bot`；调用者必须在目标群中；`bot` 调用时，添加的用户必须在应用可用范围内；内部群操作者必须属于同一租户；仅群主/管理员可添加成员时，调用者必须是群主/管理员，或具有 `im:chat:operate_as_owner` 的创建者机器人。
  - `delete` — 将用户或机器人移出群聊。身份：支持 `user` 和 `bot`；仅群主、管理员或创建者机器人可移除他人；每次请求最多 50 个用户或 5 个机器人。
  - `get` — 获取群成员列表。身份：支持 `user` 和 `bot`；调用者必须在目标群中，内部群必须属于同一租户。

### messages

  - `delete` — 撤回消息。身份：支持 `user` 和 `bot`；`bot` 调用时，机器人必须在群中才能撤回群消息；要撤回其他用户的群消息，机器人必须是群主、管理员或创建者；用户单聊撤回时，目标用户必须在机器人的可用范围内。
  - `forward` — 转发消息。身份：仅 `bot`（`tenant_access_token`）。
  - `merge_forward` — 合并转发消息。身份：仅 `bot`（`tenant_access_token`）。
  - `read_users` — 查询消息已读信息。身份：仅 `bot`（`tenant_access_token`）；机器人必须在群中，且只能查询最近 7 天内自己发送的消息的已读状态。

### reactions

  - `batch_query` — 批量获取消息表情。身份：支持 `user` 和 `bot`。[必读](references/lark-im-reactions.md)
  - `create` — 添加消息表情回复。身份：支持 `user` 和 `bot`；调用者必须在包含该消息的会话中。[必读](references/lark-im-reactions.md)
  - `delete` — 删除消息表情回复。身份：支持 `user` 和 `bot`；调用者必须在包含该消息的会话中，且只能删除自己添加的表情。[必读](references/lark-im-reactions.md)
  - `list` — 获取消息表情回复。身份：支持 `user` 和 `bot`；调用者必须在包含该消息的会话中。[必读](references/lark-im-reactions.md)

### images

  - `create` — 上传图片。身份：仅 `bot`（`tenant_access_token`）。

### pins

  - `create` — Pin 消息。身份：支持 `user` 和 `bot`。
  - `delete` — 移除 Pin 消息。身份：支持 `user` 和 `bot`。
  - `list` — 获取群内 Pin 消息。身份：支持 `user` 和 `bot`。

## 权限表

| 方法 | 所需 scope |
|------|-----------|
| `chats.create` | `im:chat:create` |
| `chats.get` | `im:chat:read` |
| `chats.link` | `im:chat:read` |
| `chats.list` | `im:chat:read` |
| `chats.update` | `im:chat:update` |
| `chat.members.bots` | `im:chat.members:read` |
| `chat.members.create` | `im:chat.members:write_only` |
| `chat.members.delete` | `im:chat.members:write_only` |
| `chat.members.get` | `im:chat.members:read` |
| `messages.delete` | `im:message:recall` |
| `messages.forward` | `im:message` |
| `messages.merge_forward` | `im:message` |
| `messages.read_users` | `im:message:readonly` |
| `reactions.batch_query` | `im:message.reactions:read` |
| `reactions.create` | `im:message.reactions:write_only` |
| `reactions.delete` | `im:message.reactions:write_only` |
| `reactions.list` | `im:message.reactions:read` |
| `images.create` | `im:resource` |
| `pins.create` | `im:message.pins:write_only` |
| `pins.delete` | `im:message.pins:write_only` |
| `pins.list` | `im:message.pins:read` |
