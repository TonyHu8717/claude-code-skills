---
name: web-component-design
description: 掌握 React、Vue 和 Svelte 组件模式，包括 CSS-in-JS、组合策略和可复用组件架构。适用于构建 UI 组件库、设计组件 API 或实现前端设计系统。
---

# Web 组件设计

使用现代框架和清晰的组合模式及样式方法构建可复用、可维护的 UI 组件。

## 何时使用此技能

- 设计可复用的组件库或设计系统
- 实现复杂的组件组合模式
- 选择和应用 CSS-in-JS 解决方案
- 构建无障碍、响应式的 UI 组件
- 在代码库中创建一致的组件 API
- 将遗留组件重构为现代模式
- 实现复合组件或渲染属性

## 核心概念

### 1. 组件组合模式

**复合组件**：协同工作的相关组件

```tsx
// 使用方式
<Select value={value} onChange={setValue}>
  <Select.Trigger>Choose option</Select.Trigger>
  <Select.Options>
    <Select.Option value="a">Option A</Select.Option>
    <Select.Option value="b">Option B</Select.Option>
  </Select.Options>
</Select>
```

**渲染属性**：将渲染委托给父组件

```tsx
<DataFetcher url="/api/users">
  {({ data, loading, error }) =>
    loading ? <Spinner /> : <UserList users={data} />
  }
</DataFetcher>
```

**插槽（Vue/Svelte）**：命名的内容注入点

```vue
<template>
  <Card>
    <template #header>Title</template>
    <template #content>Body text</template>
    <template #footer><Button>Action</Button></template>
  </Card>
</template>
```

### 2. CSS-in-JS 方法

| 方案              | 方法               | 最适合                          |
| --------------------- | ---------------------- | --------------------------------- |
| **Tailwind CSS**      | 实用类        | 快速原型、设计系统 |
| **CSS Modules**       | 作用域 CSS 文件       | 现有 CSS、渐进采用    |
| **styled-components** | 模板字面量      | React、动态样式            |
| **Emotion**           | 对象/模板样式 | 灵活、SSR 友好            |
| **Vanilla Extract**   | 零运行时           | 性能关键应用         |

### 3. 组件 API 设计

```tsx
interface ButtonProps {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  isDisabled?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
}
```

**原则**：

- 使用语义化的属性名（`isLoading` vs `loading`）
- 提供合理的默认值
- 通过 `children` 支持组合
- 通过 `className` 或 `style` 允许样式覆盖

## 快速开始：使用 Tailwind 的 React 组件

```tsx
import { forwardRef, type ComponentPropsWithoutRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-blue-600 text-white hover:bg-blue-700",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
        ghost: "hover:bg-gray-100 hover:text-gray-900",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

interface ButtonProps
  extends
    ComponentPropsWithoutRef<"button">,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, children, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading && <Spinner className="mr-2 h-4 w-4" />}
      {children}
    </button>
  ),
);
Button.displayName = "Button";
```

## 框架模式

### React：复合组件

```tsx
import { createContext, useContext, useState, type ReactNode } from "react";

interface AccordionContextValue {
  openItems: Set<string>;
  toggle: (id: string) => void;
}

const AccordionContext = createContext<AccordionContextValue | null>(null);

function useAccordion() {
  const context = useContext(AccordionContext);
  if (!context) throw new Error("Must be used within Accordion");
  return context;
}

export function Accordion({ children }: { children: ReactNode }) {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setOpenItems((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <AccordionContext.Provider value={{ openItems, toggle }}>
      <div className="divide-y">{children}</div>
    </AccordionContext.Provider>
  );
}

Accordion.Item = function AccordionItem({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: ReactNode;
}) {
  const { openItems, toggle } = useAccordion();
  const isOpen = openItems.has(id);

  return (
    <div>
      <button onClick={() => toggle(id)} className="w-full text-left py-3">
        {title}
      </button>
      {isOpen && <div className="pb-3">{children}</div>}
    </div>
  );
};
```

### Vue 3：组合式函数

```vue
<script setup lang="ts">
import { ref, computed, provide, inject, type InjectionKey } from "vue";

interface TabsContext {
  activeTab: Ref<string>;
  setActive: (id: string) => void;
}

const TabsKey: InjectionKey<TabsContext> = Symbol("tabs");

// 父组件
const activeTab = ref("tab-1");
provide(TabsKey, {
  activeTab,
  setActive: (id: string) => {
    activeTab.value = id;
  },
});

// 子组件使用
const tabs = inject(TabsKey);
const isActive = computed(() => tabs?.activeTab.value === props.id);
</script>
```

### Svelte 5：Runes

```svelte
<script lang="ts">
  interface Props {
    variant?: 'primary' | 'secondary';
    size?: 'sm' | 'md' | 'lg';
    onclick?: () => void;
    children: import('svelte').Snippet;
  }

  let { variant = 'primary', size = 'md', onclick, children }: Props = $props();

  const classes = $derived(
    `btn btn-${variant} btn-${size}`
  );
</script>

<button class={classes} {onclick}>
  {@render children()}
</button>
```

## 最佳实践

1. **单一职责**：每个组件做好一件事
2. **防止属性钻取**：对深层嵌套数据使用上下文
3. **默认无障碍**：包含 ARIA 属性、键盘支持
4. **受控 vs 非受控**：适当时支持两种模式
5. **转发 Ref**：允许父组件访问 DOM 节点
6. **记忆化**：对昂贵的渲染使用 `React.memo`、`useMemo`
7. **错误边界**：包裹可能失败的组件

## 常见问题

- **属性爆炸**：属性太多——考虑使用组合代替
- **样式冲突**：使用作用域样式或 CSS Modules
- **重渲染级联**：使用 React DevTools 分析，适当记忆化
- **无障碍差距**：使用屏幕阅读器和键盘导航测试
- **包大小**：树摇未使用的组件变体
