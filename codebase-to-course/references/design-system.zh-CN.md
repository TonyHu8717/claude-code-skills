# 设计系统参考

课程系统的完整 CSS 设计令牌库。所有令牌在 `references/styles.css` 中定义，可通过 `_base.html` 中的 `:root` 按课程覆盖。

## 1. 调色板

### 背景
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--color-bg` | `#FAF7F2` | 主背景——温暖的米白色，如陈年纸 |
| `--color-bg-warm` | `#F5F0E8` | 交替模块背景——略微更暖 |
| `--color-bg-code` | `#1E1E2E` | 代码块——深靛蓝炭色 |

### 文本
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--color-text` | `#2C2A28` | 主文本——深炭色，绝不是纯黑 |
| `--color-text-secondary` | `#6B6560` | 次要文本——描述、副标题 |
| `--color-text-muted` | `#9E9790` | 柔和文本——标签、提示 |

### 边框和表面
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--color-border` | `#E5DFD6` | 标准边框 |
| `--color-border-light` | `#EEEBE5` | 微妙边框 |
| `--color-surface` | `#FFFFFF` | 卡片、容器 |
| `--color-surface-warm` | `#FDF9F3` | 翻译块、暖色表面 |

### 强调色（通过 `_base.html` 按课程覆盖）
| 令牌 | 默认值 | 用途 |
|-------|---------|------|
| `--color-accent` | `#D94F30` | 主强调色——朱红 |
| `--color-accent-hover` | `#C4432A` | 悬停状态 |
| `--color-accent-light` | `#FDEEE9` | 浅强调背景 |
| `--color-accent-muted` | `#E8836C` | 柔和强调——已访问点、微妙高亮 |

**强调色调色板选项：**
- **朱红**（默认）：`#D94F30` / `#C4432A` / `#FDEEE9` / `#E8836C`
- **珊瑚**：`#E06B56` / `#C85A47` / `#FDECEA` / `#E89585`
- **青色**：`#2A7B9B` / `#1F6280` / `#E4F2F7` / `#5A9DB8`
- **琥珀**：`#D4A843` / `#BF9530` / `#FDF5E0` / `#E0C070`
- **森林**：`#2D8B55` / `#226B41` / `#E8F5EE` / `#5AAD7A`

### 语义颜色
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--color-success` | `#2D8B55` | 正确答案、成功状态 |
| `--color-success-light` | `#E8F5EE` | 成功背景 |
| `--color-error` | `#C93B3B` | 错误答案、错误 |
| `--color-error-light` | `#FDE8E8` | 错误背景 |
| `--color-info` | `#2A7B9B` | 信息提示、场景 |
| `--color-info-light` | `#E4F2F7` | 信息背景 |

### 角色颜色（用于群聊头像、流程图）
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--color-actor-1` | `#D94F30` | 主要角色（朱红） |
| `--color-actor-2` | `#2A7B9B` | 次要角色（青色） |
| `--color-actor-3` | `#7B6DAA` | 第三角色（紫色） |
| `--color-actor-4` | `#D4A843` | 第四角色（琥珀） |
| `--color-actor-5` | `#2D8B55` | 第五角色（绿色） |

**规则：** 偶数模块使用 `--color-bg`，奇数模块使用 `--color-bg-warm`，形成视觉节奏。

## 2. 排版

### 字体系列
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--font-display` | `'Bricolage Grotesque', Georgia, serif` | 标题——粗体、几何、有个性 |
| `--font-body` | `'DM Sans', -apple-system, sans-serif` | 正文——干净、易读 |
| `--font-mono` | `'JetBrains Mono', 'Fira Code', 'Consolas', monospace` | 代码——连字、清晰区分 |

**绝不要用：** Inter、Roboto、Arial、Space Grotesk——这些太普通了。

### 字体比例（1.25 倍率）
| 令牌 | 值 |
|-------|-------|
| `--text-xs` | `0.75rem` (12px) |
| `--text-sm` | `0.875rem` (14px) |
| `--text-base` | `1rem` (16px) |
| `--text-lg` | `1.125rem` (18px) |
| `--text-xl` | `1.25rem` (20px) |
| `--text-2xl` | `1.5rem` (24px) |
| `--text-3xl` | `1.875rem` (30px) |
| `--text-4xl` | `2.25rem` (36px) |
| `--text-5xl` | `3rem` (48px) |
| `--text-6xl` | `3.75rem` (60px) |

### 行高
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--leading-tight` | `1.15` | 标题 |
| `--leading-snug` | `1.3` | 副标题、短文本 |
| `--leading-normal` | `1.6` | 正文 |
| `--leading-loose` | `1.8` | 长篇阅读 |

### Google Fonts 链接（在 `_base.html` 中）
```html
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400;1,9..40,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

## 3. 间距和布局

### 间距比例
| 令牌 | 值 |
|-------|-------|
| `--space-1` | `0.25rem` (4px) |
| `--space-2` | `0.5rem` (8px) |
| `--space-3` | `0.75rem` (12px) |
| `--space-4` | `1rem` (16px) |
| `--space-5` | `1.25rem` (20px) |
| `--space-6` | `1.5rem` (24px) |
| `--space-8` | `2rem` (32px) |
| `--space-10` | `2.5rem` (40px) |
| `--space-12` | `3rem` (48px) |
| `--space-16` | `4rem` (64px) |
| `--space-20` | `5rem` (80px) |
| `--space-24` | `6rem` (96px) |

### 内容宽度
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--content-width` | `800px` | 标准内容 |
| `--content-width-wide` | `1000px` | 宽内容（导航、图表） |
| `--nav-height` | `50px` | 固定导航栏高度 |

### 模块布局
- 全视口高度：`min-height: 100dvh`，`100vh` 后备
- 滚动吸附：`scroll-snap-type: y proximity`（不是 mandatory）
- 顶部内边距考虑导航栏：`padding-top: calc(var(--nav-height) + var(--space-12))`

## 4. 阴影和深度

四种阴影尺寸，使用暖色调 RGBA 值。**绝不要使用纯黑色阴影。**

| 令牌 | 值 |
|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(44,42,40,0.05)` |
| `--shadow-md` | `0 4px 12px rgba(44,42,40,0.08)` |
| `--shadow-lg` | `0 8px 24px rgba(44,42,40,0.10)` |
| `--shadow-xl` | `0 16px 48px rgba(44,42,40,0.12)` |

## 5. 圆角

| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--radius-sm` | `8px` | 小元素（徽章、按钮） |
| `--radius-md` | `12px` | 卡片、代码块 |
| `--radius-lg` | `16px` | 大容器（测验、聊天） |
| `--radius-full` | `9999px` | 药丸形、圆形 |

## 6. 动画和过渡

### 缓动曲线
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--ease-out` | `cubic-bezier(0.16,1,0.3,1)` | 进入元素 |
| `--ease-in-out` | `cubic-bezier(0.65,0,0.35,1)` | 数据包动画 |

### 时长令牌
| 令牌 | 值 | 用途 |
|-------|-------|------|
| `--duration-fast` | `150ms` | 悬停状态、切换 |
| `--duration-normal` | `300ms` | 过渡、揭示 |
| `--duration-slow` | `500ms` | 页面级动画 |
| `--stagger-delay` | `120ms` | 交错子元素的延迟 |

### 滚动触发揭示
在元素上使用 `.animate-in` 类。当滚动到视图中时，它们开始动画化。`main.js` 中的 Intersection Observer 会添加 `.visible` 类，因此元素只动画一次。

```html
<div class="animate-in">
  <!-- 内容 -->
</div>
```

对于交错的子元素，在父元素上添加 `.stagger-children`：
```html
<div class="stagger-children">
  <div class="animate-in">项目 1</div>
  <div class="animate-in">项目 2</div>
  <div class="animate-in">项目 3</div>
</div>
```

## 7. 导航和进度

### 固定导航栏
- 位置：fixed，顶部，全宽
- 背景：`rgba(250,247,242,0.92)` + `backdrop-filter: blur(8px)`
- 包含：课程标题（左侧）和模块点（右侧）

### 进度条
- 位置：导航栏底部，absolute
- 高度：2px，颜色：accent
- 宽度通过 JS 在滚动时更新

### 导航点
三种视觉状态：
- **默认**：空心圆，柔和边框
- **当前**（`.active`）：填充 accent 颜色 + 发光环
- **已访问**（`.visited`）：填充柔和 accent

悬停时显示模块名称的工具提示。

## 8. 语法高亮（Catppuccin 风格）

所有代码块使用 `--color-bg-code` (#1E1E2E) 背景。

| 令牌类 | 颜色 | 用途 |
|-------------|-------|------|
| `.code-keyword` | `#CBA6F7` | 关键字（const、let、if、return） |
| `.code-string` | `#A6E3A1` | 字符串 |
| `.code-function` | `#89B4FA` | 函数名 |
| `.code-comment` | `#6C7086` | 注释 |
| `.code-number` | `#FAB387` | 数字 |
| `.code-property` | `#F9E2AF` | 对象属性 |
| `.code-operator` | `#94E2D5` | 运算符 |
| `.code-tag` | `#F38BA8` | HTML/JSX 标签 |
| `.code-attr` | `#F9E2AF` | HTML/JSX 属性 |
| `.code-value` | `#A6E3A1` | 属性值 |

## 9. 响应式断点

### 平板（768px）
- 将 `--text-4xl` 缩小到 `1.875rem`，`--text-5xl` 到 `2.25rem`，`--text-6xl` 到 `3rem`
- 翻译块垂直堆叠（单列）
- 模式卡片：2 列

### 移动端（480px）
- 进一步缩小字体令牌
- 模块内边距减少
- 模式卡片：1 列
- 流程图垂直堆叠，箭头旋转 90°
- 导航标题 max-width 减少到 140px

## 10. 滚动条和背景

### 自定义滚动条
- 宽度：6px
- 轨道：透明
- 滑块：`--color-border`，完整圆角

### 大气背景
Body 有微妙的径向渐变叠加：
```css
background-image: radial-gradient(
  ellipse at 20% 50%,
  rgba(217,79,48,0.03) 0%,
  transparent 50%
);
```

## 11. 代码块全局规则

**关键规则：**
- 所有代码块使用 `white-space: pre-wrap`——永远不要水平滚动条
- `word-break: break-word` 用于换行
- 所有 pre/code 元素上 `overflow-x: hidden`
- 翻译代码滚动条通过 `::-webkit-scrollbar { display: none }` 隐藏
- 片段应该是**从真实代码库中逐字复制的准确副本**——永远不要简化或修改
