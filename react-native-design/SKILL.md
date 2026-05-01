---
name: react-native-design
description: 掌握 React Native 样式、导航和 Reanimated 动画，用于跨平台移动开发。在构建 React Native 应用、实现导航模式或创建高性能动画时使用。
---

# React Native 设计

掌握 React Native 样式模式、React Navigation 和 Reanimated 3，构建具有原生质量用户体验的高性能跨平台移动应用。

## 何时使用此技能

- 使用 React Native 构建跨平台移动应用
- 使用 React Navigation 6+ 实现导航
- 使用 Reanimated 3 创建高性能动画
- 使用 StyleSheet 和 styled-components 为组件设置样式
- 为不同屏幕尺寸构建响应式布局
- 实现平台特定设计（iOS/Android）
- 使用 Gesture Handler 创建手势驱动的交互
- 优化 React Native 性能

## 核心概念

### 1. StyleSheet 和样式

**基本 StyleSheet：**

```typescript
import { StyleSheet, View, Text } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    lineHeight: 24,
  },
});

function Card() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Title</Text>
      <Text style={styles.subtitle}>Subtitle text</Text>
    </View>
  );
}
```

**动态样式：**

```typescript
interface CardProps {
  variant: 'primary' | 'secondary';
  disabled?: boolean;
}

function Card({ variant, disabled }: CardProps) {
  return (
    <View style={[
      styles.card,
      variant === 'primary' ? styles.primary : styles.secondary,
      disabled && styles.disabled,
    ]}>
      <Text style={styles.text}>Content</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 16,
    borderRadius: 12,
  },
  primary: {
    backgroundColor: '#6366f1',
  },
  secondary: {
    backgroundColor: '#f3f4f6',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    fontSize: 16,
  },
});
```

### 2. Flexbox 布局

**行和列布局：**

```typescript
const styles = StyleSheet.create({
  // 垂直堆叠（列）
  column: {
    flexDirection: "column",
    gap: 12,
  },
  // 水平堆叠（行）
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  // 项目间间距
  spaceBetween: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  // 居中内容
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  // 填充剩余空间
  fill: {
    flex: 1,
  },
});
```

### 3. React Navigation 设置

**Stack 导航器：**

```typescript
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  Detail: { itemId: string };
  Settings: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: { backgroundColor: '#6366f1' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: '600' },
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'Home' }}
        />
        <Stack.Screen
          name="Detail"
          component={DetailScreen}
          options={({ route }) => ({
            title: `Item ${route.params.itemId}`,
          })}
        />
        <Stack.Screen name="Settings" component={SettingsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

**Tab 导航器：**

```typescript
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

type TabParamList = {
  Home: undefined;
  Search: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<TabParamList>();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, keyof typeof Ionicons.glyphMap> = {
            Home: focused ? 'home' : 'home-outline',
            Search: focused ? 'search' : 'search-outline',
            Profile: focused ? 'person' : 'person-outline',
          };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6366f1',
        tabBarInactiveTintColor: '#9ca3af',
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Search" component={SearchScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
```

### 4. Reanimated 3 基础

**动画值：**

```typescript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
} from 'react-native-reanimated';

function AnimatedBox() {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  const handlePress = () => {
    scale.value = withSpring(1.2, {}, () => {
      scale.value = withSpring(1);
    });
  };

  return (
    <Pressable onPress={handlePress}>
      <Animated.View style={[styles.box, animatedStyle]} />
    </Pressable>
  );
}
```

**Gesture Handler 集成：**

```typescript
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

function DraggableCard() {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);

  const gesture = Gesture.Pan()
    .onUpdate((event) => {
      translateX.value = event.translationX;
      translateY.value = event.translationY;
    })
    .onEnd(() => {
      translateX.value = withSpring(0);
      translateY.value = withSpring(0);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
    ],
  }));

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View style={[styles.card, animatedStyle]}>
        <Text>Drag me!</Text>
      </Animated.View>
    </GestureDetector>
  );
}
```

### 5. 平台特定样式

```typescript
import { Platform, StyleSheet } from "react-native";

const styles = StyleSheet.create({
  container: {
    padding: 16,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  text: {
    fontFamily: Platform.OS === "ios" ? "SF Pro Text" : "Roboto",
    fontSize: 16,
  },
});

// 平台特定组件
import { Platform } from "react-native";
const StatusBarHeight = Platform.OS === "ios" ? 44 : 0;
```

## 快速开始组件

```typescript
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Image,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

interface ItemCardProps {
  title: string;
  subtitle: string;
  imageUrl: string;
  onPress: () => void;
}

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

export function ItemCard({ title, subtitle, imageUrl, onPress }: ItemCardProps) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <AnimatedPressable
      style={[styles.card, animatedStyle]}
      onPress={onPress}
      onPressIn={() => { scale.value = withSpring(0.97); }}
      onPressOut={() => { scale.value = withSpring(1); }}
    >
      <Image source={{ uri: imageUrl }} style={styles.image} />
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={1}>
          {title}
        </Text>
        <Text style={styles.subtitle} numberOfLines={2}>
          {subtitle}
        </Text>
      </View>
    </AnimatedPressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  image: {
    width: '100%',
    height: 160,
    backgroundColor: '#f3f4f6',
  },
  content: {
    padding: 16,
    gap: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
});
```

## 最佳实践

1. **使用 TypeScript**：定义导航和 props 类型以获得类型安全
2. **缓存组件**：使用 `React.memo` 和 `useCallback` 防止不必要的重新渲染
3. **在 UI 线程上运行动画**：使用 Reanimated worklets 获得 60fps 动画
4. **避免内联样式**：使用 StyleSheet.create 以获得更好性能
5. **处理安全区域**：使用 `SafeAreaView` 或 `useSafeAreaInsets`
6. **在真机上测试**：模拟器/仿真器性能与真机不同
7. **对列表使用 FlatList**：永远不要对长列表使用 ScrollView + map
8. **平台特定代码**：使用 Platform.select 处理 iOS/Android 差异

## 常见问题

- **手势冲突**：用 `GestureDetector` 包装手势并使用 `simultaneousHandlers`
- **导航类型错误**：为所有导航器定义 `ParamList` 类型
- **动画卡顿**：使用 `runOnUI` worklets 将动画移到 UI 线程
- **内存泄漏**：在 useEffect 中取消动画和清理
- **字体加载**：使用 `expo-font` 或 `react-native-asset` 加载自定义字体
- **安全区域问题**：在有刘海的设备上测试（iPhone、有挖孔的 Android）
