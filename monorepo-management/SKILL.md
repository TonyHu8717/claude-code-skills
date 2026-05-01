---
name: monorepo-management
description: 掌握使用 Turborepo、Nx 和 pnpm 工作区进行 monorepo 管理，构建高效的、可扩展的多包仓库，实现优化的构建和依赖管理。在设置 monorepo、优化构建或管理共享依赖时使用。
---

# Monorepo 管理

构建高效的、可扩展的 monorepo，实现跨多个包和应用的代码共享、一致的工具和原子化更改。

## 何时使用此技能

- 设置新的 monorepo 项目
- 从多仓库迁移到 monorepo
- 优化构建和测试性能
- 管理共享依赖
- 实现代码共享策略
- 为 monorepo 设置 CI/CD
- 版本控制和发布包
- 调试 monorepo 特定问题

## 核心概念

### 1. 为什么使用 Monorepo？

**优势：**

- 共享代码和依赖
- 跨项目的原子提交
- 一致的工具和标准
- 更容易的重构
- 简化的依赖管理
- 更好的代码可见性

**挑战：**

- 大规模构建性能
- CI/CD 复杂性
- 访问控制
- 大型 Git 仓库

### 2. Monorepo 工具

**包管理器：**

- pnpm 工作区（推荐）
- npm 工作区
- Yarn 工作区

**构建系统：**

- Turborepo（大多数情况推荐）
- Nx（功能丰富，较复杂）
- Lerna（较旧，维护模式）

## Turborepo 设置

### 初始设置

```bash
# 创建新的 monorepo
npx create-turbo@latest my-monorepo
cd my-monorepo

# 结构：
# apps/
#   web/          - Next.js 应用
#   docs/         - 文档站点
# packages/
#   ui/           - 共享 UI 组件
#   config/       - 共享配置
#   tsconfig/     - 共享 TypeScript 配置
# turbo.json      - Turborepo 配置
# package.json    - 根 package.json
```

### 配置

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": []
    }
  }
}
```

```json
// package.json（根目录）
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "format": "prettier --write \"**/*.{ts,tsx,md}\"",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0"
  },
  "packageManager": "pnpm@8.0.0"
}
```

### 包结构

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./button": {
      "import": "./dist/button.js",
      "types": "./dist/button.d.ts"
    }
  },
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "dev": "tsup src/index.ts --format esm,cjs --dts --watch",
    "lint": "eslint src/",
    "type-check": "tsc --noEmit"
  },
  "devDependencies": {
    "@repo/tsconfig": "workspace:*",
    "tsup": "^7.0.0",
    "typescript": "^5.0.0"
  },
  "dependencies": {
    "react": "^18.2.0"
  }
}
```

## pnpm 工作区

### 设置

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
  - "tools/*"
```

```json
// .npmrc
# 提升共享依赖
shamefully-hoist=true

# 严格对等依赖
auto-install-peers=true
strict-peer-dependencies=true

# 性能
store-dir=~/.pnpm-store
```

### 依赖管理

```bash
# 在特定包中安装依赖
pnpm add react --filter @repo/ui
pnpm add -D typescript --filter @repo/ui

# 安装工作区依赖
pnpm add @repo/ui --filter web

# 在所有包中安装
pnpm add -D eslint -w

# 更新所有依赖
pnpm update -r

# 移除依赖
pnpm remove react --filter @repo/ui
```

### 脚本

```bash
# 在特定包中运行脚本
pnpm --filter web dev
pnpm --filter @repo/ui build

# 在所有包中运行
pnpm -r build
pnpm -r test

# 并行运行
pnpm -r --parallel dev

# 按模式过滤
pnpm --filter "@repo/*" build
pnpm --filter "...web" build  # 构建 web 及其依赖
```

## Nx Monorepo

### 设置

```bash
# 创建 Nx monorepo
npx create-nx-workspace@latest my-org

# 生成应用
nx generate @nx/react:app my-app
nx generate @nx/next:app my-next-app

# 生成库
nx generate @nx/react:lib ui-components
nx generate @nx/js:lib utils
```

### 配置

```json
// nx.json
{
  "extends": "nx/presets/npm.json",
  "$schema": "./node_modules/nx/schemas/nx-schema.json",
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["production", "^production"],
      "cache": true
    },
    "test": {
      "inputs": ["default", "^production", "{workspaceRoot}/jest.preset.js"],
      "cache": true
    },
    "lint": {
      "inputs": ["default", "{workspaceRoot}/.eslintrc.json"],
      "cache": true
    }
  },
  "namedInputs": {
    "default": ["{projectRoot}/**/*", "sharedGlobals"],
    "production": [
      "default",
      "!{projectRoot}/**/?(*.)+(spec|test).[jt]s?(x)?(.snap)",
      "!{projectRoot}/tsconfig.spec.json"
    ],
    "sharedGlobals": []
  }
}
```

### 运行任务

```bash
# 为特定项目运行任务
nx build my-app
nx test ui-components
nx lint utils

# 为受影响的项目运行
nx affected:build
nx affected:test --base=main

# 可视化依赖
nx graph

# 并行运行
nx run-many --target=build --all --parallel=3
```

## 共享配置

### TypeScript 配置

```json
// packages/tsconfig/base.json
{
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true,
    "declaration": true
  },
  "exclude": ["node_modules"]
}

// packages/tsconfig/react.json
{
  "extends": "./base.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "lib": ["ES2022", "DOM", "DOM.Iterable"]
  }
}

// apps/web/tsconfig.json
{
  "extends": "@repo/tsconfig/react.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### ESLint 配置

```javascript
// packages/config/eslint-preset.js
module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier",
  ],
  plugins: ["@typescript-eslint", "react", "react-hooks"],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  settings: {
    react: {
      version: "detect",
    },
  },
  rules: {
    "@typescript-eslint/no-unused-vars": "error",
    "react/react-in-jsx-scope": "off",
  },
};

// apps/web/.eslintrc.js
module.exports = {
  extends: ["@repo/config/eslint-preset"],
  rules: {
    // 应用特定规则
  },
};
```

## 代码共享模式

### 模式 1：共享 UI 组件

```typescript
// packages/ui/src/button.tsx
import * as React from 'react';

export interface ButtonProps {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant = 'primary', children, onClick }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

// packages/ui/src/index.ts
export { Button, type ButtonProps } from './button';
export { Input, type InputProps } from './input';

// apps/web/src/app.tsx
import { Button } from '@repo/ui';

export function App() {
  return <Button variant="primary">Click me</Button>;
}
```

### 模式 2：共享工具

```typescript
// packages/utils/src/string.ts
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function truncate(str: string, length: number): string {
  return str.length > length ? str.slice(0, length) + "..." : str;
}

// packages/utils/src/index.ts
export * from "./string";
export * from "./array";
export * from "./date";

// 在应用中使用
import { capitalize, truncate } from "@repo/utils";
```

### 模式 3：共享类型

```typescript
// packages/types/src/user.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user";
}

export interface CreateUserInput {
  email: string;
  name: string;
  password: string;
}

// 在前端和后端中使用
import type { User, CreateUserInput } from "@repo/types";
```

## 构建优化

### Turborepo 缓存

```json
// turbo.json
{
  "pipeline": {
    "build": {
      // 构建依赖于依赖项先被构建
      "dependsOn": ["^build"],

      // 缓存这些输出
      "outputs": ["dist/**", ".next/**"],

      // 基于这些输入进行缓存（默认：所有文件）
      "inputs": ["src/**/*.tsx", "src/**/*.ts", "package.json"]
    },
    "test": {
      // 并行运行测试，不依赖构建
      "cache": true,
      "outputs": ["coverage/**"]
    }
  }
}
```

### 远程缓存

```bash
# Turborepo 远程缓存（Vercel）
npx turbo login
npx turbo link

# 自定义远程缓存
# turbo.json
{
  "remoteCache": {
    "signature": true,
    "enabled": true
  }
}
```

## Monorepo 的 CI/CD

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 # 用于 Nx affected 命令

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: "pnpm"

      - name: 安装依赖
        run: pnpm install --frozen-lockfile

      - name: 构建
        run: pnpm turbo run build

      - name: 测试
        run: pnpm turbo run test

      - name: Lint
        run: pnpm turbo run lint

      - name: 类型检查
        run: pnpm turbo run type-check
```

### 仅部署受影响的

```yaml
# 仅部署更改的应用
- name: 部署受影响的应用
  run: |
    if pnpm nx affected:apps --base=origin/main --head=HEAD | grep -q "web"; then
      echo "部署 web 应用"
      pnpm --filter web deploy
    fi
```

## 最佳实践

1. **一致的版本控制**：锁定工作区中的依赖版本
2. **共享配置**：集中 ESLint、TypeScript、Prettier 配置
3. **依赖图**：保持无环，避免循环依赖
4. **有效缓存**：正确配置输入/输出
5. **类型安全**：在前端/后端之间共享类型
6. **测试策略**：包中做单元测试，应用中做 E2E 测试
7. **文档**：每个包中放 README
8. **发布策略**：使用 changesets 进行版本控制

## 常见陷阱

- **循环依赖**：A 依赖 B，B 依赖 A
- **幽灵依赖**：使用 package.json 中未声明的依赖
- **错误的缓存输入**：Turborepo 输入中遗漏文件
- **过度共享**：共享应该分开的代码
- **共享不足**：跨包重复代码
- **大型 monorepo**：没有适当的工具，构建会变慢

## 发布包

```bash
# 使用 Changesets
pnpm add -Dw @changesets/cli
pnpm changeset init

# 创建 changeset
pnpm changeset

# 版本化包
pnpm changeset version

# 发布
pnpm changeset publish
```

```yaml
# .github/workflows/release.yml
- name: 创建发布 PR 或发布
  uses: changesets/action@v1
  with:
    publish: pnpm release
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```
