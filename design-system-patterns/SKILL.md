---
name: design-system-patterns
description: 使用设计令牌、主题基础设施和组件架构模式构建可扩展的设计系统。在创建设计令牌、实现主题切换、构建组件库或建立设计系统基础时使用。
---

# 设计系统模式

掌握设计系统架构，为 Web 和移动应用程序创建一致、可维护和可扩展的 UI 基础。

## 何时使用此技能

- 为颜色、排版、间距和阴影创建设计令牌
- 使用 CSS 自定义属性实现亮/暗主题切换
- 构建多品牌主题系统
- 使用一致的 API 架构组件库
- 使用 Figma 令牌建立设计到代码的工作流
- 创建语义令牌层级（原始、语义、组件）
- 设置设计系统文档和指南

## 核心能力

### 1. 设计令牌

- 原始令牌（原始值：颜色、大小、字体）
- 语义令牌（上下文含义：text-primary、surface-elevated）
- 组件令牌（特定用途：button-bg、card-border）
- 令牌命名约定和组织
- 多平台令牌生成（CSS、iOS、Android）

### 2. 主题基础设施

- CSS 自定义属性架构
- React 中的主题上下文提供者
- 动态主题切换
- 系统偏好检测（prefers-color-scheme）
- 持久主题存储
- 减少动效和高对比度模式

### 3. 组件架构

- 复合组件模式
- 多态组件（as prop）
- 变体和尺寸系统
- 基于插槽的组合
- Headless UI 模式
- 样式属性和响应式变体

### 4. 令牌管道

- Figma 到代码同步
- Style Dictionary 配置
- 令牌转换和格式化
- 令牌更新的 CI/CD 集成

## 快速开始

```typescript
// 使用 CSS 自定义属性的设计令牌
const tokens = {
  colors: {
    // 原始令牌
    gray: {
      50: "#fafafa",
      100: "#f5f5f5",
      900: "#171717",
    },
    blue: {
      500: "#3b82f6",
      600: "#2563eb",
    },
  },
  // 语义令牌（引用原始值）
  semantic: {
    light: {
      "text-primary": "var(--color-gray-900)",
      "text-secondary": "var(--color-gray-600)",
      "surface-default": "var(--color-white)",
      "surface-elevated": "var(--color-gray-50)",
      "border-default": "var(--color-gray-200)",
      "interactive-primary": "var(--color-blue-500)",
    },
    dark: {
      "text-primary": "var(--color-gray-50)",
      "text-secondary": "var(--color-gray-400)",
      "surface-default": "var(--color-gray-900)",
      "surface-elevated": "var(--color-gray-800)",
      "border-default": "var(--color-gray-700)",
      "interactive-primary": "var(--color-blue-400)",
    },
  },
};
```

## 关键模式

### 模式 1：令牌层级

```css
/* 第 1 层：原始令牌（原始值） */
:root {
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;
  --color-gray-50: #fafafa;
  --color-gray-900: #171717;

  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;

  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
}

/* 第 2 层：语义令牌（含义） */
:root {
  --text-primary: var(--color-gray-900);
  --text-secondary: var(--color-gray-600);
  --surface-default: white;
  --interactive-primary: var(--color-blue-500);
  --interactive-primary-hover: var(--color-blue-600);
}

/* 第 3 层：组件令牌（特定用途） */
:root {
  --button-bg: var(--interactive-primary);
  --button-bg-hover: var(--interactive-primary-hover);
  --button-text: white;
  --button-radius: var(--radius-md);
  --button-padding-x: var(--space-4);
  --button-padding-y: var(--space-2);
}
```

### 模式 2：使用 React 切换主题

```tsx
import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";

interface ThemeContextValue {
  theme: Theme;
  resolvedTheme: "light" | "dark";
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("theme") as Theme) || "system";
    }
    return "system";
  });

  const [resolvedTheme, setResolvedTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const root = document.documentElement;

    const applyTheme = (isDark: boolean) => {
      root.classList.remove("light", "dark");
      root.classList.add(isDark ? "dark" : "light");
      setResolvedTheme(isDark ? "dark" : "light");
    };

    if (theme === "system") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      applyTheme(mediaQuery.matches);

      const handler = (e: MediaQueryListEvent) => applyTheme(e.matches);
      mediaQuery.addEventListener("change", handler);
      return () => mediaQuery.removeEventListener("change", handler);
    } else {
      applyTheme(theme === "dark");
    }
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useTheme must be used within ThemeProvider");
  return context;
};
```

### 模式 3：使用 CVA 的变体系统

```tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  // 基础样式
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline:
          "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        sm: "h-9 px-3 text-sm",
        md: "h-10 px-4 text-sm",
        lg: "h-11 px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  },
);

interface ButtonProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}
```

### 模式 4：Style Dictionary 配置

```javascript
// style-dictionary.config.js
module.exports = {
  source: ["tokens/**/*.json"],
  platforms: {
    css: {
      transformGroup: "css",
      buildPath: "dist/css/",
      files: [
        {
          destination: "variables.css",
          format: "css/variables",
          options: {
            outputReferences: true, // 保留令牌引用
          },
        },
      ],
    },
    scss: {
      transformGroup: "scss",
      buildPath: "dist/scss/",
      files: [
        {
          destination: "_variables.scss",
          format: "scss/variables",
        },
      ],
    },
    ios: {
      transformGroup: "ios-swift",
      buildPath: "dist/ios/",
      files: [
        {
          destination: "DesignTokens.swift",
          format: "ios-swift/class.swift",
          className: "DesignTokens",
        },
      ],
    },
    android: {
      transformGroup: "android",
      buildPath: "dist/android/",
      files: [
        {
          destination: "colors.xml",
          format: "android/colors",
          filter: { attributes: { category: "color" } },
        },
      ],
    },
  },
};
```

## 最佳实践

1. **按用途命名令牌**：使用语义名称（text-primary）而非视觉描述（dark-gray）
2. **维护令牌层级**：原始 > 语义 > 组件令牌
3. **记录令牌用途**：在令牌定义中包含使用指南
4. **版本化令牌**：将令牌变更视为 API 变更，使用语义版本
5. **测试主题组合**：验证所有主题与所有组件配合工作
6. **自动化令牌管道**：CI/CD 用于 Figma 到代码同步
7. **提供迁移路径**：逐步弃用令牌并提供清晰的替代方案

## 常见问题

- **令牌膨胀**：太多令牌没有清晰的层级
- **命名不一致**：混合约定（camelCase vs kebab-case）
- **缺少暗色模式**：令牌不适应主题变化
- **硬编码值**：使用原始值而非令牌
- **循环引用**：令牌相互引用形成循环
- **平台差距**：某些平台缺少令牌（Web 有但移动端没有）
