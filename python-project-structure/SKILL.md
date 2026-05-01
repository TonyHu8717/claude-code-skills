---
name: python-project-structure
description: Python 项目组织、模块架构和公共 API 设计。在设置新项目、组织模块、使用 __all__ 定义公共接口或规划目录布局时使用。
---

# Python 项目结构与模块架构

设计组织良好的 Python 项目，具有清晰的模块边界、显式的公共接口和可维护的目录结构。良好的组织使代码可发现，变更可预测。

## 何时使用此技能

- 从头开始新的 Python 项目
- 重组现有代码库以提高清晰度
- 使用 `__all__` 定义模块公共 API
- 在扁平和嵌套目录结构之间选择
- 确定测试文件放置策略
- 创建可复用的库包

## 核心概念

### 1. 模块内聚性

将一起变更的相关代码分组。模块应该有单一、清晰的目的。

### 2. 显式接口

使用 `__all__` 定义公共内容。未列出的都是内部实现细节。

### 3. 扁平层次结构

优先使用浅目录结构。仅在真正的子域需要时才增加深度。

### 4. 一致的规范

在整个项目中统一应用命名和组织模式。

## 快速开始

```
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── services/
│       ├── models/
│       └── api/
├── tests/
├── pyproject.toml
└── README.md
```

## 基础模式

### 模式 1：每个文件一个概念

每个文件应专注于单一概念或紧密相关的函数集。在以下情况下考虑拆分文件：

- 处理多个不相关的职责
- 超过 300-500 行（因复杂性而异）
- 包含因不同原因而变更的类

```python
# Good: Focused files
# user_service.py - User business logic
# user_repository.py - User data access
# user_models.py - User data structures

# Avoid: Kitchen sink files
# user.py - Contains service, repository, models, utilities...
```

### 模式 2：使用 `__all__` 的显式公共 API

为每个模块定义公共接口。未列出的成员是内部实现细节。

```python
# mypackage/services/__init__.py
from .user_service import UserService
from .order_service import OrderService
from .exceptions import ServiceError, ValidationError

__all__ = [
    "UserService",
    "OrderService",
    "ServiceError",
    "ValidationError",
]

# Internal helpers remain private by omission
# from .internal_helpers import _validate_input  # Not exported
```

### 模式 3：扁平目录结构

优先使用最小嵌套。深层层次结构使导入冗长，导航困难。

```
# Preferred: Flat structure
project/
├── api/
│   ├── routes.py
│   └── middleware.py
├── services/
│   ├── user_service.py
│   └── order_service.py
├── models/
│   ├── user.py
│   └── order.py
└── utils/
    └── validation.py

# Avoid: Deep nesting
project/core/internal/services/impl/user/
```

仅在有真正的子域需要隔离时才添加子包。

### 模式 4：测试文件组织

选择一种方法并在整个项目中一致应用。

**选项 A：共置测试**

```
src/
├── user_service.py
├── test_user_service.py
├── order_service.py
└── test_order_service.py
```

优势：测试与它们验证的代码相邻。容易看到覆盖差距。

**选项 B：并行测试目录**

```
src/
├── services/
│   ├── user_service.py
│   └── order_service.py
tests/
├── services/
│   ├── test_user_service.py
│   └── test_order_service.py
```

优势：生产代码和测试代码之间的清晰分离。适用于较大项目的标准。

## 高级模式

### 模式 5：包初始化

使用 `__init__.py` 为包使用者提供干净的公共接口。

```python
# mypackage/__init__.py
"""MyPackage - A library for doing useful things."""

from .core import MainClass, HelperClass
from .exceptions import PackageError, ConfigError
from .config import Settings

__all__ = [
    "MainClass",
    "HelperClass",
    "PackageError",
    "ConfigError",
    "Settings",
]

__version__ = "1.0.0"
```

使用者可以直接从包导入：

```python
from mypackage import MainClass, Settings
```

### 模式 6：分层架构

按架构层组织代码以实现清晰的关注点分离。

```
myapp/
├── api/           # HTTP handlers, request/response
│   ├── routes/
│   └── middleware/
├── services/      # Business logic
├── repositories/  # Data access
├── models/        # Domain entities
├── schemas/       # API schemas (Pydantic)
└── config/        # Configuration
```

每层应仅依赖其下层，永远不要向上依赖。

### 模式 7：领域驱动结构

对于复杂应用程序，按业务领域而非技术层组织。

```
ecommerce/
├── users/
│   ├── models.py
│   ├── services.py
│   ├── repository.py
│   └── api.py
├── orders/
│   ├── models.py
│   ├── services.py
│   ├── repository.py
│   └── api.py
└── shared/
    ├── database.py
    └── exceptions.py
```

## 文件和模块命名

### 规范

- 所有文件和模块名使用 `snake_case`：`user_repository.py`
- 避免模糊含义的缩写：`user_repository.py` 而不是 `usr_repo.py`
- 类名与文件名匹配：`UserService` 在 `user_service.py` 中

### 导入风格

使用绝对导入以提高清晰度和可靠性：

```python
# Preferred: Absolute imports
from myproject.services import UserService
from myproject.models import User

# Avoid: Relative imports
from ..services import UserService
from . import models
```

当模块被移动或重组时，相对导入可能会中断。

## 最佳实践总结

1. **保持文件专注** - 每个文件一个概念，在 300-500 行时考虑拆分（因复杂性而异）
2. **显式定义 `__all__`** - 使公共接口清晰
3. **优先使用扁平结构** - 仅在真正的子域时增加深度
4. **使用绝对导入** - 更可靠、更清晰
5. **保持一致** - 在整个项目中统一应用模式
6. **名称与内容匹配** - 文件名应描述其目的
7. **分离关注点** - 保持层清晰，依赖单向流动
8. **记录结构** - 包含解释组织的 README
