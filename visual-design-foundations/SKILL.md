---
name: visual-design-foundations
description: 应用排版、色彩理论、间距系统和图标设计原则来创建连贯的视觉设计。适用于建立设计令牌、构建样式指南或改善视觉层次和一致性。
---

# 视觉设计基础

使用排版、颜色、间距和图标基础构建连贯、无障碍的视觉系统。

## 何时使用此技能

- 为新项目建立设计令牌
- 创建或优化间距和尺寸系统
- 选择和搭配字体
- 构建无障碍调色板
- 设计图标系统和视觉资源
- 改善视觉层次和可读性
- 审计设计的视觉一致性
- 实现深色模式或主题化

## 核心系统

### 1. 排版比例

**模块化比例**（基于比例的尺寸）：

```css
:root {
  --font-size-xs: 0.75rem; /* 12px */
  --font-size-sm: 0.875rem; /* 14px */
  --font-size-base: 1rem; /* 16px */
  --font-size-lg: 1.125rem; /* 18px */
  --font-size-xl: 1.25rem; /* 20px */
  --font-size-2xl: 1.5rem; /* 24px */
  --font-size-3xl: 1.875rem; /* 30px */
  --font-size-4xl: 2.25rem; /* 36px */
  --font-size-5xl: 3rem; /* 48px */
}
```

**行高指南**：
| 文本类型 | 行高 |
|-----------|-------------|
| 标题 | 1.1 - 1.3 |
| 正文 | 1.5 - 1.7 |
| UI 标签 | 1.2 - 1.4 |

### 2. 间距系统

**8 点网格**（行业标准）：

```css
:root {
  --space-1: 0.25rem; /* 4px */
  --space-2: 0.5rem; /* 8px */
  --space-3: 0.75rem; /* 12px */
  --space-4: 1rem; /* 16px */
  --space-5: 1.25rem; /* 20px */
  --space-6: 1.5rem; /* 24px */
  --space-8: 2rem; /* 32px */
  --space-10: 2.5rem; /* 40px */
  --space-12: 3rem; /* 48px */
  --space-16: 4rem; /* 64px */
}
```

### 3. 颜色系统

**语义颜色令牌**：

```css
:root {
  /* 品牌 */
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-primary-active: #1e40af;

  /* 语义 */
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-error: #dc2626;
  --color-info: #0891b2;

  /* 中性色 */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
}
```

## 快速开始：在 Tailwind 中使用设计令牌

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.875rem", { lineHeight: "1.25rem" }],
        base: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.125rem", { lineHeight: "1.75rem" }],
        xl: ["1.25rem", { lineHeight: "1.75rem" }],
        "2xl": ["1.5rem", { lineHeight: "2rem" }],
      },
      colors: {
        brand: {
          50: "#eff6ff",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
      },
      spacing: {
        // 使用自定义值扩展默认值
        18: "4.5rem",
        88: "22rem",
      },
    },
  },
};
```

## 排版最佳实践

### 字体搭配

**安全组合**：

- 标题：**Inter** / 正文：**Inter**（单一字体族）
- 标题：**Playfair Display** / 正文：**Source Sans Pro**（对比）
- 标题：**Space Grotesk** / 正文：**IBM Plex Sans**（几何）

### 响应式排版

```css
/* 使用 clamp() 的流体排版 */
h1 {
  font-size: clamp(2rem, 5vw + 1rem, 3.5rem);
  line-height: 1.1;
}

p {
  font-size: clamp(1rem, 2vw + 0.5rem, 1.125rem);
  line-height: 1.6;
  max-width: 65ch; /* 最佳阅读宽度 */
}
```

### 字体加载

```css
/* 防止布局偏移 */
@font-face {
  font-family: "Inter";
  src: url("/fonts/Inter.woff2") format("woff2");
  font-display: swap;
  font-weight: 400 700;
}
```

## 色彩理论

### 对比度要求（WCAG）

| 元素            | 最小比率 |
| ------------------ | ------------- |
| 正文          | 4.5:1 (AA)    |
| 大文本 (18px+) | 3:1 (AA)      |
| UI 组件      | 3:1 (AA)      |
| 增强           | 7:1 (AAA)     |

### 深色模式策略

```css
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --border: #e5e7eb;
}

[data-theme="dark"] {
  --bg-primary: #111827;
  --bg-secondary: #1f2937;
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --border: #374151;
}
```

### 颜色无障碍

```tsx
// 编程式检查对比度
function getContrastRatio(foreground: string, background: string): number {
  const getLuminance = (hex: string) => {
    const rgb = hexToRgb(hex);
    const [r, g, b] = rgb.map((c) => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const l1 = getLuminance(foreground);
  const l2 = getLuminance(background);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);

  return (lighter + 0.05) / (darker + 0.05);
}
```

## 间距指南

### 组件间距

```
卡片内边距:      16-24px (--space-4 to --space-6)
区域间隙:       32-64px (--space-8 to --space-16)
表单字段间隙:    16-24px (--space-4 to --space-6)
按钮内边距:    8-16px 垂直, 16-24px 水平
图标-文本间隙:     8px (--space-2)
```

### 视觉节奏

```css
/* 一致的垂直节奏 */
.prose > * + * {
  margin-top: var(--space-4);
}

.prose > h2 + * {
  margin-top: var(--space-2);
}

.prose > * + h2 {
  margin-top: var(--space-8);
}
```

## 图标设计

### 图标尺寸系统

```css
:root {
  --icon-xs: 12px;
  --icon-sm: 16px;
  --icon-md: 20px;
  --icon-lg: 24px;
  --icon-xl: 32px;
}
```

### 图标组件

```tsx
interface IconProps {
  name: string;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizeMap = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
};

export function Icon({ name, size = "md", className }: IconProps) {
  return (
    <svg
      width={sizeMap[size]}
      height={sizeMap[size]}
      className={cn("inline-block flex-shrink-0", className)}
      aria-hidden="true"
    >
      <use href={`/icons.svg#${name}`} />
    </svg>
  );
}
```

## 最佳实践

1. **建立约束**：限制选择以保持一致性
2. **记录决策**：创建活的样式指南
3. **测试无障碍**：验证对比度、尺寸、触控目标
4. **使用语义令牌**：按用途命名，而非外观
5. **移动优先设计**：从约束开始，增加复杂性
6. **保持垂直节奏**：一致的间距创造和谐
7. **限制字体粗细**：每个字体族 2-3 种粗细就足够了

## 常见问题

- **不一致的间距**：未使用定义的比例
- **对比度差**：未达到 WCAG 要求
- **字体过多**：太多字体族或粗细
- **魔术数字**：任意值而非令牌
- **缺少状态**：忘记悬停、焦点、禁用
- **无深色模式计划**：后期改造比计划更难
