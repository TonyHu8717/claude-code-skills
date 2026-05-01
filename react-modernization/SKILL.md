---
name: react-modernization
description: 升级 React 应用到最新版本，从类组件迁移到 hooks，并采用并发特性。在现代化 React 代码库、迁移到 React Hooks 或升级到最新 React 版本时使用。
---

# React 现代化

掌握 React 版本升级、类到 hooks 迁移、并发特性采用和用于自动转换的 codemods。

## 何时使用此技能

- 将 React 应用升级到最新版本
- 将类组件迁移到带有 hooks 的函数组件
- 采用并发 React 特性（Suspense、transitions）
- 应用 codemods 进行自动重构
- 现代化状态管理模式
- 更新到 TypeScript
- 使用 React 18+ 特性改进性能

## 版本升级路径

### React 16 → 17 → 18

**按版本的破坏性更改：**

**React 17：**

- 事件委托更改
- 无事件池
- Effect 清理时机
- JSX 转换（不再需要 React 导入）

**React 18：**

- 自动批处理
- 并发渲染
- 严格模式更改（双重调用）
- 新的 root API
- 服务端 Suspense

## 类到 Hooks 迁移

### 状态管理

```javascript
// 之前：类组件
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      count: 0,
      name: "",
    };
  }

  increment = () => {
    this.setState({ count: this.state.count + 1 });
  };

  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.increment}>Increment</button>
      </div>
    );
  }
}

// 之后：带 hooks 的函数组件
function Counter() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState("");

  const increment = () => {
    setCount(count + 1);
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
}
```

### 生命周期方法到 Hooks

```javascript
// 之前：生命周期方法
class DataFetcher extends React.Component {
  state = { data: null, loading: true };

  componentDidMount() {
    this.fetchData();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.id !== this.props.id) {
      this.fetchData();
    }
  }

  componentWillUnmount() {
    this.cancelRequest();
  }

  fetchData = async () => {
    const data = await fetch(`/api/${this.props.id}`);
    this.setState({ data, loading: false });
  };

  cancelRequest = () => {
    // 清理
  };

  render() {
    if (this.state.loading) return <div>Loading...</div>;
    return <div>{this.state.data}</div>;
  }
}

// 之后：useEffect hook
function DataFetcher({ id }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        const response = await fetch(`/api/${id}`);
        const result = await response.json();

        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      } catch (error) {
        if (!cancelled) {
          console.error(error);
        }
      }
    };

    fetchData();

    // 清理函数
    return () => {
      cancelled = true;
    };
  }, [id]); // id 变化时重新运行

  if (loading) return <div>Loading...</div>;
  return <div>{data}</div>;
}
```

### Context 和 HOCs 到 Hooks

```javascript
// 之前：Context consumer 和 HOC
const ThemeContext = React.createContext();

class ThemedButton extends React.Component {
  static contextType = ThemeContext;

  render() {
    return (
      <button style={{ background: this.context.theme }}>
        {this.props.children}
      </button>
    );
  }
}

// 之后：useContext hook
function ThemedButton({ children }) {
  const { theme } = useContext(ThemeContext);

  return <button style={{ background: theme }}>{children}</button>;
}

// 之前：用于数据获取的 HOC
function withUser(Component) {
  return class extends React.Component {
    state = { user: null };

    componentDidMount() {
      fetchUser().then((user) => this.setState({ user }));
    }

    render() {
      return <Component {...this.props} user={this.state.user} />;
    }
  };
}

// 之后：自定义 hook
function useUser() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser().then(setUser);
  }, []);

  return user;
}

function UserProfile() {
  const user = useUser();
  if (!user) return <div>Loading...</div>;
  return <div>{user.name}</div>;
}
```

## React 18 并发特性

### 新的 Root API

```javascript
// 之前：React 17
import ReactDOM from "react-dom";

ReactDOM.render(<App />, document.getElementById("root"));

// 之后：React 18
import { createRoot } from "react-dom/client";

const root = createRoot(document.getElementById("root"));
root.render(<App />);
```

### 自动批处理

```javascript
// React 18：所有更新都被批处理
function handleClick() {
  setCount((c) => c + 1);
  setFlag((f) => !f);
  // 只有一次重新渲染（批处理）
}

// 即使在异步中：
setTimeout(() => {
  setCount((c) => c + 1);
  setFlag((f) => !f);
  // 在 React 18 中仍然批处理！
}, 1000);

// 需要时退出
import { flushSync } from "react-dom";

flushSync(() => {
  setCount((c) => c + 1);
});
// 这里发生重新渲染
setFlag((f) => !f);
// 另一次重新渲染
```

### Transitions

```javascript
import { useState, useTransition } from "react";

function SearchResults() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    // 紧急：立即更新输入
    setQuery(e.target.value);

    // 非紧急：更新结果（可被中断）
    startTransition(() => {
      setResults(searchResults(e.target.value));
    });
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <Spinner />}
      <Results data={results} />
    </>
  );
}
```

### Suspense 用于数据获取

```javascript
import { Suspense } from "react";

// 基于资源的数据获取（使用 React 18）
const resource = fetchProfileData();

function ProfilePage() {
  return (
    <Suspense fallback={<Loading />}>
      <ProfileDetails />
      <Suspense fallback={<Loading />}>
        <ProfileTimeline />
      </Suspense>
    </Suspense>
  );
}

function ProfileDetails() {
  // 如果数据未就绪将挂起
  const user = resource.user.read();
  return <h1>{user.name}</h1>;
}

function ProfileTimeline() {
  const posts = resource.posts.read();
  return <Timeline posts={posts} />;
}
```

## 用于自动化的 Codemods

### 运行 React Codemods

```bash
# 重命名不安全的生命周期方法
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js src/

# 更新 React 导入（React 17+）
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/update-react-imports.js src/

# 添加错误边界
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/error-boundaries.js src/

# 用于 TypeScript 文件
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --parser=tsx src/

# 干运行预览更改
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --dry --print src/

# 类到 Hooks（第三方）
npx codemod react/hooks/convert-class-to-function src/
```

### 自定义 Codemod 示例

```javascript
// custom-codemod.js
module.exports = function (file, api) {
  const j = api.jscodeshift;
  const root = j(file.source);

  // 查找 setState 调用
  root
    .find(j.CallExpression, {
      callee: {
        type: "MemberExpression",
        property: { name: "setState" },
      },
    })
    .forEach((path) => {
      // 转换为 useState
      // ... 转换逻辑
    });

  return root.toSource();
};

// 运行：jscodeshift -t custom-codemod.js src/
```

## 性能优化

### useMemo 和 useCallback

```javascript
function ExpensiveComponent({ items, filter }) {
  // 缓存昂贵的计算
  const filteredItems = useMemo(() => {
    return items.filter((item) => item.category === filter);
  }, [items, filter]);

  // 缓存回调以防止子组件重新渲染
  const handleClick = useCallback((id) => {
    console.log("Clicked:", id);
  }, []); // 无依赖，永不改变

  return <List items={filteredItems} onClick={handleClick} />;
}

// 带 memo 的子组件
const List = React.memo(({ items, onClick }) => {
  return items.map((item) => (
    <Item key={item.id} item={item} onClick={onClick} />
  ));
});
```

### 代码分割

```javascript
import { lazy, Suspense } from "react";

// 懒加载组件
const Dashboard = lazy(() => import("./Dashboard"));
const Settings = lazy(() => import("./Settings"));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

## TypeScript 迁移

```typescript
// 之前：JavaScript
function Button({ onClick, children }) {
  return <button onClick={onClick}>{children}</button>;
}

// 之后：TypeScript
interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
}

function Button({ onClick, children }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>;
}

// 泛型组件
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <>{items.map(renderItem)}</>;
}
```

## 迁移清单

```markdown
### 迁移前

- [ ] 逐步更新依赖（不要一次性全部更新）
- [ ] 审查发布说明中的破坏性更改
- [ ] 设置测试套件
- [ ] 创建功能分支

### 类 → Hooks 迁移

- [ ] 识别要迁移的类组件
- [ ] 从叶子组件开始（无子组件）
- [ ] 将 state 转换为 useState
- [ ] 将生命周期转换为 useEffect
- [ ] 将 context 转换为 useContext
- [ ] 提取自定义 hooks
- [ ] 充分测试

### React 18 升级

- [ ] 先更新到 React 17（如需要）
- [ ] 更新 react 和 react-dom 到 18
- [ ] 如果使用 TypeScript 则更新 @types/react
- [ ] 更改为 createRoot API
- [ ] 使用 StrictMode 测试（双重调用）
- [ ] 处理并发渲染问题
- [ ] 在有益的地方采用 Suspense/Transitions

### 性能

- [ ] 识别性能瓶颈
- [ ] 在适当的地方添加 React.memo
- [ ] 对昂贵操作使用 useMemo/useCallback
- [ ] 实现代码分割
- [ ] 优化重新渲染

### 测试

- [ ] 更新测试工具（React Testing Library）
- [ ] 使用 React 18 特性测试
- [ ] 检查控制台中的警告
- [ ] 性能测试
```
