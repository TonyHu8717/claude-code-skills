---
name: modern-javascript-patterns
description: 掌握 ES6+ 特性，包括 async/await、解构、展开运算符、箭头函数、Promise、模块、迭代器、生成器和函数式编程模式，用于编写清晰高效的 JavaScript 代码。在重构遗留代码、实现现代模式或优化 JavaScript 应用时使用。
---

# 现代 JavaScript 模式

掌握现代 JavaScript（ES6+）特性、函数式编程模式和编写清晰、可维护、高性能代码最佳实践的综合指南。

## 何时使用此技能

- 将遗留 JavaScript 重构为现代语法
- 实现函数式编程模式
- 优化 JavaScript 性能
- 编写可维护和可读的代码
- 处理异步操作
- 构建现代 Web 应用
- 从回调迁移到 Promise/async-await
- 实现数据转换管道

## ES6+ 核心特性

### 1. 箭头函数

**语法和用例：**

```javascript
// 传统函数
function add(a, b) {
  return a + b;
}

// 箭头函数
const add = (a, b) => a + b;

// 单个参数（括号可选）
const double = (x) => x * 2;

// 无参数
const getRandom = () => Math.random();

// 多条语句（需要花括号）
const processUser = (user) => {
  const normalized = user.name.toLowerCase();
  return { ...user, name: normalized };
};

// 返回对象（用括号包裹）
const createUser = (name, age) => ({ name, age });
```

**词法 'this' 绑定：**

```javascript
class Counter {
  constructor() {
    this.count = 0;
  }

  // 箭头函数保留 'this' 上下文
  increment = () => {
    this.count++;
  };

  // 传统函数在回调中丢失 'this'
  incrementTraditional() {
    setTimeout(function () {
      this.count++; // 'this' 是 undefined
    }, 1000);
  }

  // 箭头函数维持 'this'
  incrementArrow() {
    setTimeout(() => {
      this.count++; // 'this' 指向 Counter 实例
    }, 1000);
  }
}
```

### 2. 解构

**对象解构：**

```javascript
const user = {
  id: 1,
  name: "John Doe",
  email: "john@example.com",
  address: {
    city: "New York",
    country: "USA",
  },
};

// 基本解构
const { name, email } = user;

// 重命名变量
const { name: userName, email: userEmail } = user;

// 默认值
const { age = 25 } = user;

// 嵌套解构
const {
  address: { city, country },
} = user;

// rest 运算符
const { id, ...userWithoutId } = user;

// 函数参数
function greet({ name, age = 18 }) {
  console.log(`Hello ${name}, you are ${age}`);
}
greet(user);
```

**数组解构：**

```javascript
const numbers = [1, 2, 3, 4, 5];

// 基本解构
const [first, second] = numbers;

// 跳过元素
const [, , third] = numbers;

// rest 运算符
const [head, ...tail] = numbers;

// 交换变量
let a = 1,
  b = 2;
[a, b] = [b, a];

// 函数返回值
function getCoordinates() {
  return [10, 20];
}
const [x, y] = getCoordinates();

// 默认值
const [one, two, three = 0] = [1, 2];
```

### 3. 展开和 Rest 运算符

**展开运算符：**

```javascript
// 数组展开
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2];

// 对象展开
const defaults = { theme: "dark", lang: "en" };
const userPrefs = { theme: "light" };
const settings = { ...defaults, ...userPrefs };

// 函数参数
const numbers = [1, 2, 3];
Math.max(...numbers);

// 复制数组/对象（浅拷贝）
const copy = [...arr1];
const objCopy = { ...user };

// 不可变地添加项
const newArr = [...arr1, 4, 5];
const newObj = { ...user, age: 30 };
```

**Rest 参数：**

```javascript
// 收集函数参数
function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0);
}
sum(1, 2, 3, 4, 5);

// 与常规参数一起使用
function greet(greeting, ...names) {
  return `${greeting} ${names.join(", ")}`;
}
greet("Hello", "John", "Jane", "Bob");

// 对象 rest
const { id, ...userData } = user;

// 数组 rest
const [first, ...rest] = [1, 2, 3, 4, 5];
```

### 4. 模板字面量

```javascript
// 基本用法
const name = "John";
const greeting = `Hello, ${name}!`;

// 多行字符串
const html = `
  <div>
    <h1>${title}</h1>
    <p>${content}</p>
  </div>
`;

// 表达式求值
const price = 19.99;
const total = `Total: $${(price * 1.2).toFixed(2)}`;

// 标签模板字面量
function highlight(strings, ...values) {
  return strings.reduce((result, str, i) => {
    const value = values[i] || "";
    return result + str + `<mark>${value}</mark>`;
  }, "");
}

const name = "John";
const age = 30;
const html = highlight`Name: ${name}, Age: ${age}`;
// 输出："Name: <mark>John</mark>, Age: <mark>30</mark>"
```

### 5. 增强的对象字面量

```javascript
const name = "John";
const age = 30;

// 简写属性名
const user = { name, age };

// 简写方法名
const calculator = {
  add(a, b) {
    return a + b;
  },
  subtract(a, b) {
    return a - b;
  },
};

// 计算属性名
const field = "email";
const user = {
  name: "John",
  [field]: "john@example.com",
  [`get${field.charAt(0).toUpperCase()}${field.slice(1)}`]() {
    return this[field];
  },
};

// 动态属性创建
const createUser = (name, ...props) => {
  return props.reduce(
    (user, [key, value]) => ({
      ...user,
      [key]: value,
    }),
    { name },
  );
};

const user = createUser("John", ["age", 30], ["email", "john@example.com"]);
```

## 异步模式

### 1. Promise

**创建和使用 Promise：**

```javascript
// 创建 Promise
const fetchUser = (id) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id > 0) {
        resolve({ id, name: "John" });
      } else {
        reject(new Error("Invalid ID"));
      }
    }, 1000);
  });
};

// 使用 Promise
fetchUser(1)
  .then((user) => console.log(user))
  .catch((error) => console.error(error))
  .finally(() => console.log("Done"));

// 链式 Promise
fetchUser(1)
  .then((user) => fetchUserPosts(user.id))
  .then((posts) => processPosts(posts))
  .then((result) => console.log(result))
  .catch((error) => console.error(error));
```

**Promise 组合器：**

```javascript
// Promise.all - 等待所有 Promise
const promises = [fetchUser(1), fetchUser(2), fetchUser(3)];

Promise.all(promises)
  .then((users) => console.log(users))
  .catch((error) => console.error("At least one failed:", error));

// Promise.allSettled - 等待所有，无论结果
Promise.allSettled(promises).then((results) => {
  results.forEach((result) => {
    if (result.status === "fulfilled") {
      console.log("Success:", result.value);
    } else {
      console.log("Error:", result.reason);
    }
  });
});

// Promise.race - 第一个完成的
Promise.race(promises)
  .then((winner) => console.log("First:", winner))
  .catch((error) => console.error(error));

// Promise.any - 第一个成功的
Promise.any(promises)
  .then((first) => console.log("First success:", first))
  .catch((error) => console.error("All failed:", error));
```

### 2. Async/Await

**基本用法：**

```javascript
// Async 函数始终返回 Promise
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  const user = await response.json();
  return user;
}

// 使用 try/catch 进行错误处理
async function getUserData(id) {
  try {
    const user = await fetchUser(id);
    const posts = await fetchUserPosts(user.id);
    return { user, posts };
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
}

// 顺序执行 vs 并行执行
async function sequential() {
  const user1 = await fetchUser(1); // 等待
  const user2 = await fetchUser(2); // 然后等待
  return [user1, user2];
}

async function parallel() {
  const [user1, user2] = await Promise.all([fetchUser(1), fetchUser(2)]);
  return [user1, user2];
}
```

**高级模式：**

```javascript
// Async IIFE
(async () => {
  const result = await someAsyncOperation();
  console.log(result);
})();

// 异步迭代
async function processUsers(userIds) {
  for (const id of userIds) {
    const user = await fetchUser(id);
    await processUser(user);
  }
}

// 顶层 await（ES2022）
const config = await fetch("/config.json").then((r) => r.json());

// 重试逻辑
async function fetchWithRetry(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise((resolve) => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}

// 超时包装器
async function withTimeout(promise, ms) {
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error("Timeout")), ms),
  );
  return Promise.race([promise, timeout]);
}
```

## 函数式编程模式

JavaScript 中的函数式编程以纯函数、不可变性和可组合的转换为核心。

关键主题详见 [references/advanced-patterns.md](references/advanced-patterns.md)：
- **数组方法** — `map`、`filter`、`reduce`、`find`、`findIndex`、`some`、`every`、`flatMap`、`Array.from`
- **高阶函数** — 自定义 `forEach`/`map`/`filter`、柯里化、偏应用、记忆化
- **组合和管道** — `compose`/`pipe` 工具及实际数据转换示例
- **纯函数和不可变性** — 不可变数组/对象操作、使用 `structuredClone` 的深拷贝

## 现代类特性

ES2022 类支持私有字段（`#field`）、静态字段、getter/setter 和私有方法。完整的继承示例请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。

## 模块（ES6）

```javascript
// 命名导出
export const PI = 3.14159;
export function add(a, b) { return a + b; }

// 默认导出
export default function multiply(a, b) { return a * b; }

// 导入
import multiply, { PI, add } from "./math.js";

// 动态导入（代码分割）
const { add } = await import("./math.js");
```

有关重新导出、命名空间导入和条件动态加载，请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。

## 迭代器和生成器

生成器（`function*`）和异步生成器（`async function*`）支持惰性序列和异步分页。自定义迭代器、范围生成器、斐波那契和 `for await...of` 示例请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。

## 现代运算符

```javascript
// 可选链 — 安全属性访问
const city = user?.address?.city;
const result = obj.method?.();

// 空值合并 — 仅对 null/undefined 使用默认值（不对 0 或 ""）
const value = null ?? "default"; // 'default'
const zero = 0 ?? "default";    // 0

// 逻辑赋值
a ??= "default";   // 如果 null/undefined 则赋值
obj.count ||= 1;   // 如果 falsy 则赋值
obj.count &&= 2;   // 如果 truthy 则赋值
```

## 性能优化

防抖、节流和使用生成器的惰性求值请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。

## 最佳实践

1. **默认使用 const**：仅在需要重新赋值时使用 let
2. **优先使用箭头函数**：尤其在回调中
3. **使用模板字面量**：替代字符串拼接
4. **解构对象和数组**：使代码更清晰
5. **使用 async/await**：替代 Promise 链
6. **避免修改数据**：使用展开运算符和数组方法
7. **使用可选链**：防止"Cannot read property of undefined"
8. **使用空值合并**：用于默认值
9. **优先使用数组方法**：替代传统循环
10. **使用模块**：实现更好的代码组织
11. **编写纯函数**：更容易测试和推理
12. **使用有意义的变量名**：自文档化代码
13. **保持函数小**：单一职责原则
14. **正确处理错误**：使用 try/catch 配合 async/await
15. **使用严格模式**：`'use strict'` 以更好地捕获错误

常见陷阱（this 绑定、Promise 反模式、内存泄漏）请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。
