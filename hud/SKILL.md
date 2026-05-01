---
name: hud
description: 配置 HUD 显示选项（布局、预设、显示元素）
argument-hint: "[setup|minimal|focused|full|status]"
role: config-writer  # DOCUMENTATION ONLY - This skill writes to ~/.claude/ paths
scope: ~/.claude/**  # DOCUMENTATION ONLY - Allowed write scope
level: 2
---

# HUD 技能

为状态栏配置 OMC HUD（抬头显示器）。

注意：本指南中所有 `~/.claude/...` 路径在设置了 `CLAUDE_CONFIG_DIR` 环境变量时会遵循该变量。

## 快速命令

| 命令 | 描述 |
|------|------|
| `/oh-my-claudecode:hud` | 显示当前 HUD 状态（需要时自动设置） |
| `/oh-my-claudecode:hud setup` | 安装/修复 HUD 状态栏 |
| `/oh-my-claudecode:hud minimal` | 切换到最小显示 |
| `/oh-my-claudecode:hud focused` | 切换到聚焦显示（默认） |
| `/oh-my-claudecode:hud full` | 切换到完整显示 |
| `/oh-my-claudecode:hud status` | 显示详细 HUD 状态 |

## 自动设置

当你运行 `/oh-my-claudecode:hud` 或 `/oh-my-claudecode:hud setup` 时，系统将自动：
1. 检查 `~/.claude/hud/omc-hud.mjs` 是否存在
2. 检查 `~/.claude/settings.json` 中是否配置了 `statusLine`
3. 如果缺失，创建 HUD 包装脚本并配置设置
4. 报告状态，如果进行了更改则提示重启 Claude Code

**重要**：如果参数是 `setup` 或者 HUD 脚本不存在于 `~/.claude/hud/omc-hud.mjs`，你必须使用以下说明直接创建 HUD 文件。

### 设置说明（运行这些命令）

**步骤 1：** 检查是否需要设置：
```bash
node -e "const p=require('path'),f=require('fs'),d=process.env.CLAUDE_CONFIG_DIR||p.join(require('os').homedir(),'.claude');console.log(f.existsSync(p.join(d,'hud','omc-hud.mjs'))?'EXISTS':'MISSING')"
```

**步骤 2：** 验证插件已安装：
```bash
node -e "const p=require('path'),f=require('fs'),d=process.env.CLAUDE_CONFIG_DIR||p.join(require('os').homedir(),'.claude'),b=p.join(d,'plugins','cache','omc','oh-my-claudecode');try{const v=f.readdirSync(b).filter(x=>/^\d/.test(x)).sort((a,c)=>a.localeCompare(c,void 0,{numeric:true}));if(v.length===0){console.log('Plugin not installed - run: /plugin install oh-my-claudecode');process.exit()}const l=v[v.length-1],h=p.join(b,l,'dist','hud','index.js');console.log('Version:',l);console.log(f.existsSync(h)?'READY':'NOT_FOUND - try reinstalling: /plugin install oh-my-claudecode')}catch{console.log('Plugin not installed - run: /plugin install oh-my-claudecode')}"
```

**步骤 3：** 如果 omc-hud.mjs 缺失或参数为 `setup`，从规范模板安装 HUD 包装器及其依赖：

```bash
HUD_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hud"
mkdir -p "$HUD_DIR/lib"
cp "${CLAUDE_PLUGIN_ROOT}/scripts/lib/hud-wrapper-template.txt" "$HUD_DIR/omc-hud.mjs"
cp "${CLAUDE_PLUGIN_ROOT}/scripts/lib/config-dir.mjs" "$HUD_DIR/lib/config-dir.mjs"
```

**重要：** 始终从规范模板 `scripts/lib/hud-wrapper-template.txt` 复制。不要内联编写包装器内容 — 模板是唯一真实来源，受漂移测试保护（`src/__tests__/hud-wrapper-template-sync.test.ts`、`src/__tests__/paths-consistency.test.ts`）。

**步骤 4：** 设置可执行权限（仅 Unix，Windows 上跳过）：
```bash
node -e "if(process.platform==='win32'){console.log('Skipped (Windows)')}else{require('fs').chmodSync(require('path').join(process.env.CLAUDE_CONFIG_DIR||require('path').join(require('os').homedir(),'.claude'),'hud','omc-hud.mjs'),0o755);console.log('Done')}"
```

**步骤 5：** 更新 settings.json 以使用 HUD：

读取 `${CLAUDE_CONFIG_DIR:-~/.claude}/settings.json`，然后更新/添加 `statusLine` 字段。

**重要：** 不要在命令中使用 `~`。在 Unix 上，使用 `$HOME` 以保持路径在不同机器间的可移植性。在 Windows 上，使用绝对路径，因为 Windows 不会在 shell 命令中展开 `~`。

如果在 Windows 上，先确定正确的路径：
```bash
node -e "const p=require('path').join(require('os').homedir(),'.claude','hud','omc-hud.mjs').split(require('path').sep).join('/');console.log(JSON.stringify(p))"
```

**重要：** 命令路径在所有平台上必须使用正斜杠。Claude Code 通过 bash 执行 statusLine 命令，bash 将反斜杠解释为转义字符，会破坏路径。

然后设置 `statusLine` 字段。在 Unix 上应保持可移植性，如下所示：
```json
{
  "statusLine": {
    "type": "command",
    "command": "node ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hud/omc-hud.mjs"
  }
}
```

在 Windows 上路径使用正斜杠（而非反斜杠）：
```json
{
  "statusLine": {
    "type": "command",
    "command": "node C:/Users/username/.claude/hud/omc-hud.mjs"
  }
}
```

使用 Edit 工具添加/更新此字段，同时保留其他设置。

**步骤 6：** 清理旧的 HUD 脚本（如果有）：
```bash
node -e "const p=require('path'),f=require('fs'),d=process.env.CLAUDE_CONFIG_DIR||p.join(require('os').homedir(),'.claude'),t=p.join(d,'hud','omc-hud.js');try{if(f.existsSync(t)){f.unlinkSync(t);console.log('Removed legacy omc-hud.js')}else{console.log('No legacy script found')}}catch{}"
```

**步骤 7：** 告知用户重启 Claude Code 以使更改生效。

## 显示预设

### 最小（Minimal）
只显示基本要素：
```
[OMC] ralph | ultrawork | todos:2/5
```

### 聚焦（Focused，默认）
显示所有相关元素：
```
[OMC] branch:main | ralph:3/10 | US-002 | ultrawork skill:planner | ctx:67% | agents:2 | bg:3/5 | todos:2/5
```

### 完整（Full）
显示所有内容，包括多行代理详情：
```
[OMC] repo:oh-my-claudecode branch:main | ralph:3/10 | US-002 (2/5) | ultrawork | ctx:[████░░]67% | agents:3 | bg:3/5 | todos:2/5
├─ O architect    2m   analyzing architecture patterns...
├─ e explore     45s   searching for test files
└─ s executor     1m   implementing validation logic
```

## 多行代理显示

当代理运行时，HUD 在单独的行上显示详细信息：
- **树形字符**（`├─`、`└─`）显示视觉层级
- **代理代码**（O、e、s）用模型层级颜色指示代理类型
- **持续时间**显示每个代理运行了多长时间
- **描述**显示每个代理正在做什么（最多 45 个字符）

## 显示元素

| 元素 | 描述 |
|------|------|
| `[OMC]` | 模式标识符 |
| `repo:name` | Git 仓库名称（青色） |
| `branch:name` | Git 分支名称（青色） |
| `ralph:3/10` | Ralph 循环迭代/最大值 |
| `US-002` | 当前 PRD 故事 ID |
| `ultrawork` | 活动模式徽章 |
| `skill:name` | 最后激活的技能（青色） |
| `ctx:67%` | 上下文窗口使用率 |
| `agents:2` | 运行中的子代理数量 |
| `bg:3/5` | 后台任务槽位 |
| `todos:2/5` | 待办事项完成情况 |

## 颜色编码

- **绿色**：正常/健康
- **黄色**：警告（上下文 >70%，ralph >7）
- **红色**：严重（上下文 >85%，ralph 达到最大值）

## 配置位置

HUD 配置存储在 `~/.claude/settings.json` 的 `omcHud` 键下（或你在 `CLAUDE_CONFIG_DIR` 中设置的自定义配置目录）。

旧版配置位置（已弃用）：`~/.claude/.omc/hud-config.json`

## 手动配置

你可以手动编辑配置文件。每个选项可以单独设置 - 未设置的值将使用默认值。

```json
{
  "preset": "focused",
  "elements": {
    "omcLabel": true,
    "ralph": true,
    "autopilot": true,
    "prdStory": true,
    "activeSkills": true,
    "lastSkill": true,
    "contextBar": true,
    "agents": true,
    "agentsFormat": "multiline",
    "backgroundTasks": true,
    "todos": true,
    "thinking": true,
    "thinkingFormat": "text",
    "permissionStatus": false,
    "apiKeySource": false,
    "profile": true,
    "promptTime": true,
    "sessionHealth": true,
    "useBars": true,
    "showCallCounts": true,
    "callCountsFormat": "auto",
    "safeMode": true,
    "maxOutputLines": 4
  },
  "thresholds": {
    "contextWarning": 70,
    "contextCompactSuggestion": 80,
    "contextCritical": 85,
    "ralphWarning": 7
  },
  "staleTaskThresholdMinutes": 30,
  "contextLimitWarning": {
    "threshold": 80,
    "autoCompact": false
  }
}
```

### callCountsFormat

控制调用计数徽章图标样式：
- `"auto"`（默认）：macOS/Linux 上使用 emoji，Windows/WSL 上使用 ASCII
- `"emoji"`：强制使用 `🔧 🤖 ⚡`
- `"ascii"`：强制使用 `T: A: S:`

### safeMode

当 `safeMode` 为 `true`（默认）时，HUD 会去除 ANSI 代码并使用纯 ASCII 输出，以防止并发更新期间的终端渲染损坏。这在 Windows 上和使用终端多路复用器时尤为重要。

### agentsFormat 选项

- `count`：agents:2
- `codes`：agents:Oes（带模型层级大小写的类型代码）
- `codes-duration`：agents:O(2m)es（带持续时间的代码）
- `detailed`：agents:[architect(2m),explore,exec]
- `descriptions`：O:analyzing code | e:searching（代码 + 正在做什么）
- `tasks`：[analyzing code, searching...]（仅描述）
- `multiline`：多行显示，在单独的行上显示完整的代理详情

## 故障排除

如果 HUD 未显示：
1. 运行 `/oh-my-claudecode:hud setup` 自动安装和配置
2. 设置完成后重启 Claude Code
3. 如果仍然不工作，运行 `/oh-my-claudecode:omc-doctor` 进行完整诊断

**旧版字符串格式迁移：** 旧版 OMC 将 `statusLine` 写为纯字符串（例如 `"~/.claude/hud/omc-hud.mjs"`）。现代 Claude Code（v2.1+）需要对象格式。运行安装程序或 `/oh-my-claudecode:hud setup` 将自动将旧版字符串迁移为正确的对象格式：
```json
{
  "statusLine": {
    "type": "command",
    "command": "node ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hud/omc-hud.mjs"
  }
}
```

**Node 24+ 兼容性：** HUD 包装脚本从 `node:os`（而非 `node:path`）导入 `homedir`。如果遇到 `SyntaxError: The requested module 'path' does not provide an export named 'homedir'`，请重新运行安装程序以重新生成 `omc-hud.mjs`。

手动验证：
- HUD 脚本：`~/.claude/hud/omc-hud.mjs`
- 设置：`~/.claude/settings.json` 应将 `statusLine` 配置为包含 `type` 和 `command` 字段的对象

---

*HUD 在活动会话期间每约 300ms 自动更新一次。*
