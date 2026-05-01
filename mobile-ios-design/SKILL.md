---
name: mobile-ios-design
description: 掌握 iOS 人机界面指南和 SwiftUI 模式，用于构建原生 iOS 应用。当设计 iOS 界面、实现 SwiftUI 视图或确保应用遵循 Apple 设计原则时使用。
---

# iOS 移动设计

掌握 iOS 人机界面指南（HIG）和 SwiftUI 模式，构建在 Apple 平台上感觉自然的精美原生 iOS 应用。

## 何时使用此技能

- 遵循 Apple HIG 设计 iOS 应用界面
- 构建 SwiftUI 视图和布局
- 实现 iOS 导航模式（NavigationStack、TabView、sheets）
- 为 iPhone 和 iPad 创建自适应布局
- 使用 SF Symbols 和系统排版
- 构建无障碍 iOS 界面
- 实现 iOS 特定的手势和交互
- 为动态类型和深色模式进行设计

## 核心概念

### 1. 人机界面指南原则

**清晰**：内容清晰易读，图标精确，装饰微妙
**谦逊**：UI 帮助用户理解内容而不与之竞争
**深度**：视觉层次和动效传达层级并支持导航

**平台考量：**

- **iOS**：触控优先，紧凑显示，竖屏方向
- **iPadOS**：更大画布，多任务，指针支持
- **visionOS**：空间计算，眼/手输入

### 2. SwiftUI 布局系统

**基于堆栈的布局：**

```swift
// 带对齐的垂直堆栈
VStack(alignment: .leading, spacing: 12) {
    Text("标题")
        .font(.headline)
    Text("副标题")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}

// 带弹性间距的水平堆栈
HStack {
    Image(systemName: "star.fill")
    Text("精选")
    Spacer()
    Text("查看全部")
        .foregroundStyle(.blue)
}
```

**网格布局：**

```swift
// 填充可用宽度的自适应网格
LazyVGrid(columns: [
    GridItem(.adaptive(minimum: 150, maximum: 200))
], spacing: 16) {
    ForEach(items) { item in
        ItemCard(item: item)
    }
}

// 固定列网格
LazyVGrid(columns: [
    GridItem(.flexible()),
    GridItem(.flexible()),
    GridItem(.flexible())
], spacing: 12) {
    ForEach(items) { item in
        ItemThumbnail(item: item)
    }
}
```

### 3. 导航模式

**NavigationStack（iOS 16+）：**

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: item) {
                    ItemRow(item: item)
                }
            }
            .navigationTitle("项目")
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
        }
    }
}
```

**TabView（iOS 18+）：**

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            Tab("首页", systemImage: "house", value: 0) {
                HomeView()
            }

            Tab("搜索", systemImage: "magnifyingglass", value: 1) {
                SearchView()
            }

            Tab("个人", systemImage: "person", value: 2) {
                ProfileView()
            }
        }
    }
}
```

### 4. 系统集成

**SF Symbols：**

```swift
// 基本符号
Image(systemName: "heart.fill")
    .foregroundStyle(.red)

// 带渲染模式的符号
Image(systemName: "cloud.sun.fill")
    .symbolRenderingMode(.multicolor)

// 可变符号（iOS 16+）
Image(systemName: "speaker.wave.3.fill", variableValue: volume)

// 符号动效（iOS 17+）
Image(systemName: "bell.fill")
    .symbolEffect(.bounce, value: notificationCount)
```

**动态类型：**

```swift
// 使用语义字体
Text("标题")
    .font(.headline)

// 随用户偏好缩放的正文文本
Text("随用户偏好缩放的正文文本")
    .font(.body)

// 尊重动态类型的自定义字体
Text("自定义")
    .font(.custom("Avenir", size: 17, relativeTo: .body))
```

### 5. 视觉设计

**颜色和材质：**

```swift
// 适配深色/浅色模式的语义颜色
Text("主要")
    .foregroundStyle(.primary)
Text("次要")
    .foregroundStyle(.secondary)

// 模糊效果的系统材质
Rectangle()
    .fill(.ultraThinMaterial)
    .frame(height: 100)

// 叠加层的鲜艳材质
Text("叠加层")
    .padding()
    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
```

**阴影和深度：**

```swift
// 标准卡片阴影
RoundedRectangle(cornerRadius: 16)
    .fill(.background)
    .shadow(color: .black.opacity(0.1), radius: 8, y: 4)

// 浮起效果
.shadow(radius: 2, y: 1)
.shadow(radius: 8, y: 4)
```

## 快速开始组件

```swift
import SwiftUI

struct FeatureCard: View {
    let title: String
    let description: String
    let systemImage: String

    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: systemImage)
                .font(.title)
                .foregroundStyle(.blue)
                .frame(width: 44, height: 44)
                .background(.blue.opacity(0.1), in: Circle())

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(description)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }

            Spacer()

            Image(systemName: "chevron.right")
                .foregroundStyle(.tertiary)
        }
        .padding()
        .background(.background, in: RoundedRectangle(cornerRadius: 12))
        .shadow(color: .black.opacity(0.05), radius: 4, y: 2)
    }
}
```

## 最佳实践

1. **使用语义颜色**：始终使用 `.primary`、`.secondary`、`.background` 以自动支持深色/浅色模式
2. **拥抱 SF Symbols**：使用系统符号以保持一致性和自动无障碍支持
3. **支持动态类型**：使用语义字体（`.body`、`.headline`）而非固定大小
4. **添加无障碍支持**：包含 `.accessibilityLabel()` 和 `.accessibilityHint()` 修饰符
5. **使用安全区域**：尊重 `safeAreaInset`，避免在屏幕边缘硬编码边距
6. **实现状态恢复**：使用 `@SceneStorage` 保留用户状态
7. **支持 iPad 多任务**：为分屏视图和侧拉进行设计
8. **在真机上测试**：模拟器无法完全捕捉触觉和性能体验

## 常见问题

- **布局破坏**：谨慎使用 `.fixedSize()`；优先使用弹性布局
- **性能问题**：长滚动列表使用 `LazyVStack`/`LazyHStack`
- **导航 Bug**：确保 `NavigationLink` 值是 `Hashable` 的
- **深色模式问题**：避免硬编码颜色；使用语义或资源目录颜色
- **无障碍失败**：启用 VoiceOver 进行测试
- **内存泄漏**：注意闭包中的强引用循环
