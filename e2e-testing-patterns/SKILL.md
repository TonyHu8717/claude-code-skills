---
name: e2e-testing-patterns
description: 掌握使用 Playwright 和 Cypress 进行端到端测试，构建可靠的测试套件以捕获错误、提高信心并实现快速部署。在实现 E2E 测试、调试不稳定测试或建立测试标准时使用。
---

# E2E 测试模式

构建可靠、快速且可维护的端到端测试套件，为快速发布代码提供信心，并在用户之前捕获回归问题。

## 何时使用此技能

- 实现端到端测试自动化
- 调试不稳定或不可靠的测试
- 测试关键用户工作流
- 设置 CI/CD 测试流水线
- 跨多个浏览器测试
- 验证无障碍访问要求
- 测试响应式设计
- 建立 E2E 测试标准

## 核心概念

### 1. E2E 测试基础

**E2E 应该测试什么：**

- 关键用户旅程（登录、结账、注册）
- 复杂交互（拖放、多步骤表单）
- 跨浏览器兼容性
- 真实 API 集成
- 身份验证流程

**E2E 不应该测试什么：**

- 单元级逻辑（使用单元测试）
- API 契约（使用集成测试）
- 边缘情况（太慢）
- 内部实现细节

### 2. 测试理念

**测试金字塔：**

```
        /\
       /E2E\         ← 少量，专注于关键路径
      /─────\
     /Integr\        ← 更多，测试组件交互
    /────────\
   /Unit Tests\      ← 大量，快速，隔离
  /────────────\
```

**最佳实践：**

- 测试用户行为，而非实现
- 保持测试独立性
- 使测试具有确定性
- 优化速度
- 使用 data-testid，而非 CSS 选择器

## Playwright 模式

### 设置和配置

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html"], ["junit", { outputFile: "results.xml" }]],
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "mobile", use: { ...devices["iPhone 13"] } },
  ],
});
```

### 模式 1：页面对象模型

```typescript
// pages/LoginPage.ts
import { Page, Locator } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel("Email");
    this.passwordInput = page.getByLabel("Password");
    this.loginButton = page.getByRole("button", { name: "Login" });
    this.errorMessage = page.getByRole("alert");
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async getErrorMessage(): Promise<string> {
    return (await this.errorMessage.textContent()) ?? "";
  }
}

// 使用页面对象的测试
import { test, expect } from "@playwright/test";
import { LoginPage } from "./pages/LoginPage";

test("successful login", async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login("user@example.com", "password123");

  await expect(page).toHaveURL("/dashboard");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
});

test("failed login shows error", async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login("invalid@example.com", "wrong");

  const error = await loginPage.getErrorMessage();
  expect(error).toContain("Invalid credentials");
});
```

### 模式 2：测试数据 Fixture

```typescript
// fixtures/test-data.ts
import { test as base } from "@playwright/test";

type TestData = {
  testUser: {
    email: string;
    password: string;
    name: string;
  };
  adminUser: {
    email: string;
    password: string;
  };
};

export const test = base.extend<TestData>({
  testUser: async ({}, use) => {
    const user = {
      email: `test-${Date.now()}@example.com`,
      password: "Test123!@#",
      name: "Test User",
    };
    // 设置：在数据库中创建用户
    await createTestUser(user);
    await use(user);
    // 清理：删除用户
    await deleteTestUser(user.email);
  },

  adminUser: async ({}, use) => {
    await use({
      email: "admin@example.com",
      password: process.env.ADMIN_PASSWORD!,
    });
  },
});

// 测试中的用法
import { test } from "./fixtures/test-data";

test("user can update profile", async ({ page, testUser }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(testUser.email);
  await page.getByLabel("Password").fill(testUser.password);
  await page.getByRole("button", { name: "Login" }).click();

  await page.goto("/profile");
  await page.getByLabel("Name").fill("Updated Name");
  await page.getByRole("button", { name: "Save" }).click();

  await expect(page.getByText("Profile updated")).toBeVisible();
});
```

### 模式 3：等待策略

```typescript
// ❌ 不好：固定超时
await page.waitForTimeout(3000); // 不稳定！

// ✅ 好：等待特定条件
await page.waitForLoadState("networkidle");
await page.waitForURL("/dashboard");
await page.waitForSelector('[data-testid="user-profile"]');

// ✅ 更好：使用断言自动等待
await expect(page.getByText("Welcome")).toBeVisible();
await expect(page.getByRole("button", { name: "Submit" })).toBeEnabled();

// 等待 API 响应
const responsePromise = page.waitForResponse(
  (response) =>
    response.url().includes("/api/users") && response.status() === 200,
);
await page.getByRole("button", { name: "Load Users" }).click();
const response = await responsePromise;
const data = await response.json();
expect(data.users).toHaveLength(10);

// 等待多个条件
await Promise.all([
  page.waitForURL("/success"),
  page.waitForLoadState("networkidle"),
  expect(page.getByText("Payment successful")).toBeVisible(),
]);
```

### 模式 4：网络模拟和拦截

```typescript
// 模拟 API 响应
test("displays error when API fails", async ({ page }) => {
  await page.route("**/api/users", (route) => {
    route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({ error: "Internal Server Error" }),
    });
  });

  await page.goto("/users");
  await expect(page.getByText("Failed to load users")).toBeVisible();
});

// 拦截并修改请求
test("can modify API request", async ({ page }) => {
  await page.route("**/api/users", async (route) => {
    const request = route.request();
    const postData = JSON.parse(request.postData() || "{}");

    // 修改请求
    postData.role = "admin";

    await route.continue({
      postData: JSON.stringify(postData),
    });
  });

  // 测试继续...
});

// 模拟第三方服务
test("payment flow with mocked Stripe", async ({ page }) => {
  await page.route("**/api/stripe/**", (route) => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({
        id: "mock_payment_id",
        status: "succeeded",
      }),
    });
  });

  // 使用模拟响应测试支付流程
});
```

## Cypress 模式

### 设置和配置

```typescript
// cypress.config.ts
import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:3000",
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    setupNodeEvents(on, config) {
      // 实现节点事件监听器
    },
  },
});
```

### 模式 1：自定义命令

```typescript
// cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      createUser(userData: UserData): Chainable<User>;
      dataCy(value: string): Chainable<JQuery<HTMLElement>>;
    }
  }
}

Cypress.Commands.add("login", (email: string, password: string) => {
  cy.visit("/login");
  cy.get('[data-testid="email"]').type(email);
  cy.get('[data-testid="password"]').type(password);
  cy.get('[data-testid="login-button"]').click();
  cy.url().should("include", "/dashboard");
});

Cypress.Commands.add("createUser", (userData: UserData) => {
  return cy.request("POST", "/api/users", userData).its("body");
});

Cypress.Commands.add("dataCy", (value: string) => {
  return cy.get(`[data-cy="${value}"]`);
});

// 用法
cy.login("user@example.com", "password");
cy.dataCy("submit-button").click();
```

### 模式 2：Cypress 拦截

```typescript
// 模拟 API 调用
cy.intercept("GET", "/api/users", {
  statusCode: 200,
  body: [
    { id: 1, name: "John" },
    { id: 2, name: "Jane" },
  ],
}).as("getUsers");

cy.visit("/users");
cy.wait("@getUsers");
cy.get('[data-testid="user-list"]').children().should("have.length", 2);

// 修改响应
cy.intercept("GET", "/api/users", (req) => {
  req.reply((res) => {
    // 修改响应
    res.body.users = res.body.users.slice(0, 5);
    res.send();
  });
});

// 模拟慢速网络
cy.intercept("GET", "/api/data", (req) => {
  req.reply((res) => {
    res.delay(3000); // 3 秒延迟
    res.send();
  });
});
```

## 高级模式

### 模式 1：视觉回归测试

```typescript
// 使用 Playwright
import { test, expect } from "@playwright/test";

test("homepage looks correct", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveScreenshot("homepage.png", {
    fullPage: true,
    maxDiffPixels: 100,
  });
});

test("button in all states", async ({ page }) => {
  await page.goto("/components");

  const button = page.getByRole("button", { name: "Submit" });

  // 默认状态
  await expect(button).toHaveScreenshot("button-default.png");

  // 悬停状态
  await button.hover();
  await expect(button).toHaveScreenshot("button-hover.png");

  // 禁用状态
  await button.evaluate((el) => el.setAttribute("disabled", "true"));
  await expect(button).toHaveScreenshot("button-disabled.png");
});
```

### 模式 2：分片并行测试

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: "shard-1",
      use: { ...devices["Desktop Chrome"] },
      grepInvert: /@slow/,
      shard: { current: 1, total: 4 },
    },
    {
      name: "shard-2",
      use: { ...devices["Desktop Chrome"] },
      shard: { current: 2, total: 4 },
    },
    // ... 更多分片
  ],
});

// 在 CI 中运行
// npx playwright test --shard=1/4
// npx playwright test --shard=2/4
```

### 模式 3：无障碍访问测试

```typescript
// 安装：npm install @axe-core/playwright
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("page should not have accessibility violations", async ({ page }) => {
  await page.goto("/");

  const accessibilityScanResults = await new AxeBuilder({ page })
    .exclude("#third-party-widget")
    .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});

test("form is accessible", async ({ page }) => {
  await page.goto("/signup");

  const results = await new AxeBuilder({ page }).include("form").analyze();

  expect(results.violations).toEqual([]);
});
```

## 最佳实践

1. **使用数据属性**：`data-testid` 或 `data-cy` 作为稳定选择器
2. **避免脆弱选择器**：不要依赖 CSS 类或 DOM 结构
3. **测试用户行为**：点击、输入、查看 — 而非实现细节
4. **保持测试独立**：每个测试应独立运行
5. **清理测试数据**：在每个测试中创建和销毁测试数据
6. **使用页面对象**：封装页面逻辑
7. **有意义的断言**：检查实际用户可见的行为
8. **优化速度**：尽可能模拟，并行执行

```typescript
// ❌ 不好的选择器
cy.get(".btn.btn-primary.submit-button").click();
cy.get("div > form > div:nth-child(2) > input").type("text");

// ✅ 好的选择器
cy.getByRole("button", { name: "Submit" }).click();
cy.getByLabel("Email address").type("user@example.com");
cy.get('[data-testid="email-input"]').type("user@example.com");
```

## 常见陷阱

- **不稳定测试**：使用适当的等待，而非固定超时
- **慢速测试**：模拟外部 API，使用并行执行
- **过度测试**：不要用 E2E 测试每个边缘情况
- **耦合测试**：测试不应相互依赖
- **糟糕的选择器**：避免 CSS 类和 nth-child
- **无清理**：每个测试后清理测试数据
- **测试实现**：测试用户行为，而非内部实现

## 调试失败的测试

```typescript
// Playwright 调试
// 1. 以有头模式运行
npx playwright test --headed

// 2. 以调试模式运行
npx playwright test --debug

// 3. 使用追踪查看器
await page.screenshot({ path: 'screenshot.png' });
await page.video()?.saveAs('video.webm');

// 4. 添加 test.step 以获得更好的报告
test('checkout flow', async ({ page }) => {
    await test.step('Add item to cart', async () => {
        await page.goto('/products');
        await page.getByRole('button', { name: 'Add to Cart' }).click();
    });

    await test.step('Proceed to checkout', async () => {
        await page.goto('/cart');
        await page.getByRole('button', { name: 'Checkout' }).click();
    });
});

// 5. 检查页面状态
await page.pause();  // 暂停执行，打开检查器
```
