---
name: responsive-design
description: 使用容器查询、流体排版、CSS Grid 和移动优先断点策略实现现代响应式布局。在构建自适应界面、实现流体布局或创建组件级响应行为时使用。
---

# 响应式设计

掌握现代响应式设计技术，创建在所有屏幕尺寸和设备上下文中无缝适配的界面。

## 何时使用此技能

- 实现移动优先的响应式布局
- 使用容器查询实现基于组件的响应式
- 创建流体排版和间距比例
- 使用 CSS Grid 和 Flexbox 构建复杂布局
- 为设计系统设计断点策略
- 实现响应式图片和媒体
- 创建自适应导航模式
- 构建响应式表格和数据展示

## 核心能力

### 1. 容器查询

- 独立于视口的组件级响应式
- 容器查询单位（cqi、cqw、cqh）
- 用于条件样式的样式查询
- 浏览器支持的回退方案

### 2. 流体排版和间距

- CSS clamp() 用于流体缩放
- 视口相对单位（vw、vh、dvh）
- 带最小/最大边界的流体字体比例
- 响应式间距系统

### 3. 布局模式

- CSS Grid 用于二维布局
- Flexbox 用于一维分布
- 内在布局（基于内容的尺寸）
- Subgrid 用于嵌套网格对齐

### 4. 断点策略

- 移动优先媒体查询
- 基于内容的断点
- 设计令牌集成
- 特性查询（@supports）

## 快速参考

### 现代断点比例

```css
/* 移动优先断点 */
/* 基础：移动端（< 640px） */
@media (min-width: 640px) {
  /* sm：横屏手机、小平板 */
}
@media (min-width: 768px) {
  /* md：平板 */
}
@media (min-width: 1024px) {
  /* lg：笔记本、小桌面 */
}
@media (min-width: 1280px) {
  /* xl：桌面 */
}
@media (min-width: 1536px) {
  /* 2xl：大桌面 */
}

/* Tailwind CSS 等效 */
/* sm:  @media (min-width: 640px) */
/* md:  @media (min-width: 768px) */
/* lg:  @media (min-width: 1024px) */
/* xl:  @media (min-width: 1280px) */
/* 2xl: @media (min-width: 1536px) */
```

## 关键模式

### 模式 1：容器查询

```css
/* 定义包含上下文 */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* 查询容器而非视口 */
@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 1rem;
  }

  .card-image {
    aspect-ratio: 1;
  }
}

@container card (min-width: 600px) {
  .card {
    grid-template-columns: 250px 1fr;
  }

  .card-title {
    font-size: 1.5rem;
  }
}

/* 容器查询单位 */
.card-title {
  /* 容器宽度的 5%，限制在 1rem 和 2rem 之间 */
  font-size: clamp(1rem, 5cqi, 2rem);
}
```

```tsx
// 使用容器查询的 React 组件
function ResponsiveCard({ title, image, description }) {
  return (
    <div className="@container">
      <article className="flex flex-col @md:flex-row @md:gap-4">
        <img
          src={image}
          alt=""
          className="w-full @md:w-48 @lg:w-64 aspect-video @md:aspect-square object-cover"
        />
        <div className="p-4 @md:p-0">
          <h2 className="text-lg @md:text-xl @lg:text-2xl font-semibold">
            {title}
          </h2>
          <p className="mt-2 text-muted-foreground @md:line-clamp-3">
            {description}
          </p>
        </div>
      </article>
    </div>
  );
}
```

### 模式 2：流体排版

```css
/* 使用 clamp() 的流体字体比例 */
:root {
  /* 最小尺寸、首选（流体）、最大尺寸 */
  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --text-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg: clamp(1.125rem, 1rem + 0.625vw, 1.25rem);
  --text-xl: clamp(1.25rem, 1rem + 1.25vw, 1.5rem);
  --text-2xl: clamp(1.5rem, 1.25rem + 1.25vw, 2rem);
  --text-3xl: clamp(1.875rem, 1.5rem + 1.875vw, 2.5rem);
  --text-4xl: clamp(2.25rem, 1.75rem + 2.5vw, 3.5rem);
}

/* 使用 */
h1 {
  font-size: var(--text-4xl);
}
h2 {
  font-size: var(--text-3xl);
}
h3 {
  font-size: var(--text-2xl);
}
p {
  font-size: var(--text-base);
}

/* 流体间距比例 */
:root {
  --space-xs: clamp(0.25rem, 0.2rem + 0.25vw, 0.5rem);
  --space-sm: clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-md: clamp(1rem, 0.8rem + 1vw, 1.5rem);
  --space-lg: clamp(1.5rem, 1.2rem + 1.5vw, 2.5rem);
  --space-xl: clamp(2rem, 1.5rem + 2.5vw, 4rem);
}
```

```tsx
// 流体值工具函数
function fluidValue(
  minSize: number,
  maxSize: number,
  minWidth = 320,
  maxWidth = 1280,
) {
  const slope = (maxSize - minSize) / (maxWidth - minWidth);
  const yAxisIntersection = -minWidth * slope + minSize;

  return `clamp(${minSize}rem, ${yAxisIntersection.toFixed(4)}rem + ${(slope * 100).toFixed(4)}vw, ${maxSize}rem)`;
}

// 生成流体字体比例
const fluidTypeScale = {
  sm: fluidValue(0.875, 1),
  base: fluidValue(1, 1.125),
  lg: fluidValue(1.25, 1.5),
  xl: fluidValue(1.5, 2),
  "2xl": fluidValue(2, 3),
};
```

### 模式 3：CSS Grid 响应式布局

```css
/* 自适应网格 - 项目自动换行 */
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
  gap: 1.5rem;
}

/* 自动填充网格 - 保持空列 */
.grid-auto-fill {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

/* 带命名区域的响应式网格 */
.page-layout {
  display: grid;
  grid-template-areas:
    "header"
    "main"
    "sidebar"
    "footer";
  gap: 1rem;
}

@media (min-width: 768px) {
  .page-layout {
    grid-template-columns: 1fr 300px;
    grid-template-areas:
      "header header"
      "main sidebar"
      "footer footer";
  }
}

@media (min-width: 1024px) {
  .page-layout {
    grid-template-columns: 250px 1fr 300px;
    grid-template-areas:
      "header header header"
      "nav main sidebar"
      "footer footer footer";
  }
}

.header {
  grid-area: header;
}
.main {
  grid-area: main;
}
.sidebar {
  grid-area: sidebar;
}
.footer {
  grid-area: footer;
}
```

```tsx
// 响应式网格组件
function ResponsiveGrid({ children, minItemWidth = "250px", gap = "1.5rem" }) {
  return (
    <div
      className="grid"
      style={{
        gridTemplateColumns: `repeat(auto-fit, minmax(min(${minItemWidth}, 100%), 1fr))`,
        gap,
      }}
    >
      {children}
    </div>
  );
}

// 使用 Tailwind 的用法
function ProductGrid({ products }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

### 模式 4：响应式导航

```tsx
function ResponsiveNav({ items }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="relative">
      {/* 移动端菜单按钮 */}
      <button
        className="lg:hidden p-2"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls="nav-menu"
      >
        <span className="sr-only">切换导航</span>
        {isOpen ? <X /> : <Menu />}
      </button>

      {/* 导航链接 */}
      <ul
        id="nav-menu"
        className={cn(
          // 基础：移动端隐藏
          "absolute top-full left-0 right-0 bg-background border-b",
          "flex flex-col",
          // 移动端：滑下
          isOpen ? "flex" : "hidden",
          // 桌面端：始终可见，水平
          "lg:static lg:flex lg:flex-row lg:border-0 lg:bg-transparent",
        )}
      >
        {items.map((item) => (
          <li key={item.href}>
            <a
              href={item.href}
              className={cn(
                "block px-4 py-3",
                "lg:px-3 lg:py-2",
                "hover:bg-muted lg:hover:bg-transparent lg:hover:text-primary",
              )}
            >
              {item.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
```

### 模式 5：响应式图片

```tsx
// 带艺术方向的响应式图片
function ResponsiveHero() {
  return (
    <picture>
      {/* 艺术方向：不同屏幕使用不同裁剪 */}
      <source
        media="(min-width: 1024px)"
        srcSet="/hero-wide.webp"
        type="image/webp"
      />
      <source
        media="(min-width: 768px)"
        srcSet="/hero-medium.webp"
        type="image/webp"
      />
      <source srcSet="/hero-mobile.webp" type="image/webp" />

      {/* 回退 */}
      <img
        src="/hero-mobile.jpg"
        alt="Hero image description"
        className="w-full h-auto"
        loading="eager"
        fetchpriority="high"
      />
    </picture>
  );
}

// 使用 srcset 进行分辨率切换的响应式图片
function ProductImage({ product }) {
  return (
    <img
      src={product.image}
      srcSet={`
        ${product.image}?w=400 400w,
        ${product.image}?w=800 800w,
        ${product.image}?w=1200 1200w
      `}
      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
      alt={product.name}
      className="w-full h-auto object-cover"
      loading="lazy"
    />
  );
}
```

### 模式 6：响应式表格

```tsx
// 带水平滚动的响应式表格
function ResponsiveTable({ data, columns }) {
  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full min-w-[600px]">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="text-left p-3">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="border-t">
              {columns.map((col) => (
                <td key={col.key} className="p-3">
                  {row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// 移动端卡片式表格
function ResponsiveDataTable({ data, columns }) {
  return (
    <>
      {/* 桌面端表格 */}
      <table className="hidden md:table w-full">
        {/* ... 标准表格 */}
      </table>

      {/* 移动端卡片 */}
      <div className="md:hidden space-y-4">
        {data.map((row, i) => (
          <div key={i} className="border rounded-lg p-4 space-y-2">
            {columns.map((col) => (
              <div key={col.key} className="flex justify-between">
                <span className="font-medium text-muted-foreground">
                  {col.label}
                </span>
                <span>{row[col.key]}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </>
  );
}
```

## 视口单位

```css
/* 标准视口单位 */
.full-height {
  height: 100vh; /* 在移动端可能导致问题 */
}

/* 动态视口单位（推荐用于移动端） */
.full-height-dynamic {
  height: 100dvh; /* 考虑移动端浏览器 UI */
}

/* 小视口（最小） */
.min-full-height {
  min-height: 100svh;
}

/* 大视口（最大） */
.max-full-height {
  max-height: 100lvh;
}

/* 视口相对字体大小 */
.hero-title {
  /* 5vw，带最小/最大边界 */
  font-size: clamp(2rem, 5vw, 4rem);
}
```

## 最佳实践

1. **移动优先**：从移动端样式开始，为更大屏幕增强
2. **内容断点**：基于内容而非设备设置断点
3. **流体优于固定**：对排版和间距使用流体值
4. **容器查询**：用于组件级响应式
5. **测试真机**：模拟器无法捕获所有问题
6. **性能**：优化图片，懒加载屏幕外内容
7. **触摸目标**：移动端保持 44x44px 最小尺寸
8. **逻辑属性**：使用 inline/block 以支持国际化

## 常见问题

- **水平溢出**：内容超出视口
- **固定宽度**：使用 px 而非相对单位
- **视口高度**：移动端浏览器上的 100vh 问题
- **字体大小**：移动端文字太小
- **触摸目标**：按钮太小无法准确点击
- **宽高比**：图片被挤压或拉伸
- **Z-Index 堆叠**：覆盖层在不同屏幕上异常
