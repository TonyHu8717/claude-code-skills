---
name: openapi-spec-generation
description: 从代码生成和维护 OpenAPI 3.1 规范，支持设计优先规范和验证模式。在创建 API 文档、生成 SDK 或确保 API 合约合规时使用。
---

# OpenAPI 规范生成

创建、维护和验证 RESTful API 的 OpenAPI 3.1 规范的综合模式。

## 何时使用此技能

- 从头创建 API 文档
- 从现有代码生成 OpenAPI 规范
- 设计 API 合约（设计优先方法）
- 根据规范验证 API 实现
- 从规范生成客户端 SDK
- 设置 API 文档门户

## 核心概念

### 1. OpenAPI 3.1 结构

```yaml
openapi: 3.1.0
info:
  title: API Title
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
paths:
  /resources:
    get: ...
components:
  schemas: ...
  securitySchemes: ...
```

### 2. 设计方法

| 方法           | 描述                       | 最适合              |
| -------------- | -------------------------- | ------------------- |
| **设计优先**   | 在编写代码前编写规范       | 新 API、合约        |
| **代码优先**   | 从代码生成规范             | 现有 API            |
| **混合**       | 注释代码，生成规范         | 演进中的 API        |

## 模板

### 模板 1：完整 API 规范

```yaml
openapi: 3.1.0
info:
  title: User Management API
  description: |
    API for managing users and their profiles.

    ## Authentication
    All endpoints require Bearer token authentication.

    ## Rate Limiting
    - 1000 requests per minute for standard tier
    - 10000 requests per minute for enterprise tier
  version: 2.0.0
  contact:
    name: API Support
    email: api-support@example.com
    url: https://docs.example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.example.com/v2
    description: Production
  - url: https://staging-api.example.com/v2
    description: Staging
  - url: http://localhost:3000/v2
    description: Local development

tags:
  - name: Users
    description: User management operations
  - name: Profiles
    description: User profile operations
  - name: Admin
    description: Administrative operations

paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      description: Returns a paginated list of users with optional filtering.
      tags:
        - Users
      parameters:
        - $ref: "#/components/parameters/PageParam"
        - $ref: "#/components/parameters/LimitParam"
        - name: status
          in: query
          description: Filter by user status
          schema:
            $ref: "#/components/schemas/UserStatus"
        - name: search
          in: query
          description: Search by name or email
          schema:
            type: string
            minLength: 2
            maxLength: 100
      responses:
        "200":
          description: Successful response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserListResponse"
              examples:
                default:
                  $ref: "#/components/examples/UserListExample"
        "400":
          $ref: "#/components/responses/BadRequest"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "429":
          $ref: "#/components/responses/RateLimited"
      security:
        - bearerAuth: []

    post:
      operationId: createUser
      summary: Create a new user
      description: Creates a new user account and sends welcome email.
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUserRequest"
            examples:
              standard:
                summary: Standard user
                value:
                  email: user@example.com
                  name: John Doe
                  role: user
              admin:
                summary: Admin user
                value:
                  email: admin@example.com
                  name: Admin User
                  role: admin
      responses:
        "201":
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
          headers:
            Location:
              description: URL of created user
              schema:
                type: string
                format: uri
        "400":
          $ref: "#/components/responses/BadRequest"
        "409":
          description: Email already exists
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
      security:
        - bearerAuth: []

  /users/{userId}:
    parameters:
      - $ref: "#/components/parameters/UserIdParam"

    get:
      operationId: getUser
      summary: Get user by ID
      tags:
        - Users
      responses:
        "200":
          description: Successful response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "404":
          $ref: "#/components/responses/NotFound"
      security:
        - bearerAuth: []

    patch:
      operationId: updateUser
      summary: Update user
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UpdateUserRequest"
      responses:
        "200":
          description: User updated
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "400":
          $ref: "#/components/responses/BadRequest"
        "404":
          $ref: "#/components/responses/NotFound"
      security:
        - bearerAuth: []

    delete:
      operationId: deleteUser
      summary: Delete user
      tags:
        - Users
        - Admin
      responses:
        "204":
          description: User deleted
        "404":
          $ref: "#/components/responses/NotFound"
      security:
        - bearerAuth: []
        - apiKey: []

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - name
        - status
        - createdAt
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
          description: Unique user identifier
        email:
          type: string
          format: email
          description: User email address
        name:
          type: string
          minLength: 1
          maxLength: 100
          description: User display name
        status:
          $ref: "#/components/schemas/UserStatus"
        role:
          type: string
          enum: [user, moderator, admin]
          default: user
        avatar:
          type: string
          format: uri
          nullable: true
        metadata:
          type: object
          additionalProperties: true
          description: Custom metadata
        createdAt:
          type: string
          format: date-time
          readOnly: true
        updatedAt:
          type: string
          format: date-time
          readOnly: true

    UserStatus:
      type: string
      enum: [active, inactive, suspended, pending]
      description: User account status

    CreateUserRequest:
      type: object
      required:
        - email
        - name
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100
        role:
          type: string
          enum: [user, moderator, admin]
          default: user
        metadata:
          type: object
          additionalProperties: true

    UpdateUserRequest:
      type: object
      minProperties: 1
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 100
        status:
          $ref: "#/components/schemas/UserStatus"
        role:
          type: string
          enum: [user, moderator, admin]
        metadata:
          type: object
          additionalProperties: true

    UserListResponse:
      type: object
      required:
        - data
        - pagination
      properties:
        data:
          type: array
          items:
            $ref: "#/components/schemas/User"
        pagination:
          $ref: "#/components/schemas/Pagination"

    Pagination:
      type: object
      required:
        - page
        - limit
        - total
        - totalPages
      properties:
        page:
          type: integer
          minimum: 1
        limit:
          type: integer
          minimum: 1
          maximum: 100
        total:
          type: integer
          minimum: 0
        totalPages:
          type: integer
          minimum: 0
        hasNext:
          type: boolean
        hasPrev:
          type: boolean

    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: string
          description: Error code for programmatic handling
        message:
          type: string
          description: Human-readable error message
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
        requestId:
          type: string
          description: Request ID for support

  parameters:
    UserIdParam:
      name: userId
      in: path
      required: true
      description: User ID
      schema:
        type: string
        format: uuid

    PageParam:
      name: page
      in: query
      description: Page number (1-based)
      schema:
        type: integer
        minimum: 1
        default: 1

    LimitParam:
      name: limit
      in: query
      description: Items per page
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

  responses:
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
          example:
            code: VALIDATION_ERROR
            message: Invalid request parameters
            details:
              - field: email
                message: Must be a valid email address

    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
          example:
            code: UNAUTHORIZED
            message: Authentication required

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
          example:
            code: NOT_FOUND
            message: User not found

    RateLimited:
      description: Too many requests
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
      headers:
        Retry-After:
          description: Seconds until rate limit resets
          schema:
            type: integer
        X-RateLimit-Limit:
          description: Request limit per window
          schema:
            type: integer
        X-RateLimit-Remaining:
          description: Remaining requests in window
          schema:
            type: integer

  examples:
    UserListExample:
      value:
        data:
          - id: "550e8400-e29b-41d4-a716-446655440000"
            email: "john@example.com"
            name: "John Doe"
            status: "active"
            role: "user"
            createdAt: "2024-01-15T10:30:00Z"
        pagination:
          page: 1
          limit: 20
          total: 1
          totalPages: 1
          hasNext: false
          hasPrev: false

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT token from /auth/login

    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for service-to-service calls

security:
  - bearerAuth: []
```

高级代码优先生成模式和工具请参见 [references/code-first-and-tooling.md](references/code-first-and-tooling.md)：

- **模板 2：Python/FastAPI** — 带 `Field` 验证的 Pydantic 模型、枚举类型、带 `response_model` 和 `status_code` 的完整 CRUD 端点、导出规范为 JSON
- **模板 3：TypeScript/tsoa** — 基于装饰器的控制器（`@Route`、`@Get`、`@Security`、`@Example`、`@Response`），从 TypeScript 类型生成 OpenAPI
- **模板 4：验证和 Lint** — Spectral 规则集（`.spectral.yaml`），包含 operationId、安全、命名约定的自定义规则；Redocly 配置，包含 MIME 类型强制和代码示例生成
- **SDK 生成** — `openapi-generator-cli` 用于 TypeScript（fetch）、Python 和 Go 客户端

## 最佳实践

### 推荐做法

- **使用 $ref** - 重用模式、参数、响应
- **添加示例** - 真实世界的值帮助消费者
- **记录错误** - 所有可能的错误代码
- **为 API 版本化** - 在 URL 或头部中
- **使用语义化版本控制** - 用于规范更改

### 避免做法

- **不要使用通用描述** - 要具体
- **不要跳过安全** - 定义所有方案
- **不要忘记 nullable** - 显式关于 null
- **不要混合风格** - 全程一致的命名
- **不要硬编码 URL** - 使用服务器变量
