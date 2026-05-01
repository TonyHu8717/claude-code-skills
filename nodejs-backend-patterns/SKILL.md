---
name: nodejs-backend-patterns
description: 使用 Express/Fastify 构建生产就绪的 Node.js 后端服务，实现中间件模式、错误处理、身份验证、数据库集成和 API 设计最佳实践。在创建 Node.js 服务器、REST API、GraphQL 后端或微服务架构时使用。
---

# Node.js 后端模式

使用现代框架、架构模式和最佳实践构建可扩展、可维护和生产就绪的 Node.js 后端应用的综合指导。

## 何时使用此技能

- 构建 REST API 或 GraphQL 服务器
- 使用 Node.js 创建微服务
- 实现身份验证和授权
- 设计可扩展的后端架构
- 设置中间件和错误处理
- 集成数据库（SQL 和 NoSQL）
- 使用 WebSockets 构建实时应用
- 实现后台任务处理

## 核心框架

### Express.js - 极简框架

**基本设置：**

```typescript
import express, { Request, Response, NextFunction } from "express";
import helmet from "helmet";
import cors from "cors";
import compression from "compression";

const app = express();

// 安全中间件
app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(",") }));
app.use(compression());

// 请求体解析
app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true, limit: "10mb" }));

// 请求日志
app.use((req: Request, res: Response, next: NextFunction) => {
  console.log(`${req.method} ${req.path}`);
  next();
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Fastify - 高性能框架

**基本设置：**

```typescript
import Fastify from "fastify";
import helmet from "@fastify/helmet";
import cors from "@fastify/cors";
import compress from "@fastify/compress";

const fastify = Fastify({
  logger: {
    level: process.env.LOG_LEVEL || "info",
    transport: {
      target: "pino-pretty",
      options: { colorize: true },
    },
  },
});

// 插件
await fastify.register(helmet);
await fastify.register(cors, { origin: true });
await fastify.register(compress);

// 带模式验证的类型安全路由
fastify.post<{
  Body: { name: string; email: string };
  Reply: { id: string; name: string };
}>(
  "/users",
  {
    schema: {
      body: {
        type: "object",
        required: ["name", "email"],
        properties: {
          name: { type: "string", minLength: 1 },
          email: { type: "string", format: "email" },
        },
      },
    },
  },
  async (request, reply) => {
    const { name, email } = request.body;
    return { id: "123", name };
  },
);

await fastify.listen({ port: 3000, host: "0.0.0.0" });
```

## 架构模式

### 模式 1：分层架构

**结构：**

```
src/
├── controllers/     # 处理 HTTP 请求/响应
├── services/        # 业务逻辑
├── repositories/    # 数据访问层
├── models/          # 数据模型
├── middleware/      # Express/Fastify 中间件
├── routes/          # 路由定义
├── utils/           # 辅助函数
├── config/          # 配置
└── types/           # TypeScript 类型
```

**控制器层：**

```typescript
// controllers/user.controller.ts
import { Request, Response, NextFunction } from "express";
import { UserService } from "../services/user.service";
import { CreateUserDTO, UpdateUserDTO } from "../types/user.types";

export class UserController {
  constructor(private userService: UserService) {}

  async createUser(req: Request, res: Response, next: NextFunction) {
    try {
      const userData: CreateUserDTO = req.body;
      const user = await this.userService.createUser(userData);
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  }

  async getUser(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const user = await this.userService.getUserById(id);
      res.json(user);
    } catch (error) {
      next(error);
    }
  }

  async updateUser(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const updates: UpdateUserDTO = req.body;
      const user = await this.userService.updateUser(id, updates);
      res.json(user);
    } catch (error) {
      next(error);
    }
  }

  async deleteUser(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      await this.userService.deleteUser(id);
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}
```

**服务层：**

```typescript
// services/user.service.ts
import { UserRepository } from "../repositories/user.repository";
import { CreateUserDTO, UpdateUserDTO, User } from "../types/user.types";
import { NotFoundError, ValidationError } from "../utils/errors";
import bcrypt from "bcrypt";

export class UserService {
  constructor(private userRepository: UserRepository) {}

  async createUser(userData: CreateUserDTO): Promise<User> {
    // 验证
    const existingUser = await this.userRepository.findByEmail(userData.email);
    if (existingUser) {
      throw new ValidationError("Email already exists");
    }

    // 哈希密码
    const hashedPassword = await bcrypt.hash(userData.password, 10);

    // 创建用户
    const user = await this.userRepository.create({
      ...userData,
      password: hashedPassword,
    });

    // 从响应中移除密码
    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword as User;
  }

  async getUserById(id: string): Promise<User> {
    const user = await this.userRepository.findById(id);
    if (!user) {
      throw new NotFoundError("User not found");
    }
    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword as User;
  }

  async updateUser(id: string, updates: UpdateUserDTO): Promise<User> {
    const user = await this.userRepository.update(id, updates);
    if (!user) {
      throw new NotFoundError("User not found");
    }
    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword as User;
  }

  async deleteUser(id: string): Promise<void> {
    const deleted = await this.userRepository.delete(id);
    if (!deleted) {
      throw new NotFoundError("User not found");
    }
  }
}
```

**仓库层：**

```typescript
// repositories/user.repository.ts
import { Pool } from "pg";
import { CreateUserDTO, UpdateUserDTO, UserEntity } from "../types/user.types";

export class UserRepository {
  constructor(private db: Pool) {}

  async create(
    userData: CreateUserDTO & { password: string },
  ): Promise<UserEntity> {
    const query = `
      INSERT INTO users (name, email, password)
      VALUES ($1, $2, $3)
      RETURNING id, name, email, password, created_at, updated_at
    `;
    const { rows } = await this.db.query(query, [
      userData.name,
      userData.email,
      userData.password,
    ]);
    return rows[0];
  }

  async findById(id: string): Promise<UserEntity | null> {
    const query = "SELECT * FROM users WHERE id = $1";
    const { rows } = await this.db.query(query, [id]);
    return rows[0] || null;
  }

  async findByEmail(email: string): Promise<UserEntity | null> {
    const query = "SELECT * FROM users WHERE email = $1";
    const { rows } = await this.db.query(query, [email]);
    return rows[0] || null;
  }

  async update(id: string, updates: UpdateUserDTO): Promise<UserEntity | null> {
    const fields = Object.keys(updates);
    const values = Object.values(updates);

    const setClause = fields
      .map((field, idx) => `${field} = $${idx + 2}`)
      .join(", ");

    const query = `
      UPDATE users
      SET ${setClause}, updated_at = CURRENT_TIMESTAMP
      WHERE id = $1
      RETURNING *
    `;

    const { rows } = await this.db.query(query, [id, ...values]);
    return rows[0] || null;
  }

  async delete(id: string): Promise<boolean> {
    const query = "DELETE FROM users WHERE id = $1";
    const { rowCount } = await this.db.query(query, [id]);
    return rowCount > 0;
  }
}
```

### 模式 2：依赖注入

使用 DI 容器连接仓库、服务和控制器。完整的容器实现请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。

## 中间件模式

### 身份验证中间件

```typescript
// middleware/auth.middleware.ts
import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { UnauthorizedError } from "../utils/errors";

interface JWTPayload {
  userId: string;
  email: string;
}

declare global {
  namespace Express {
    interface Request {
      user?: JWTPayload;
    }
  }
}

export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  try {
    const token = req.headers.authorization?.replace("Bearer ", "");

    if (!token) {
      throw new UnauthorizedError("No token provided");
    }

    const payload = jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload;

    req.user = payload;
    next();
  } catch (error) {
    next(new UnauthorizedError("Invalid token"));
  }
};

export const authorize = (...roles: string[]) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return next(new UnauthorizedError("Not authenticated"));
    }

    // 检查用户是否有所需角色
    const hasRole = roles.some((role) => req.user?.roles?.includes(role));

    if (!hasRole) {
      return next(new UnauthorizedError("Insufficient permissions"));
    }

    next();
  };
};
```

### 验证中间件

```typescript
// middleware/validation.middleware.ts
import { Request, Response, NextFunction } from "express";
import { AnyZodObject, ZodError } from "zod";
import { ValidationError } from "../utils/errors";

export const validate = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map((err) => ({
          field: err.path.join("."),
          message: err.message,
        }));
        next(new ValidationError("Validation failed", errors));
      } else {
        next(error);
      }
    }
  };
};

// 使用 Zod
import { z } from "zod";

const createUserSchema = z.object({
  body: z.object({
    name: z.string().min(1),
    email: z.string().email(),
    password: z.string().min(8),
  }),
});

router.post("/users", validate(createUserSchema), userController.createUser);
```

### 速率限制中间件

```typescript
// middleware/rate-limit.middleware.ts
import rateLimit from "express-rate-limit";
import RedisStore from "rate-limit-redis";
import Redis from "ioredis";

const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: parseInt(process.env.REDIS_PORT || "6379"),
});

export const apiLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: "rl:",
  }),
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 每个 IP 每 windowMs 限制 100 次请求
  message: "Too many requests from this IP, please try again later",
  standardHeaders: true,
  legacyHeaders: false,
});

export const authLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: "rl:auth:",
  }),
  windowMs: 15 * 60 * 1000,
  max: 5, // 对认证端点使用更严格的限制
  skipSuccessfulRequests: true,
});
```

### 请求日志中间件

```typescript
// middleware/logger.middleware.ts
import { Request, Response, NextFunction } from "express";
import pino from "pino";

const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  transport: {
    target: "pino-pretty",
    options: { colorize: true },
  },
});

export const requestLogger = (
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  const start = Date.now();

  // 完成时记录响应
  res.on("finish", () => {
    const duration = Date.now() - start;
    logger.info({
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration: `${duration}ms`,
      userAgent: req.headers["user-agent"],
      ip: req.ip,
    });
  });

  next();
};

export { logger };
```

## 错误处理

### 自定义错误类

```typescript
// utils/errors.ts
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true,
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(
    message: string,
    public errors?: any[],
  ) {
    super(message, 400);
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = "Resource not found") {
    super(message, 404);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = "Unauthorized") {
    super(message, 401);
  }
}

export class ForbiddenError extends AppError {
  constructor(message: string = "Forbidden") {
    super(message, 403);
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 409);
  }
}
```

### 全局错误处理器

```typescript
// middleware/error-handler.ts
import { Request, Response, NextFunction } from "express";
import { AppError } from "../utils/errors";
import { logger } from "./logger.middleware";

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      status: "error",
      message: err.message,
      ...(err instanceof ValidationError && { errors: err.errors }),
    });
  }

  // 记录意外错误
  logger.error({
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
  });

  // 在生产环境中不泄露错误详情
  const message =
    process.env.NODE_ENV === "production"
      ? "Internal server error"
      : err.message;

  res.status(500).json({
    status: "error",
    message,
  });
};

// 异步错误包装器
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>,
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
```

## 数据库模式

Node.js 支持 SQL 和 NoSQL 数据库。所有生产数据库都使用连接池。

关键模式详见 [references/advanced-patterns.md](references/advanced-patterns.md)：
- **带连接池的 PostgreSQL** — `pg` Pool 配置和优雅关闭
- **带 Mongoose 的 MongoDB** — 连接管理和模式定义
- **事务模式** — 使用 `pg` 客户端的 `BEGIN`/`COMMIT`/`ROLLBACK`

## 身份验证和授权

基于 JWT 的认证，使用访问令牌（短期，15 分钟）和刷新令牌（7 天）。完整的 `AuthService` 实现，包含 `bcrypt` 密码比较，请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。

## 缓存策略

Redis 支持的 `CacheService`，包含 get/set/delete/invalidatePattern，以及用于方法级缓存的 `@Cacheable` 装饰器。请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。

## API 响应格式

标准化的 `ApiResponse` 辅助工具，包含 `success`、`error` 和 `paginated` 静态方法。请参见 [references/advanced-patterns.md](references/advanced-patterns.md)。

## 最佳实践

1. **使用 TypeScript**：类型安全防止运行时错误
2. **实现正确的错误处理**：使用自定义错误类
3. **验证输入**：使用 Zod 或 Joi 等库
4. **使用环境变量**：永远不要硬编码密钥
5. **实现日志记录**：使用结构化日志（Pino、Winston）
6. **添加速率限制**：防止滥用
7. **使用 HTTPS**：在生产环境中始终使用
8. **正确实现 CORS**：在生产环境中不要使用 `*`
9. **使用依赖注入**：更容易测试和维护
10. **编写测试**：单元测试、集成测试和 E2E 测试
11. **处理优雅关闭**：清理资源
12. **使用连接池**：用于数据库
13. **实现健康检查**：用于监控
14. **使用压缩**：减少响应大小
15. **监控性能**：使用 APM 工具

## 测试模式

综合测试指导请参见 `javascript-testing-patterns` 技能。
