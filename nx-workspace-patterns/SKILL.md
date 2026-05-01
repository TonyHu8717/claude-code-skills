---
name: nx-workspace-patterns
description: 配置和优化 Nx monorepo 工作区。在设置 Nx、配置项目边界、优化构建缓存或实现受影响命令时使用。
---

# Nx 工作区模式

Nx monorepo 管理的生产模式。

## 何时使用此技能

- 设置新的 Nx 工作区
- 配置项目边界
- 使用受影响命令优化 CI
- 实现远程缓存
- 管理项目间的依赖
- 迁移到 Nx

## 核心概念

### 1. Nx 架构

```
workspace/
├── apps/              # 可部署的应用
│   ├── web/
│   └── api/
├── libs/              # 共享库
│   ├── shared/
│   │   ├── ui/
│   │   └── utils/
│   └── feature/
│       ├── auth/
│       └── dashboard/
├── tools/             # 自定义执行器/生成器
├── nx.json            # Nx 配置
└── workspace.json     # 项目配置
```

### 2. 库类型

| 类型           | 用途                         | 示例                |
| -------------- | ---------------------------- | ------------------- |
| **feature**    | 智能组件、业务逻辑           | `feature-auth`      |
| **ui**         | 展示组件                     | `ui-buttons`        |
| **data-access**| API 调用、状态管理           | `data-access-users` |
| **util**       | 纯函数、辅助工具             | `util-formatting`   |
| **shell**      | 应用引导                     | `shell-web`         |

## 模板

### 模板 1：nx.json 配置

```json
{
  "$schema": "./node_modules/nx/schemas/nx-schema.json",
  "npmScope": "myorg",
  "affected": {
    "defaultBase": "main"
  },
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": {
        "cacheableOperations": [
          "build",
          "lint",
          "test",
          "e2e",
          "build-storybook"
        ],
        "parallel": 3
      }
    }
  },
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
    },
    "e2e": {
      "inputs": ["default", "^production"],
      "cache": true
    }
  },
  "namedInputs": {
    "default": ["{projectRoot}/**/*", "sharedGlobals"],
    "production": [
      "default",
      "!{projectRoot}/**/?(*.)+(spec|test).[jt]s?(x)?(.snap)",
      "!{projectRoot}/tsconfig.spec.json",
      "!{projectRoot}/jest.config.[jt]s",
      "!{projectRoot}/.eslintrc.json"
    ],
    "sharedGlobals": [
      "{workspaceRoot}/babel.config.json",
      "{workspaceRoot}/tsconfig.base.json"
    ]
  },
  "generators": {
    "@nx/react": {
      "application": {
        "style": "css",
        "linter": "eslint",
        "bundler": "webpack"
      },
      "library": {
        "style": "css",
        "linter": "eslint"
      },
      "component": {
        "style": "css"
      }
    }
  }
}
```

### 模板 2：项目配置

```json
// apps/web/project.json
{
  "name": "web",
  "$schema": "../../node_modules/nx/schemas/project-schema.json",
  "sourceRoot": "apps/web/src",
  "projectType": "application",
  "tags": ["type:app", "scope:web"],
  "targets": {
    "build": {
      "executor": "@nx/webpack:webpack",
      "outputs": ["{options.outputPath}"],
      "defaultConfiguration": "production",
      "options": {
        "compiler": "babel",
        "outputPath": "dist/apps/web",
        "index": "apps/web/src/index.html",
        "main": "apps/web/src/main.tsx",
        "tsConfig": "apps/web/tsconfig.app.json",
        "assets": ["apps/web/src/assets"],
        "styles": ["apps/web/src/styles.css"]
      },
      "configurations": {
        "development": {
          "extractLicenses": false,
          "optimization": false,
          "sourceMap": true
        },
        "production": {
          "optimization": true,
          "outputHashing": "all",
          "sourceMap": false,
          "extractLicenses": true
        }
      }
    },
    "serve": {
      "executor": "@nx/webpack:dev-server",
      "defaultConfiguration": "development",
      "options": {
        "buildTarget": "web:build"
      },
      "configurations": {
        "development": {
          "buildTarget": "web:build:development"
        },
        "production": {
          "buildTarget": "web:build:production"
        }
      }
    },
    "test": {
      "executor": "@nx/jest:jest",
      "outputs": ["{workspaceRoot}/coverage/{projectRoot}"],
      "options": {
        "jestConfig": "apps/web/jest.config.ts",
        "passWithNoTests": true
      }
    },
    "lint": {
      "executor": "@nx/eslint:lint",
      "outputs": ["{options.outputFile}"],
      "options": {
        "lintFilePatterns": ["apps/web/**/*.{ts,tsx,js,jsx}"]
      }
    }
  }
}
```

### 模板 3：模块边界规则

```json
// .eslintrc.json
{
  "root": true,
  "ignorePatterns": ["**/*"],
  "plugins": ["@nx"],
  "overrides": [
    {
      "files": ["*.ts", "*.tsx", "*.js", "*.jsx"],
      "rules": {
        "@nx/enforce-module-boundaries": [
          "error",
          {
            "enforceBuildableLibDependency": true,
            "allow": [],
            "depConstraints": [
              {
                "sourceTag": "type:app",
                "onlyDependOnLibsWithTags": [
                  "type:feature",
                  "type:ui",
                  "type:data-access",
                  "type:util"
                ]
              },
              {
                "sourceTag": "type:feature",
                "onlyDependOnLibsWithTags": [
                  "type:ui",
                  "type:data-access",
                  "type:util"
                ]
              },
              {
                "sourceTag": "type:ui",
                "onlyDependOnLibsWithTags": ["type:ui", "type:util"]
              },
              {
                "sourceTag": "type:data-access",
                "onlyDependOnLibsWithTags": ["type:data-access", "type:util"]
              },
              {
                "sourceTag": "type:util",
                "onlyDependOnLibsWithTags": ["type:util"]
              },
              {
                "sourceTag": "scope:web",
                "onlyDependOnLibsWithTags": ["scope:web", "scope:shared"]
              },
              {
                "sourceTag": "scope:api",
                "onlyDependOnLibsWithTags": ["scope:api", "scope:shared"]
              },
              {
                "sourceTag": "scope:shared",
                "onlyDependOnLibsWithTags": ["scope:shared"]
              }
            ]
          }
        ]
      }
    }
  ]
}
```

### 模板 4：自定义生成器

```typescript
// tools/generators/feature-lib/index.ts
import {
  Tree,
  formatFiles,
  generateFiles,
  joinPathFragments,
  names,
  readProjectConfiguration,
} from "@nx/devkit";
import { libraryGenerator } from "@nx/react";

interface FeatureLibraryGeneratorSchema {
  name: string;
  scope: string;
  directory?: string;
}

export default async function featureLibraryGenerator(
  tree: Tree,
  options: FeatureLibraryGeneratorSchema,
) {
  const { name, scope, directory } = options;
  const projectDirectory = directory
    ? `${directory}/${name}`
    : `libs/${scope}/feature-${name}`;

  // 生成基础库
  await libraryGenerator(tree, {
    name: `feature-${name}`,
    directory: projectDirectory,
    tags: `type:feature,scope:${scope}`,
    style: "css",
    skipTsConfig: false,
    skipFormat: true,
    unitTestRunner: "jest",
    linter: "eslint",
  });

  // 添加自定义文件
  const projectConfig = readProjectConfiguration(
    tree,
    `${scope}-feature-${name}`,
  );
  const projectNames = names(name);

  generateFiles(
    tree,
    joinPathFragments(__dirname, "files"),
    projectConfig.sourceRoot,
    {
      ...projectNames,
      scope,
      tmpl: "",
    },
  );

  await formatFiles(tree);
}
```

### 模板 5：带受影响的 CI 配置

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  NX_CLOUD_ACCESS_TOKEN: ${{ secrets.NX_CLOUD_ACCESS_TOKEN }}

jobs:
  main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"

      - name: 安装依赖
        run: npm ci

      - name: 为受影响命令派生 SHAs
        uses: nrwl/nx-set-shas@v4

      - name: 运行受影响的 lint
        run: npx nx affected -t lint --parallel=3

      - name: 运行受影响的测试
        run: npx nx affected -t test --parallel=3 --configuration=ci

      - name: 运行受影响的构建
        run: npx nx affected -t build --parallel=3

      - name: 运行受影响的 e2e
        run: npx nx affected -t e2e --parallel=1
```

### 模板 6：远程缓存设置

```typescript
// 带 Nx Cloud 的 nx.json
{
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx-cloud",
      "options": {
        "cacheableOperations": ["build", "lint", "test", "e2e"],
        "accessToken": "your-nx-cloud-token",
        "parallel": 3,
        "cacheDirectory": ".nx/cache"
      }
    }
  },
  "nxCloudAccessToken": "your-nx-cloud-token"
}

// 使用 S3 的自托管缓存
{
  "tasksRunnerOptions": {
    "default": {
      "runner": "@nx-aws-cache/nx-aws-cache",
      "options": {
        "cacheableOperations": ["build", "lint", "test"],
        "awsRegion": "us-east-1",
        "awsBucket": "my-nx-cache-bucket",
        "awsProfile": "default"
      }
    }
  }
}
```

## 常用命令

```bash
# 生成新库
nx g @nx/react:lib feature-auth --directory=libs/web --tags=type:feature,scope:web

# 运行受影响的测试
nx affected -t test --base=main

# 查看依赖图
nx graph

# 运行特定项目
nx build web --configuration=production

# 重置缓存
nx reset

# 运行迁移
nx migrate latest
nx migrate --run-migrations
```

## 最佳实践

### 推荐做法

- **一致地使用标签** - 通过模块边界强制执行
- **尽早启用缓存** - 显著节省 CI
- **保持库专注** - 单一职责
- **使用生成器** - 确保一致性
- **记录边界** - 帮助新开发者

### 避免做法

- **不要创建循环依赖** - 图应该是无环的
- **不要跳过受影响** - 仅测试更改的部分
- **不要忽略边界** - 技术债务会累积
- **不要过度细化** - 平衡库数量
