---
name: dependency-upgrade
description: 管理主要依赖版本升级，包括兼容性分析、分阶段发布和全面测试。在升级框架版本、更新主要依赖或处理库中的破坏性变更时使用。
---

# 依赖升级

掌握主要依赖版本升级、兼容性分析、分阶段升级策略和全面测试方法。

## 何时使用此技能

- 升级主要框架版本
- 更新存在安全漏洞的依赖
- 现代化旧版依赖
- 解决依赖冲突
- 规划增量升级路径
- 测试兼容性矩阵
- 自动化依赖更新

## 语义化版本回顾

```
MAJOR.MINOR.PATCH（例如 2.3.1）

MAJOR：破坏性变更
MINOR：新功能，向后兼容
PATCH：错误修复，向后兼容

^2.3.1 = >=2.3.1 <3.0.0（次要更新）
~2.3.1 = >=2.3.1 <2.4.0（补丁更新）
2.3.1 = 精确版本
```

## 依赖分析

### 审计依赖

```bash
# npm
npm outdated
npm audit
npm audit fix

# yarn
yarn outdated
yarn audit

# 检查主要更新
npx npm-check-updates
npx npm-check-updates -u  # 更新 package.json
```

### 分析依赖树

```bash
# 查看安装某个包的原因
npm ls package-name
yarn why package-name

# 查找重复包
npm dedupe
yarn dedupe

# 可视化依赖
npx madge --image graph.png src/
```

## 兼容性矩阵

```javascript
// compatibility-matrix.js
const compatibilityMatrix = {
  react: {
    "16.x": {
      "react-dom": "^16.0.0",
      "react-router-dom": "^5.0.0",
      "@testing-library/react": "^11.0.0",
    },
    "17.x": {
      "react-dom": "^17.0.0",
      "react-router-dom": "^5.0.0 || ^6.0.0",
      "@testing-library/react": "^12.0.0",
    },
    "18.x": {
      "react-dom": "^18.0.0",
      "react-router-dom": "^6.0.0",
      "@testing-library/react": "^13.0.0",
    },
  },
};

function checkCompatibility(packages) {
  // 根据矩阵验证包版本
}
```

## 分阶段升级策略

### 阶段 1：规划

```bash
# 1. 识别当前版本
npm list --depth=0

# 2. 检查破坏性变更
# 阅读 CHANGELOG.md 和 MIGRATION.md

# 3. 创建升级计划
echo "升级顺序：
1. TypeScript
2. React
3. React Router
4. 测试库
5. 构建工具" > UPGRADE_PLAN.md
```

### 阶段 2：增量更新

```bash
# 不要一次升级所有内容！

# 步骤 1：更新 TypeScript
npm install typescript@latest

# 测试
npm run test
npm run build

# 步骤 2：更新 React（一次升级一个主要版本）
npm install react@17 react-dom@17

# 再次测试
npm run test

# 步骤 3：继续更新其他包
npm install react-router-dom@6

# 依此类推...
```

### 阶段 3：验证

```javascript
// tests/compatibility.test.js
describe("Dependency Compatibility", () => {
  it("should have compatible React versions", () => {
    const reactVersion = require("react/package.json").version;
    const reactDomVersion = require("react-dom/package.json").version;

    expect(reactVersion).toBe(reactDomVersion);
  });

  it("should not have peer dependency warnings", () => {
    // 运行 npm ls 并检查警告
  });
});
```

## 破坏性变更处理

### 识别破坏性变更

```bash
# 直接检查变更日志
curl https://raw.githubusercontent.com/facebook/react/master/CHANGELOG.md
```

### 使用 Codemod 自动修复

```bash
# 使用转换 URL 运行 jscodeshift
npx jscodeshift -t <transform-url> <path>

# 示例：重命名不安全的生命周期方法
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js src/

# 对于 TypeScript 文件
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --parser=tsx src/

# 试运行以预览更改
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --dry src/
```

### 自定义迁移脚本

```javascript
// migration-script.js
const fs = require("fs");
const glob = require("glob");

glob("src/**/*.tsx", (err, files) => {
  files.forEach((file) => {
    let content = fs.readFileSync(file, "utf8");

    // 用新 API 替换旧 API
    content = content.replace(
      /componentWillMount/g,
      "UNSAFE_componentWillMount",
    );

    // 更新导入
    content = content.replace(
      /import { Component } from 'react'/g,
      "import React, { Component } from 'react'",
    );

    fs.writeFileSync(file, content);
  });
});
```

## 测试策略

### 单元测试

```javascript
// 确保升级前后测试通过
npm run test

// 如果需要，更新测试工具
npm install @testing-library/react@latest
```

### 集成测试

```javascript
// tests/integration/app.test.js
describe("App Integration", () => {
  it("should render without crashing", () => {
    render(<App />);
  });

  it("should handle navigation", () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText("Navigate"));
    expect(screen.getByText("New Page")).toBeInTheDocument();
  });
});
```

### 视觉回归测试

```javascript
// visual-regression.test.js
describe("Visual Regression", () => {
  it("should match snapshot", () => {
    const { container } = render(<App />);
    expect(container.firstChild).toMatchSnapshot();
  });
});
```

### 端到端测试

```javascript
// cypress/e2e/app.cy.js
describe("E2E Tests", () => {
  it("should complete user flow", () => {
    cy.visit("/");
    cy.get('[data-testid="login"]').click();
    cy.get('input[name="email"]').type("user@example.com");
    cy.get('button[type="submit"]').click();
    cy.url().should("include", "/dashboard");
  });
});
```

## 自动化依赖更新

### Renovate 配置

```json
// renovate.json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["major-update"]
    }
  ],
  "schedule": ["before 3am on Monday"],
  "timezone": "America/New_York"
}
```

### Dependabot 配置

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    reviewers:
      - "team-leads"
    commit-message:
      prefix: "chore"
      include: "scope"
```

## 回滚计划

```javascript
// rollback.sh
#!/bin/bash

# 保存当前状态
git stash
git checkout -b upgrade-branch

# 尝试升级
npm install package@latest

# 运行测试
if npm run test; then
  echo "升级成功"
  git add package.json package-lock.json
  git commit -m "chore: upgrade package"
else
  echo "升级失败，回滚中"
  git checkout main
  git branch -D upgrade-branch
  npm install  # 从 package-lock.json 恢复
fi
```

## 常见升级模式

### 锁文件管理

```bash
# npm
npm install --package-lock-only  # 仅更新锁文件
npm ci  # 从锁文件进行干净安装

# yarn
yarn install --frozen-lockfile  # CI 模式
yarn upgrade-interactive  # 交互式升级
```

### 对等依赖解析

```bash
# npm 7+：严格对等依赖
npm install --legacy-peer-deps  # 忽略对等依赖

# npm 8+：覆盖对等依赖
npm install --force
```

### 工作区升级

```bash
# 更新所有工作区包
npm install --workspaces

# 更新特定工作区
npm install package@latest --workspace=packages/app
```
