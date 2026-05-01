---
name: mobile-android-design
description: 掌握 Material Design 3 和 Jetpack Compose 模式，用于构建原生 Android 应用。当设计 Android 界面、实现 Compose UI 或遵循 Google 的 Material Design 指南时使用。
---

# Android 移动设计

掌握 Material Design 3（Material You）和 Jetpack Compose，构建与 Android 生态系统无缝集成的现代自适应应用。

## 何时使用此技能

- 遵循 Material Design 3 设计 Android 应用界面
- 构建 Jetpack Compose UI 和布局
- 实现 Android 导航模式（Navigation Compose）
- 为手机、平板和折叠屏创建自适应布局
- 使用 Material 3 主题和动态颜色
- 构建无障碍 Android 界面
- 实现 Android 特定的手势和交互
- 为不同屏幕配置进行设计

## 核心概念

### 1. Material Design 3 原则

**个性化**：动态颜色使 UI 适配用户壁纸
**无障碍**：色调调色板确保足够的颜色对比度
**大屏幕**：为平板和折叠屏提供响应式布局

**Material 组件：**

- 卡片、按钮、FAB、Chip
- 导航（导航栏、抽屉、底部导航）
- 文本字段、对话框、底部表单
- 列表、菜单、进度指示器

### 2. Jetpack Compose 布局系统

**Column 和 Row：**

```kotlin
// 带对齐的垂直排列
Column(
    modifier = Modifier.padding(16.dp),
    verticalArrangement = Arrangement.spacedBy(12.dp),
    horizontalAlignment = Alignment.Start
) {
    Text(
        text = "标题",
        style = MaterialTheme.typography.headlineSmall
    )
    Text(
        text = "副标题",
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.onSurfaceVariant
    )
}

// 带权重的水平排列
Row(
    modifier = Modifier.fillMaxWidth(),
    horizontalArrangement = Arrangement.SpaceBetween,
    verticalAlignment = Alignment.CenterVertically
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("精选")
    Spacer(modifier = Modifier.weight(1f))
    TextButton(onClick = {}) {
        Text("查看全部")
    }
}
```

**懒加载列表和网格：**

```kotlin
// 带粘性头部的懒加载列
LazyColumn {
    items.groupBy { it.category }.forEach { (category, categoryItems) ->
        stickyHeader {
            Text(
                text = category,
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(16.dp),
                style = MaterialTheme.typography.titleMedium
            )
        }
        items(categoryItems) { item ->
            ItemRow(item = item)
        }
    }
}

// 自适应网格
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 150.dp),
    contentPadding = PaddingValues(16.dp),
    horizontalArrangement = Arrangement.spacedBy(12.dp),
    verticalArrangement = Arrangement.spacedBy(12.dp)
) {
    items(items) { item ->
        ItemCard(item = item)
    }
}
```

### 3. 导航模式

**底部导航：**

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination

                NavigationDestination.entries.forEach { destination ->
                    NavigationBarItem(
                        icon = { Icon(destination.icon, contentDescription = null) },
                        label = { Text(destination.label) },
                        selected = currentDestination?.hierarchy?.any {
                            it.route == destination.route
                        } == true,
                        onClick = {
                            navController.navigate(destination.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = NavigationDestination.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(NavigationDestination.Home.route) { HomeScreen() }
            composable(NavigationDestination.Search.route) { SearchScreen() }
            composable(NavigationDestination.Profile.route) { ProfileScreen() }
        }
    }
}
```

**导航抽屉：**

```kotlin
@Composable
fun DrawerNavigation() {
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Spacer(Modifier.height(12.dp))
                Text(
                    "应用名称",
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.titleLarge
                )
                HorizontalDivider()

                NavigationDrawerItem(
                    icon = { Icon(Icons.Default.Home, null) },
                    label = { Text("首页") },
                    selected = true,
                    onClick = { scope.launch { drawerState.close() } }
                )
                NavigationDrawerItem(
                    icon = { Icon(Icons.Default.Settings, null) },
                    label = { Text("设置") },
                    selected = false,
                    onClick = { }
                )
            }
        }
    ) {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("首页") },
                    navigationIcon = {
                        IconButton(onClick = { scope.launch { drawerState.open() } }) {
                            Icon(Icons.Default.Menu, contentDescription = "菜单")
                        }
                    }
                )
            }
        ) { innerPadding ->
            Content(modifier = Modifier.padding(innerPadding))
        }
    }
}
```

### 4. Material 3 主题

**颜色方案：**

```kotlin
// 动态颜色（Android 12+）
val dynamicColorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    val context = LocalContext.current
    if (darkTheme) dynamicDarkColorScheme(context)
    else dynamicLightColorScheme(context)
} else {
    if (darkTheme) DarkColorScheme else LightColorScheme
}

// 自定义颜色方案
private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF6750A4),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFEADDFF),
    onPrimaryContainer = Color(0xFF21005D),
    secondary = Color(0xFF625B71),
    onSecondary = Color.White,
    tertiary = Color(0xFF7D5260),
    onTertiary = Color.White,
    surface = Color(0xFFFFFBFE),
    onSurface = Color(0xFF1C1B1F),
)
```

**排版：**

```kotlin
val AppTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 57.sp,
        lineHeight = 64.sp
    ),
    headlineMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 28.sp,
        lineHeight = 36.sp
    ),
    titleLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 22.sp,
        lineHeight = 28.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    labelMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp
    )
)
```

### 5. 组件示例

**卡片：**

```kotlin
@Composable
fun FeatureCard(
    title: String,
    description: String,
    imageUrl: String,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column {
            AsyncImage(
                model = imageUrl,
                contentDescription = null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp),
                contentScale = ContentScale.Crop
            )
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
```

**按钮：**

```kotlin
// 填充按钮（主要操作）
Button(onClick = { }) {
    Text("继续")
}

// 填充色调按钮（次要操作）
FilledTonalButton(onClick = { }) {
    Icon(Icons.Default.Add, null)
    Spacer(Modifier.width(8.dp))
    Text("添加项目")
}

// 轮廓按钮
OutlinedButton(onClick = { }) {
    Text("取消")
}

// 文本按钮
TextButton(onClick = { }) {
    Text("了解更多")
}

// FAB
FloatingActionButton(
    onClick = { },
    containerColor = MaterialTheme.colorScheme.primaryContainer,
    contentColor = MaterialTheme.colorScheme.onPrimaryContainer
) {
    Icon(Icons.Default.Add, contentDescription = "添加")
}
```

## 快速开始组件

```kotlin
@Composable
fun ItemListCard(
    item: Item,
    onItemClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onItemClick,
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.title,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = item.subtitle,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
```

## 最佳实践

1. **使用 Material 主题**：通过 `MaterialTheme.colorScheme` 访问颜色，自动支持深色模式
2. **支持动态颜色**：在 Android 12+ 上启用动态颜色以实现个性化
3. **自适应布局**：使用 `WindowSizeClass` 实现响应式设计
4. **内容描述**：为所有交互元素添加 `contentDescription`
5. **触摸目标**：无障碍要求最小 48dp 触摸目标
6. **状态提升**：提升状态以使组件可复用和可测试
7. **正确使用 remember**：适当使用 `remember` 和 `rememberSaveable`
8. **预览注解**：添加不同配置的 `@Preview`

## 常见问题

- **重组问题**：避免传递不稳定的 lambda；使用 `remember`
- **状态丢失**：对配置更改使用 `rememberSaveable`
- **性能**：长列表使用 `LazyColumn` 而非 `Column`
- **主题泄漏**：确保 `MaterialTheme` 包装所有 composable
- **导航崩溃**：正确处理返回键和深层链接
- **内存泄漏**：在 `DisposableEffect` 中取消协程
