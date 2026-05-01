---
name: react-native-architecture
description: 使用 Expo、导航、原生模块、离线同步和跨平台模式构建生产级 React Native 应用。在开发移动应用、实现原生集成或架构 React Native 项目时使用。
---

# React Native 架构

使用 Expo 进行 React Native 开发的生产就绪模式，包括导航、状态管理、原生模块和离线优先架构。

## 何时使用此技能

- 启动新的 React Native 或 Expo 项目
- 实现复杂导航模式
- 集成原生模块和平台 API
- 构建离线优先移动应用
- 优化 React Native 性能
- 设置移动发布的 CI/CD

## 核心概念

### 1. 项目结构

```
src/
├── app/                    # Expo Router 屏幕
│   ├── (auth)/            # 认证组
│   ├── (tabs)/            # 标签导航
│   └── _layout.tsx        # 根布局
├── components/
│   ├── ui/                # 可复用 UI 组件
│   └── features/          # 功能特定组件
├── hooks/                 # 自定义 hooks
├── services/              # API 和原生服务
├── stores/                # 状态管理
├── utils/                 # 工具函数
└── types/                 # TypeScript 类型
```

### 2. Expo vs Bare React Native

| 功能            | Expo           | Bare RN        |
| ------------------ | -------------- | -------------- |
| 设置复杂度   | 低            | 高           |
| 原生模块     | EAS Build      | 手动链接 |
| OTA 更新        | 内置       | 手动设置   |
| 构建服务      | EAS            | 自定义 CI      |
| 自定义原生代码 | 配置插件 | 直接访问  |

## 快速开始

```bash
# 创建新 Expo 项目
npx create-expo-app@latest my-app -t expo-template-blank-typescript

# 安装核心依赖
npx expo install expo-router expo-status-bar react-native-safe-area-context
npx expo install @react-native-async-storage/async-storage
npx expo install expo-secure-store expo-haptics
```

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router'
import { ThemeProvider } from '@/providers/ThemeProvider'
import { QueryProvider } from '@/providers/QueryProvider'

export default function RootLayout() {
  return (
    <QueryProvider>
      <ThemeProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
        </Stack>
      </ThemeProvider>
    </QueryProvider>
  )
}
```

## 模式

### 模式 1：Expo Router 导航

```typescript
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router'
import { Home, Search, User, Settings } from 'lucide-react-native'
import { useTheme } from '@/hooks/useTheme'

export default function TabLayout() {
  const { colors } = useTheme()

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: { backgroundColor: colors.background },
        headerShown: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => <Home size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="search"
        options={{
          title: 'Search',
          tabBarIcon: ({ color, size }) => <Search size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => <User size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: 'Settings',
          tabBarIcon: ({ color, size }) => <Settings size={size} color={color} />,
        }}
      />
    </Tabs>
  )
}

// app/(tabs)/profile/[id].tsx - 动态路由
import { useLocalSearchParams } from 'expo-router'

export default function ProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()

  return <UserProfile userId={id} />
}

// 从任意位置导航
import { router } from 'expo-router'

// 编程式导航
router.push('/profile/123')
router.replace('/login')
router.back()

// 带参数
router.push({
  pathname: '/product/[id]',
  params: { id: '123', referrer: 'home' },
})
```

### 模式 2：认证流程

```typescript
// providers/AuthProvider.tsx
import { createContext, useContext, useEffect, useState } from 'react'
import { useRouter, useSegments } from 'expo-router'
import * as SecureStore from 'expo-secure-store'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  signIn: (credentials: Credentials) => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const segments = useSegments()
  const router = useRouter()

  // 挂载时检查认证
  useEffect(() => {
    checkAuth()
  }, [])

  // 保护路由
  useEffect(() => {
    if (isLoading) return

    const inAuthGroup = segments[0] === '(auth)'

    if (!user && !inAuthGroup) {
      router.replace('/login')
    } else if (user && inAuthGroup) {
      router.replace('/(tabs)')
    }
  }, [user, segments, isLoading])

  async function checkAuth() {
    try {
      const token = await SecureStore.getItemAsync('authToken')
      if (token) {
        const userData = await api.getUser(token)
        setUser(userData)
      }
    } catch (error) {
      await SecureStore.deleteItemAsync('authToken')
    } finally {
      setIsLoading(false)
    }
  }

  async function signIn(credentials: Credentials) {
    const { token, user } = await api.login(credentials)
    await SecureStore.setItemAsync('authToken', token)
    setUser(user)
  }

  async function signOut() {
    await SecureStore.deleteItemAsync('authToken')
    setUser(null)
  }

  if (isLoading) {
    return <SplashScreen />
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
```

### 模式 3：使用 React Query 的离线优先

```typescript
// providers/QueryProvider.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister'
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client'
import AsyncStorage from '@react-native-async-storage/async-storage'
import NetInfo from '@react-native-community/netinfo'
import { onlineManager } from '@tanstack/react-query'

// 同步在线状态
onlineManager.setEventListener((setOnline) => {
  return NetInfo.addEventListener((state) => {
    setOnline(!!state.isConnected)
  })
})

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 1000 * 60 * 60 * 24, // 24 小时
      staleTime: 1000 * 60 * 5, // 5 分钟
      retry: 2,
      networkMode: 'offlineFirst',
    },
    mutations: {
      networkMode: 'offlineFirst',
    },
  },
})

const asyncStoragePersister = createAsyncStoragePersister({
  storage: AsyncStorage,
  key: 'REACT_QUERY_OFFLINE_CACHE',
})

export function QueryProvider({ children }: { children: React.ReactNode }) {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister: asyncStoragePersister }}
    >
      {children}
    </PersistQueryClientProvider>
  )
}

// hooks/useProducts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: api.getProducts,
    // 重新验证时使用过期数据
    placeholderData: (previousData) => previousData,
  })
}

export function useCreateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.createProduct,
    // 乐观更新
    onMutate: async (newProduct) => {
      await queryClient.cancelQueries({ queryKey: ['products'] })
      const previous = queryClient.getQueryData(['products'])

      queryClient.setQueryData(['products'], (old: Product[]) => [
        ...old,
        { ...newProduct, id: 'temp-' + Date.now() },
      ])

      return { previous }
    },
    onError: (err, newProduct, context) => {
      queryClient.setQueryData(['products'], context?.previous)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}
```

### 模式 4：原生模块集成

```typescript
// services/haptics.ts
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

export const haptics = {
  light: () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  },
  medium: () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
  },
  heavy: () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    }
  },
  success: () => {
    if (Platform.OS !== "web") {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  },
  error: () => {
    if (Platform.OS !== "web") {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  },
};

// services/biometrics.ts
import * as LocalAuthentication from "expo-local-authentication";

export async function authenticateWithBiometrics(): Promise<boolean> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  if (!hasHardware) return false;

  const isEnrolled = await LocalAuthentication.isEnrolledAsync();
  if (!isEnrolled) return false;

  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Authenticate to continue",
    fallbackLabel: "Use passcode",
    disableDeviceFallback: false,
  });

  return result.success;
}

// services/notifications.ts
import * as Notifications from "expo-notifications";
import { Platform } from "react-native";
import Constants from "expo-constants";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications() {
  let token: string | undefined;

  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
    });
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== "granted") {
    return null;
  }

  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  token = (await Notifications.getExpoPushTokenAsync({ projectId })).data;

  return token;
}
```

### 模式 5：平台特定代码

```typescript
// components/ui/Button.tsx
import { Platform, Pressable, StyleSheet, Text, ViewStyle } from 'react-native'
import * as Haptics from 'expo-haptics'
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from 'react-native-reanimated'

const AnimatedPressable = Animated.createAnimatedComponent(Pressable)

interface ButtonProps {
  title: string
  onPress: () => void
  variant?: 'primary' | 'secondary' | 'outline'
  disabled?: boolean
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
}: ButtonProps) {
  const scale = useSharedValue(1)

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }))

  const handlePressIn = () => {
    scale.value = withSpring(0.95)
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
    }
  }

  const handlePressOut = () => {
    scale.value = withSpring(1)
  }

  return (
    <AnimatedPressable
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={disabled}
      style={[
        styles.button,
        styles[variant],
        disabled && styles.disabled,
        animatedStyle,
      ]}
    >
      <Text style={[styles.text, styles[`${variant}Text`]]}>{title}</Text>
    </AnimatedPressable>
  )
}

// 平台特定文件
// Button.ios.tsx - iOS 特定实现
// Button.android.tsx - Android 特定实现
// Button.web.tsx - Web 特定实现

// 或使用 Platform.select
const styles = StyleSheet.create({
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  primary: {
    backgroundColor: '#007AFF',
  },
  secondary: {
    backgroundColor: '#5856D6',
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    fontSize: 16,
    fontWeight: '600',
  },
  primaryText: {
    color: '#FFFFFF',
  },
  secondaryText: {
    color: '#FFFFFF',
  },
  outlineText: {
    color: '#007AFF',
  },
})
```

### 模式 6：性能优化

```typescript
// components/ProductList.tsx
import { FlashList } from '@shopify/flash-list'
import { memo, useCallback } from 'react'

interface ProductListProps {
  products: Product[]
  onProductPress: (id: string) => void
}

// 缓存列表项
const ProductItem = memo(function ProductItem({
  item,
  onPress,
}: {
  item: Product
  onPress: (id: string) => void
}) {
  const handlePress = useCallback(() => onPress(item.id), [item.id, onPress])

  return (
    <Pressable onPress={handlePress} style={styles.item}>
      <FastImage
        source={{ uri: item.image }}
        style={styles.image}
        resizeMode="cover"
      />
      <Text style={styles.title}>{item.name}</Text>
      <Text style={styles.price}>${item.price}</Text>
    </Pressable>
  )
})

export function ProductList({ products, onProductPress }: ProductListProps) {
  const renderItem = useCallback(
    ({ item }: { item: Product }) => (
      <ProductItem item={item} onPress={onProductPress} />
    ),
    [onProductPress]
  )

  const keyExtractor = useCallback((item: Product) => item.id, [])

  return (
    <FlashList
      data={products}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      estimatedItemSize={100}
      // 性能优化
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={5}
      // 下拉刷新
      onRefresh={onRefresh}
      refreshing={isRefreshing}
    />
  )
}
```

## EAS Build 和 Submit

```json
// eas.json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": {
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "production": {
      "autoIncrement": true
    }
  },
  "submit": {
    "production": {
      "ios": { "appleId": "your@email.com", "ascAppId": "123456789" },
      "android": { "serviceAccountKeyPath": "./google-services.json" }
    }
  }
}
```

```bash
# 构建命令
eas build --platform ios --profile development
eas build --platform android --profile preview
eas build --platform all --profile production

# 提交到商店
eas submit --platform ios
eas submit --platform android

# OTA 更新
eas update --branch production --message "Bug fixes"
```

## 最佳实践

### 推荐

- **使用 Expo** - 更快的开发、OTA 更新、托管原生代码
- **FlashList 优于 FlatList** - 长列表性能更好
- **缓存组件** - 防止不必要的重新渲染
- **使用 Reanimated** - 原生线程上的 60fps 动画
- **在真机上测试** - 模拟器会遗漏真实世界的问题

### 避免

- **不要内联样式** - 使用 StyleSheet.create 以获得更好性能
- **不要在渲染中获取数据** - 使用 useEffect 或 React Query
- **不要忽略平台差异** - 在 iOS 和 Android 上都测试
- **不要在代码中存储密钥** - 使用环境变量
- **不要跳过错误边界** - 移动端崩溃是不可原谅的
