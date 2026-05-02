---
name: skills-sync
description: |
  同步 Claude Code 技能目录到 GitHub 仓库。支持三种模式：upload（本地覆盖远程）、download（远程覆盖本地）、merge（双向合并，冲突时提示用户确认）。触发词："skills sync"、"sync skills"、"同步技能"、"上传技能"、"下载技能"、upload/download/merge + skills。
---

# Skills Sync — 技能目录同步

将 `.agents/skills/` 目录与 GitHub 仓库进行双向同步。

## 配置

同步基于 `.agents/skills/` 目录内的 git 仓库。首次使用前需确保：

1. `.agents/skills/` 已初始化为 git 仓库（`git init`）
2. 已配置远程仓库（`git remote add origin <url>`）
3. 已完成首次推送（`git push -u origin master`）

如果未配置，引导用户完成初始化：
```
cd .agents/skills
git init
git remote add origin https://github.com/<user>/<repo>.git
git add . && git commit -m "init" && git push -u origin master
```

## 三种模式

### 1. Upload（本地 → 远程）

**触发关键词**：`upload`、`上传`、`push`

本地内容覆盖远程仓库。适用于本地有修改、要推送到 GitHub 的场景。

**执行流程：**
1. `git add -A` — 暂存所有变更（新增、修改、删除）
2. `git status` — 显示将要上传的变更，让用户确认
3. 用户确认后，`git commit -m "sync: upload skills"` 提交
4. `git push --force-with-lease origin master` — 强制推送覆盖远程

**安全措施：**
- 推送前显示变更列表，用户确认后才执行
- 使用 `--force-with-lease`（而非 `--force`），防止覆盖他人的并发提交
- 推送前自动创建备份分支：`git branch backup/main-$(date +%Y%m%d%H%M%S)`

### 2. Download（远程 → 本地）

**触发关键词**：`download`、`下载`、`pull`

远程内容覆盖本地。适用于在其他设备修改了技能、要同步到本地的场景。

**执行流程：**
1. `git fetch origin` — 获取远程最新内容
2. `git log HEAD..origin/master --oneline` — 显示远程有而本地没有的提交
3. `git diff HEAD origin/master --stat` — 显示文件差异
4. 用户确认后，`git reset --hard origin/master` — 本地强制对齐远程

**安全措施：**
- 覆盖前显示差异，用户确认后才执行
- 覆盖前自动创建备份分支：`git branch backup/local-$(date +%Y%m%d%H%M%S)`
- 如果本地有未提交的修改，先提示用户

### 3. Merge（双向合并）— 默认模式

**触发关键词**：`merge`、`sync`、`同步`，或**不指定任何关键词时的默认行为**

双向合并本地和远程的变更。适用于日常同步场景。

**执行流程：**
1. `git fetch origin` — 获取远程最新内容
2. `git status` — 检查本地是否有未提交的修改
3. 如果有未提交的修改：
   - `git stash` — 暂存本地修改
   - `git pull --rebase origin master` — 拉取远程并变基
   - `git stash pop` — 恢复本地修改
4. 如果没有未提交的修改：
   - `git pull --rebase origin master` — 直接拉取并变基

**冲突处理：**
如果 rebase 过程中出现冲突：
1. 显示冲突文件列表：`git diff --name-only --diff-filter=U`
2. 对每个冲突文件，进行**智能分析**后给出选择建议：

   **分析维度：**
   - **内容对比**：统计本地/远程版本的行数、功能描述数量、触发条件覆盖范围
   - **更新时间**：`git log -1 --format="%ai" -- <file>` 获取本地最后修改时间，`git log -1 --format="%ai" origin/master -- <file>` 获取远程最后修改时间
   - **功能丰富度**：对比 description 字段长度、SKILL.md 正文段落数、引用的参考文件数量

   **呈现格式：**
   ```
   ━━━ 冲突文件: {filename} ━━━

   📊 版本对比：
   ┌──────────┬──────────────┬──────────────┐
   │ 维度     │ 本地版本     │ 远程版本     │
   ├──────────┼──────────────┼──────────────┤
   │ 修改时间 │ 2026-04-30   │ 2026-04-28   │ ← 本地更新
   │ 文件大小 │ 2.3KB        │ 1.8KB        │ ← 本地更大
   │ 内容行数 │ 45行         │ 32行         │ ← 本地更详细
   └──────────┴──────────────┴──────────────┘

   💡 建议：保留本地（内容更丰富、更新时间更近）

   请选择：[1] 保留本地  [2] 保留远程  [3] 手动合并
   ```

3. 用户选择后执行对应操作：
   - **保留本地**：`git checkout --ours <file>`
   - **保留远程**：`git checkout --theirs <file>`
   - **手动合并**：提示用户编辑文件后 `git add <file>`
4. 所有冲突解决后：`git rebase --continue`
5. `git push origin master` — 推送合并结果到 GitHub

## 通用规则

- **工作目录**：所有 git 命令在 `.agents/skills/` 目录下执行
- **分支**：统一使用 `master` 分支
- **提交信息格式**：`sync: {mode} — {brief description}`
- **备份**：upload 和 download 操作前自动创建备份分支
- **确认**：任何覆盖操作前必须显示差异并获得用户确认
- **错误处理**：git 命令失败时，显示错误信息并建议恢复步骤，不自动执行 `git reset --hard` 等破坏性操作
- **REGISTRY.md**：upload 模式下，确保 `REGISTRY.md` 已更新后再推送；download/merge 后提示用户检查 `REGISTRY.md` 是否需要更新

## 使用示例

```
# 日常同步（默认 merge）
/skills-sync

# 明确上传
/skills-sync upload

# 明确下载
/skills-sync download

# 明确合并
/skills-sync merge
```
