---
name: nextjs-app-router-patterns
description: 掌握 Next.js 14+ App Router，包括服务器组件、流式传输、并行路由和高级数据获取。在构建 Next.js 应用、实现 SSR/SSG 或优化 React 服务器组件时使用。
---

# Next.js App Router 模式

Next.js 14+ App Router 架构、服务器组件和现代全栈 React 开发的综合模式。

## 何时使用此技能

- 使用 App Router 构建新的 Next.js 应用
- 从 Pages Router 迁移到 App Router
- 实现服务器组件和流式传输
- 设置并行和拦截路由
- 优化数据获取和缓存
- 使用 Server Actions 构建全栈功能

## 核心概念

### 1. 渲染模式

| 模式             | 位置         | 何时使用                               |
| ---------------- | ------------ | -------------------------------------- |
| **服务器组件**   | 仅服务器     | 数据获取、重计算、密钥                 |
| **客户端组件**   | 浏览器       | 交互性、hooks、浏览器 API              |
| **静态**         | 构建时       | 很少变化的内容                         |
| **动态**         | 请求时       | 个性化或实时数据                       |
| **流式传输**     | 渐进式       | 大页面、慢数据源                       |

### 2. 文件约定

```
app/
├── layout.tsx       # 共享 UI 包装器
├── page.tsx         # 路由 UI
├── loading.tsx      # 加载 UI（Suspense）
├── error.tsx        # 错误边界
├── not-found.tsx    # 404 UI
├── route.ts         # API 端点
├── template.tsx     # 重新挂载的布局
├── default.tsx      # 并行路由回退
└── opengraph-image.tsx  # OG 图片生成
```

## 快速开始

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: { default: 'My App', template: '%s | My App' },
  description: 'Built with Next.js App Router',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

// app/page.tsx - 默认为服务器组件
async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 }, // ISR：每小时重新验证
  })
  return res.json()
}

export default async function HomePage() {
  const products = await getProducts()

  return (
    <main>
      <h1>Products</h1>
      <ProductGrid products={products} />
    </main>
  )
}
```

## 模式

### 模式 1：带数据获取的服务器组件

```typescript
// app/products/page.tsx
import { Suspense } from 'react'
import { ProductList, ProductListSkeleton } from '@/components/products'
import { FilterSidebar } from '@/components/filters'

interface SearchParams {
  category?: string
  sort?: 'price' | 'name' | 'date'
  page?: string
}

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>
}) {
  const params = await searchParams

  return (
    <div className="flex gap-8">
      <FilterSidebar />
      <Suspense
        key={JSON.stringify(params)}
        fallback={<ProductListSkeleton />}
      >
        <ProductList
          category={params.category}
          sort={params.sort}
          page={Number(params.page) || 1}
        />
      </Suspense>
    </div>
  )
}

// components/products/ProductList.tsx - 服务器组件
async function getProducts(filters: ProductFilters) {
  const res = await fetch(
    `${process.env.API_URL}/products?${new URLSearchParams(filters)}`,
    { next: { tags: ['products'] } }
  )
  if (!res.ok) throw new Error('Failed to fetch products')
  return res.json()
}

export async function ProductList({ category, sort, page }: ProductFilters) {
  const { products, totalPages } = await getProducts({ category, sort, page })

  return (
    <div>
      <div className="grid grid-cols-3 gap-4">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
      <Pagination currentPage={page} totalPages={totalPages} />
    </div>
  )
}
```

### 模式 2：带 'use client' 的客户端组件

```typescript
// components/products/AddToCartButton.tsx
'use client'

import { useState, useTransition } from 'react'
import { addToCart } from '@/app/actions/cart'

export function AddToCartButton({ productId }: { productId: string }) {
  const [isPending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)

  const handleClick = () => {
    setError(null)
    startTransition(async () => {
      const result = await addToCart(productId)
      if (result.error) {
        setError(result.error)
      }
    })
  }

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={isPending}
        className="btn-primary"
      >
        {isPending ? 'Adding...' : 'Add to Cart'}
      </button>
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  )
}
```

### 模式 3：Server Actions

```typescript
// app/actions/cart.ts
"use server";

import { revalidateTag } from "next/cache";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function addToCart(productId: string) {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get("session")?.value;

  if (!sessionId) {
    redirect("/login");
  }

  try {
    await db.cart.upsert({
      where: { sessionId_productId: { sessionId, productId } },
      update: { quantity: { increment: 1 } },
      create: { sessionId, productId, quantity: 1 },
    });

    revalidateTag("cart");
    return { success: true };
  } catch (error) {
    return { error: "Failed to add item to cart" };
  }
}

export async function checkout(formData: FormData) {
  const address = formData.get("address") as string;
  const payment = formData.get("payment") as string;

  // 验证
  if (!address || !payment) {
    return { error: "Missing required fields" };
  }

  // 处理订单
  const order = await processOrder({ address, payment });

  // 重定向到确认页
  redirect(`/orders/${order.id}/confirmation`);
}
```

### 模式 4：并行路由

```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <div className="dashboard-grid">
      <main>{children}</main>
      <aside className="analytics-panel">{analytics}</aside>
      <aside className="team-panel">{team}</aside>
    </div>
  )
}

// app/dashboard/@analytics/page.tsx
export default async function AnalyticsSlot() {
  const stats = await getAnalytics()
  return <AnalyticsChart data={stats} />
}

// app/dashboard/@analytics/loading.tsx
export default function AnalyticsLoading() {
  return <ChartSkeleton />
}

// app/dashboard/@team/page.tsx
export default async function TeamSlot() {
  const members = await getTeamMembers()
  return <TeamList members={members} />
}
```

### 模式 5：拦截路由（模态框模式）

```typescript
// 照片模态框的文件结构
// app/
// ├── @modal/
// │   ├── (.)photos/[id]/page.tsx  # 拦截
// │   └── default.tsx
// ├── photos/
// │   └── [id]/page.tsx            # 完整页面
// └── layout.tsx

// app/@modal/(.)photos/[id]/page.tsx
import { Modal } from '@/components/Modal'
import { PhotoDetail } from '@/components/PhotoDetail'

export default async function PhotoModal({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const photo = await getPhoto(id)

  return (
    <Modal>
      <PhotoDetail photo={photo} />
    </Modal>
  )
}

// app/photos/[id]/page.tsx - 完整页面版本
export default async function PhotoPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const photo = await getPhoto(id)

  return (
    <div className="photo-page">
      <PhotoDetail photo={photo} />
      <RelatedPhotos photoId={id} />
    </div>
  )
}

// app/layout.tsx
export default function RootLayout({
  children,
  modal,
}: {
  children: React.ReactNode
  modal: React.ReactNode
}) {
  return (
    <html>
      <body>
        {children}
        {modal}
      </body>
    </html>
  )
}
```

### 模式 6：使用 Suspense 的流式传输

```typescript
// app/product/[id]/page.tsx
import { Suspense } from 'react'

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  // 此数据首先加载（阻塞）
  const product = await getProduct(id)

  return (
    <div>
      {/* 立即渲染 */}
      <ProductHeader product={product} />

      {/* 流式加载评论 */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews productId={id} />
      </Suspense>

      {/* 流式加载推荐 */}
      <Suspense fallback={<RecommendationsSkeleton />}>
        <Recommendations productId={id} />
      </Suspense>
    </div>
  )
}

// 这些组件获取自己的数据
async function Reviews({ productId }: { productId: string }) {
  const reviews = await getReviews(productId) // 慢 API
  return <ReviewList reviews={reviews} />
}

async function Recommendations({ productId }: { productId: string }) {
  const products = await getRecommendations(productId) // 基于 ML，慢
  return <ProductCarousel products={products} />
}
```

### 模式 7：路由处理器（API 路由）

```typescript
// app/api/products/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const category = searchParams.get("category");

  const products = await db.product.findMany({
    where: category ? { category } : undefined,
    take: 20,
  });

  return NextResponse.json(products);
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  const product = await db.product.create({
    data: body,
  });

  return NextResponse.json(product, { status: 201 });
}

// app/api/products/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const product = await db.product.findUnique({ where: { id } });

  if (!product) {
    return NextResponse.json({ error: "Product not found" }, { status: 404 });
  }

  return NextResponse.json(product);
}
```

### 模式 8：元数据和 SEO

```typescript
// app/products/[slug]/page.tsx
import { Metadata } from 'next'
import { notFound } from 'next/navigation'

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const product = await getProduct(slug)

  if (!product) return {}

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [{ url: product.image, width: 1200, height: 630 }],
    },
    twitter: {
      card: 'summary_large_image',
      title: product.name,
      description: product.description,
      images: [product.image],
    },
  }
}

export async function generateStaticParams() {
  const products = await db.product.findMany({ select: { slug: true } })
  return products.map((p) => ({ slug: p.slug }))
}

export default async function ProductPage({ params }: Props) {
  const { slug } = await params
  const product = await getProduct(slug)

  if (!product) notFound()

  return <ProductDetail product={product} />
}
```

## 缓存策略

### 数据缓存

```typescript
// 不缓存（始终最新）
fetch(url, { cache: "no-store" });

// 永久缓存（静态）
fetch(url, { cache: "force-cache" });

// ISR - 60 秒后重新验证
fetch(url, { next: { revalidate: 60 } });

// 基于标签的失效
fetch(url, { next: { tags: ["products"] } });

// 通过 Server Action 失效
("use server");
import { revalidateTag, revalidatePath } from "next/cache";

export async function updateProduct(id: string, data: ProductData) {
  await db.product.update({ where: { id }, data });
  revalidateTag("products");
  revalidatePath("/products");
}
```

## 最佳实践

### 推荐做法

- **从服务器组件开始** - 仅在需要时添加 'use client'
- **就近获取数据** - 在使用数据的地方获取
- **使用 Suspense 边界** - 为慢数据启用流式传输
- **利用并行路由** - 独立的加载状态
- **使用 Server Actions** - 用于带渐进增强的变更

### 避免做法

- **不要传递可序列化数据** - 服务器 → 客户端边界限制
- **不要在服务器组件中使用 hooks** - 没有 useState、useEffect
- **不要在客户端组件中获取数据** - 使用服务器组件或 React Query
- **不要过度嵌套布局** - 每个布局都增加组件树
- **不要忽略加载状态** - 始终提供 loading.tsx 或 Suspense
