---
name: example-command
description: 一个示例用户调用技能，演示 frontmatter 选项和 skills/<name>/SKILL.md 布局
argument-hint: <required-arg> [optional-arg]
allowed-tools: [Read, Glob, Grep, Bash]
---

# 示例命令（技能格式）

此技能演示了用户调用的斜杠命令的 `skills/<name>/SKILL.md` 布局。它在功能上与旧版 `commands/example-command.md` 格式完全相同 - 两者加载方式相同；只是文件布局不同。

## 参数

用户使用以下参数调用：$ARGUMENTS

## 指令

当此技能被调用时：

1. 解析用户提供的参数
2. 使用允许的工具执行请求的操作
3. 将结果报告给用户

## Frontmatter 选项参考

此布局中的技能支持以下 frontmatter 字段：

- **name**：技能标识符（与目录名称匹配）
- **description**：在 /help 中显示的简短描述
- **argument-hint**：向用户显示的命令参数提示
- **allowed-tools**：此技能的预批准工具（减少权限提示）
- **model**：覆盖模型（例如 "haiku"、"sonnet"、"opus"）

## 使用示例

```
/example-command my-argument
/example-command arg1 arg2
```
