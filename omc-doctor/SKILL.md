---
name: omc-doctor
description: 诊断和修复 oh-my-claudecode 安装问题
level: 3
---

# 诊断技能

注意：本指南中所有 `~/.claude/...` 路径在设置了 `CLAUDE_CONFIG_DIR` 环境变量时会遵循该变量。

## 任务：运行安装诊断

你是 OMC 医生 - 诊断和修复安装问题。

### 步骤 1：检查插件版本

```bash
# 获取已安装和最新版本（跨平台）
node -e "const p=require('path'),f=require('fs'),h=require('os').homedir(),d=process.env.CLAUDE_CONFIG_DIR||p.join(h,'.claude'),b=p.join(d,'plugins','cache','omc','oh-my-claudecode');try{const v=f.readdirSync(b).filter(x=>/^\d/.test(x)).sort((a,c)=>a.localeCompare(c,void 0,{numeric:true}));console.log('Installed:',v.length?v[v.length-1]:'(none)')}catch{console.log('Installed: (none)')}"
npm view oh-my-claudecode version 2>/dev/null || echo "Latest: (unavailable)"
```

**诊断**：
- 如果没有安装版本：严重 - 插件未安装
- 如果已安装 != 最新：警告 - 插件过时
- 如果存在多个版本：警告 - 缓存过期

### 步骤 2：检查 settings.json 中的遗留钩子

读取 `${CLAUDE_CONFIG_DIR:-~/.claude}/settings.json`（配置文件级别）和 `./.claude/settings.json`（项目级别），检查是否有 `"hooks"` 键包含如下条目：
- `bash ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/keyword-detector.sh`
- `bash ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/persistent-mode.sh`
- `bash ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/session-start.sh`

**诊断**：
- 如果找到：严重 - 遗留钩子导致重复

### 步骤 3：检查遗留的 Bash 钩子脚本

```bash
ls -la "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/hooks/*.sh 2>/dev/null
```

**诊断**：
- 如果存在 `keyword-detector.sh`、`persistent-mode.sh`、`session-start.sh` 或 `stop-continuation.sh`：警告 - 遗留脚本（可能导致混淆）

### 步骤 4：检查 CLAUDE.md

```bash
# 检查 CLAUDE.md 是否存在
ls -la "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/CLAUDE.md 2>/dev/null

# 检查 OMC 标记（<!-- OMC:START --> 是标准标记）
grep -q "<!-- OMC:START -->" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/CLAUDE.md" 2>/dev/null && echo "Has OMC config" || echo "Missing OMC config in CLAUDE.md"

# 检查 CLAUDE.md（或确定性伴侣文件）版本标记，并与最新已安装插件缓存版本比较
node -e "const p=require('path'),f=require('fs'),h=require('os').homedir(),d=process.env.CLAUDE_CONFIG_DIR||p.join(h,'.claude');const base=p.join(d,'CLAUDE.md');let baseContent='';try{baseContent=f.readFileSync(base,'utf8')}catch{};let candidates=[base];let referenced='';const importMatch=baseContent.match(/CLAUDE-[^ )]*\\.md/);if(importMatch){referenced=p.join(d,importMatch[0]);candidates.push(referenced)}else{const defaultCompanion=p.join(d,'CLAUDE-omc.md');if(f.existsSync(defaultCompanion))candidates.push(defaultCompanion);try{const others=f.readdirSync(d).filter(n=>/^CLAUDE-.*\\.md$/i.test(n)).sort().map(n=>p.join(d,n));for(const o of others){if(candidates.includes(o)===false)candidates.push(o)}}catch{}};let claudeV='(missing)';let claudeSource='(none)';for(const file of candidates){try{const c=f.readFileSync(file,'utf8');const m=c.match(/<!--\\s*OMC:VERSION:([^\\s]+)\\s*-->/i);if(m){claudeV=m[1];claudeSource=file;break}}catch{}};if(claudeV==='(missing)'&&candidates.length>0){claudeV='(missing marker)';claudeSource='scanned deterministic CLAUDE sources';};let pluginV='(none)';try{const b=p.join(d,'plugins','cache','omc','oh-my-claudecode');const v=f.readdirSync(b).filter(x=>/^\\d/.test(x)).sort((a,c)=>a.localeCompare(c,void 0,{numeric:true}));pluginV=v.length?v[v.length-1]:'(none)';}catch{};console.log('CLAUDE.md OMC version:',claudeV);console.log('OMC version source:',claudeSource);console.log('Latest cached plugin version:',pluginV);if(claudeV==='(missing)'||claudeV==='(missing marker)'||pluginV==='(none)'){console.log('VERSION CHECK SKIPPED: missing CLAUDE marker or plugin cache')}else if(claudeV===pluginV){console.log('VERSION MATCH: CLAUDE and plugin cache are aligned')}else{console.log('VERSION DRIFT: CLAUDE.md and plugin versions differ')}"

# 检查伴侣文件的文件分割模式（如 CLAUDE-omc.md）
find "${CLAUDE_CONFIG_DIR:-$HOME/.claude}" -maxdepth 1 -type f -name 'CLAUDE-*.md' -print 2>/dev/null
while IFS= read -r f; do
  grep -q "<!-- OMC:START -->" "$f" 2>/dev/null && echo "Has OMC config in companion: $f"
done < <(find "${CLAUDE_CONFIG_DIR:-$HOME/.claude}" -maxdepth 1 -type f -name 'CLAUDE-*.md' -print 2>/dev/null)

# 检查 CLAUDE.md 是否引用了伴侣文件
grep -o "CLAUDE-[^ )]*\.md" "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/CLAUDE.md" 2>/dev/null
```

**诊断**：
- 如果 CLAUDE.md 缺失：严重 - CLAUDE.md 未配置
- 如果在 CLAUDE.md 中找到 `<!-- OMC:START -->`：正常
- 如果在伴侣文件（如 `CLAUDE-omc.md`）中找到 `<!-- OMC:START -->`：正常 - 检测到文件分割模式
- 如果 CLAUDE.md 或任何伴侣文件中没有 OMC 标记：警告 - CLAUDE.md 过时
- 如果确定性 CLAUDE 源扫描（基础 + 引用的伴侣文件）中缺少 `OMC:VERSION` 标记：警告 - 无法验证 CLAUDE.md 新鲜度
- 如果 `CLAUDE.md OMC version` != `Latest cached plugin version`：警告 - 检测到版本漂移（运行 `omc update` 或 `omc setup`）

### 步骤 5：检查过期的插件缓存

```bash
# 计算缓存中的版本数（跨平台）
node -e "const p=require('path'),f=require('fs'),h=require('os').homedir(),d=process.env.CLAUDE_CONFIG_DIR||p.join(h,'.claude'),b=p.join(d,'plugins','cache','omc','oh-my-claudecode');try{const v=f.readdirSync(b).filter(x=>/^\d/.test(x));console.log(v.length+' version(s):',v.join(', '))}catch{console.log('0 versions')}"
```

**诊断**：
- 如果 > 1 个版本：警告 - 多个缓存版本（建议清理）

### 步骤 6：检查遗留的 Curl 安装内容

检查通过 curl 安装的遗留代理、命令和技能（在插件系统之前）。
**重要**：仅标记名称与实际插件提供的名称匹配的文件。不要标记与 OMC 无关的用户自定义代理/命令/技能。

```bash
# 检查遗留代理目录
ls -la "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/agents/ 2>/dev/null

# 检查遗留命令目录
ls -la "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/commands/ 2>/dev/null

# 检查遗留技能目录
ls -la "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/skills/ 2>/dev/null
```

**诊断**：
- 如果 `~/.claude/agents/` 存在且文件匹配插件代理名称：警告 - 遗留代理（现在由插件提供）
- 如果 `~/.claude/commands/` 存在且文件匹配插件命令名称：警告 - 遗留命令（现在由插件提供）
- 如果 `~/.claude/skills/` 存在且文件匹配插件技能名称：警告 - 遗留技能（现在由插件提供）
- 如果存在不匹配插件名称的自定义文件：正常 - 这些是用户自定义内容，不要标记

**已知插件代理名称**（检查 agents/ 中是否有这些）：
`architect.md`、`document-specialist.md`、`explore.md`、`executor.md`、`debugger.md`、`planner.md`、`analyst.md`、`critic.md`、`verifier.md`、`test-engineer.md`、`designer.md`、`writer.md`、`qa-tester.md`、`scientist.md`、`security-reviewer.md`、`code-reviewer.md`、`git-master.md`、`code-simplifier.md`

**已知插件技能名称**（检查 skills/ 中是否有这些）：
`ai-slop-cleaner`、`ask`、`autopilot`、`cancel`、`ccg`、`configure-notifications`、`deep-interview`、`deepinit`、`external-context`、`hud`、`learner`、`mcp-setup`、`omc-doctor`、`omc-setup`、`omc-teams`、`plan`、`project-session-manager`、`ralph`、`ralplan`、`release`、`sciomc`、`setup`、`skill`、`team`、`ultraqa`、`ultrawork`、`visual-verdict`、`writer-memory`

**已知插件命令名称**（检查 commands/ 中是否有这些）：
`ultrawork.md`、`deepsearch.md`

---

## 报告格式

运行所有检查后，输出报告：

```
## OMC 诊断报告

### 摘要
[健康 / 发现问题]

### 检查

| 检查 | 状态 | 详情 |
|------|------|------|
| 插件版本 | 正常/警告/严重 | ... |
| 遗留钩子（settings.json） | 正常/严重 | ... |
| 遗留脚本（~/.claude/hooks/） | 正常/警告 | ... |
| CLAUDE.md | 正常/警告/严重 | ... |
| 插件缓存 | 正常/警告 | ... |
| 遗留代理（~/.claude/agents/） | 正常/警告 | ... |
| 遗留命令（~/.claude/commands/） | 正常/警告 | ... |
| 遗留技能（~/.claude/skills/） | 正常/警告 | ... |

### 发现的问题
1. [问题描述]
2. [问题描述]

### 建议的修复
[根据问题列出修复方案]
```

---

## 自动修复（如果用户确认）

如果发现问题，询问用户："您希望我自动修复这些问题吗？"

如果是，应用修复：

### 修复：settings.json 中的遗留钩子
从 `${CLAUDE_CONFIG_DIR:-~/.claude}/settings.json` 中移除 `"hooks"` 部分（保留其他设置不变）

### 修复：遗留 Bash 脚本
```bash
rm -f "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/hooks/keyword-detector.sh
rm -f "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/hooks/persistent-mode.sh
rm -f "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/hooks/session-start.sh
rm -f "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/hooks/stop-continuation.sh
```

### 修复：过时的插件
```bash
# 清除插件缓存（跨平台）
node -e "const p=require('path'),f=require('fs'),d=process.env.CLAUDE_CONFIG_DIR||p.join(require('os').homedir(),'.claude'),b=p.join(d,'plugins','cache','omc','oh-my-claudecode');try{f.rmSync(b,{recursive:true,force:true});console.log('Plugin cache cleared. Restart Claude Code to fetch latest version.')}catch{console.log('No plugin cache found')}"
```

### 修复：过期缓存（多个版本）
```bash
# 仅保留最新版本（跨平台）
node -e "const p=require('path'),f=require('fs'),h=require('os').homedir(),d=process.env.CLAUDE_CONFIG_DIR||p.join(h,'.claude'),b=p.join(d,'plugins','cache','omc','oh-my-claudecode');try{const v=f.readdirSync(b).filter(x=>/^\d/.test(x)).sort((a,c)=>a.localeCompare(c,void 0,{numeric:true}));v.slice(0,-1).forEach(x=>f.rmSync(p.join(b,x),{recursive:true,force:true}));console.log('Removed',v.length-1,'old version(s)')}catch(e){console.log('No cache to clean')}"
```

### 修复：缺失/过时的 CLAUDE.md
从 GitHub 获取最新内容并写入 `${CLAUDE_CONFIG_DIR:-~/.claude}/CLAUDE.md`：
```
WebFetch(url: "https://raw.githubusercontent.com/Yeachan-Heo/oh-my-claudecode/main/docs/CLAUDE.md", prompt: "Return the complete raw markdown content exactly as-is")
```

### 修复：遗留的 Curl 安装内容

移除遗留的代理、命令和技能目录（现在由插件提供）：

```bash
# 先备份（可选 - 询问用户）
# mv "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/agents "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/agents.bak
# mv "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/commands "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/commands.bak
# mv "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/skills "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/skills.bak

# 或直接删除
rm -rf "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/agents
rm -rf "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/commands
rm -rf "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/skills
```

**注意**：仅在这些包含 oh-my-claudecode 相关文件时才删除。如果用户有自定义代理/命令/技能，请警告他们并在删除前询问。

---

## 修复后

应用修复后，通知用户：
> 修复已应用。**重启 Claude Code** 以使更改生效。
