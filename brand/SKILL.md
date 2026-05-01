---
name: ckm:brand
description: 品牌声音、视觉形象、消息框架、资产管理、品牌一致性。用于品牌内容、语气、营销资产、品牌合规、风格指南。
argument-hint: "[update|review|create] [args]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# 品牌

品牌标识、声音、消息、资产管理和一致性框架。

## 使用场景

- 品牌声音定义和内容语气指导
- 视觉形象标准和风格指南开发
- 消息框架创建
- 品牌一致性审查和审计
- 资产组织、命名和审批
- 调色板管理和排版规范

## 快速开始

**将品牌上下文注入提示：**
```bash
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json
```

**验证资产：**
```bash
node scripts/validate-asset.cjs <asset-path>
```

**提取/比较颜色：**
```bash
node scripts/extract-colors.cjs --palette
node scripts/extract-colors.cjs <image-path>
```

## 品牌同步工作流

```bash
# 1. 编辑 docs/brand-guidelines.md（或使用 /brand update）
# 2. 同步到设计令牌
node scripts/sync-brand-to-tokens.cjs
# 3. 验证
node scripts/inject-brand-context.cjs --json | head -20
```

**同步的文件：**
- `docs/brand-guidelines.md` → 来源真相
- `assets/design-tokens.json` → 令牌定义
- `assets/design-tokens.css` → CSS 变量

## 子命令

| 子命令 | 描述 | 参考 |
|--------|------|------|
| `update` | 更新品牌标识并同步到所有设计系统 | `references/update.md` |

## 参考文件

| 主题 | 文件 |
|------|------|
| 声音框架 | `references/voice-framework.md` |
| 视觉形象 | `references/visual-identity.md` |
| 消息框架 | `references/messaging-framework.md` |
| 一致性 | `references/consistency-checklist.md` |
| 指南模板 | `references/brand-guideline-template.md` |
| 资产组织 | `references/asset-organization.md` |
| 颜色管理 | `references/color-palette-management.md` |
| 排版 | `references/typography-specifications.md` |
| 标志使用 | `references/logo-usage-rules.md` |
| 审批清单 | `references/approval-checklist.md` |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/inject-brand-context.cjs` | 提取品牌上下文用于提示注入 |
| `scripts/sync-brand-to-tokens.cjs` | 同步 brand-guidelines.md → design-tokens.json/css |
| `scripts/validate-asset.cjs` | 验证资产命名、大小、格式 |
| `scripts/extract-colors.cjs` | 提取颜色并与调色板比较 |

## 模板

| 模板 | 用途 |
|------|------|
| `templates/brand-guidelines-starter.md` | 新品牌的完整入门模板 |

## 路由

1. 从 `$ARGUMENTS` 解析子命令（第一个单词）
2. 加载对应的 `references/{subcommand}.md`
3. 使用剩余参数执行
