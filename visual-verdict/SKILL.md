---
name: visual-verdict
description: 用于截图与参考图比较的结构化视觉 QA 判定
level: 2
---

<Purpose>
使用此技能将生成的 UI 截图与一个或多个参考图像进行比较，并返回严格的 JSON 判定，以驱动下一次编辑迭代。
</Purpose>

<Use_When>
- 任务包含视觉保真度要求（布局、间距、排版、组件样式）
- 你有生成的截图和至少一张参考图像
- 在继续编辑之前需要确定性的通过/失败指导
</Use_When>

<Inputs>
- `reference_images[]`（一个或多个图像路径）
- `generated_screenshot`（当前输出图像）
- 可选：`category_hint`（如 `hackernews`、`sns-feed`、`dashboard`）
</Inputs>

<Output_Contract>
返回**仅 JSON**，格式如下：

```json
{
  "score": 0,
  "verdict": "revise",
  "category_match": false,
  "differences": ["..."],
  "suggestions": ["..."],
  "reasoning": "short explanation"
}
```

规则：
- `score`：整数 0-100
- `verdict`：简短状态（`pass`、`revise` 或 `fail`）
- `category_match`：当生成的截图匹配目标 UI 类别/风格时为 `true`
- `differences[]`：具体的视觉不匹配（布局、间距、排版、颜色、层次）
- `suggestions[]`：与差异相关的可操作的下一步编辑
- `reasoning`：1-2 句摘要

<Threshold_And_Loop>
- 目标通过阈值为 **90+**。
- 如果 `score < 90`，继续编辑并在任何进一步的视觉审查之前重新运行 `/oh-my-claudecode:visual-verdict`。
- 在下一张截图达到阈值之前，**不要**将视觉任务视为完成。
</Threshold_And_Loop>

<Debug_Visualization>
当不匹配诊断困难时：
1. 保持 `$visual-verdict` 作为权威决策。
2. 使用像素级差异工具（pixel diff / pixelmatch overlay）作为**辅助调试工具**来定位热点。
3. 将像素差异热点转换为具体的 `differences[]` 和 `suggestions[]` 更新。
</Debug_Visualization>

<Example>
```json
{
  "score": 87,
  "verdict": "revise",
  "category_match": true,
  "differences": [
    "顶部导航间距比参考更紧凑",
    "主按钮使用了更小的字体粗细"
  ],
  "suggestions": [
    "将导航项水平内边距增加 4px",
    "将主按钮 font-weight 设置为 600"
  ],
  "reasoning": "核心布局匹配，但样式细节仍有差异。"
}
```
</Example>

Task: {{ARGUMENTS}}
